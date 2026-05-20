import logging
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import yfinance as yf

from app.core.data.nifty50 import NIFTY_50
from app.core.portfolio.metrics import (
    _flatten_close,
    compute_portfolio_analytics,
)
from app.ml.features import add_all_features

logger = logging.getLogger(__name__)

MODEL_PATH = Path(__file__).resolve().parent / "lgbm_model.pkl"
_model = None
_price_cache: dict[tuple[str, str, str], pd.DataFrame] = {}


def get_ranking_model():
    """Lazy-load ML model so API can start even if weights are missing."""
    global _model
    if _model is not None:
        return _model
    if not MODEL_PATH.is_file():
        raise FileNotFoundError(f"Model file not found: {MODEL_PATH}")
    _model = joblib.load(MODEL_PATH)
    logger.info("Loaded ranking model from %s", MODEL_PATH)
    return _model


def _download_price_data(symbol: str, period: str, interval: str = "1d") -> pd.DataFrame | None:
    """Cached yfinance fetch to reduce duplicate network calls on free tier."""
    key = (symbol, period, interval)
    if key in _price_cache:
        return _price_cache[key]

    try:
        df = yf.download(
            symbol,
            period=period,
            interval=interval,
            progress=False,
        )
    except Exception as exc:
        logger.warning("Download failed for %s: %s", symbol, exc)
        _price_cache[key] = None
        return None

    if df is None or df.empty:
        _price_cache[key] = None
        return None

    # FIX MULTIINDEX
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    _price_cache[key] = df
    return df


# =========================
# FEATURES
# =========================
FEATURES = [

    # STRATEGY FEATURES
    "sharpe",
    "max_drawdown",
    "risk_reward",
    "win_quality",
    "stability",
    "consistency",

    # MARKET FEATURES
    "mkt_volatility",
    "momentum",
    "trend_strength",
    "volume_spike",

    # ADVANCED FEATURES
    "atr",
    "macd",
    "macd_signal",
    "bb_width"
]


# =========================
# LOAD STOCK DATA
# =========================
def load_stock_data(symbol):

    try:
        df = _download_price_data(
            symbol=symbol,
            period="2y",
            interval="1d",
        )

        if df is None or df.empty or len(df) < 100:
            return None

        # ADD FEATURES
        df = add_all_features(df)

        return df

    except Exception as e:

        logger.warning("Failed loading %s: %s", symbol, e)

        return None


# =========================
# BUILD FEATURE ROW
# =========================
def build_feature_row(df):

    latest = df.iloc[-1]

    returns = (
        df["Close"]
        .pct_change()
        .dropna()
    )

    sharpe = (
        returns.mean()
        /
        (returns.std() + 1e-9)
    )

    volatility = returns.std()

    max_drawdown = (
        (
            df["Close"]
            /
            df["Close"].cummax()
        ) - 1
    ).min()

    win_rate = (
        (returns > 0)
        .mean()
    )

    profit_factor = 1.0

    feature_row = {

        # STRATEGY FEATURES
        "sharpe":
            float(sharpe),

        "max_drawdown":
            abs(float(max_drawdown)),

        "risk_reward":
            float(
                sharpe /
                (
                    abs(max_drawdown)
                    + 0.001
                )
            ),

        "win_quality":
            float(
                win_rate
                * sharpe
            ),

        "stability":
            float(
                sharpe /
                (
                    volatility
                    + 0.001
                )
            ),

        "consistency":
            float(
                win_rate
                * profit_factor
            ),

        # MARKET FEATURES
        "mkt_volatility":
            float(
                latest.get(
                    "volatility",
                    0
                )
            ),

        "momentum":
            float(
                latest.get(
                    "momentum",
                    0
                )
            ),

        "trend_strength":
            float(
                latest.get(
                    "trend_strength",
                    0
                )
            ),

        "volume_spike":
            float(
                latest.get(
                    "volume_spike",
                    0
                )
            ),

        # ADVANCED FEATURES
        "atr":
            float(
                latest.get(
                    "atr",
                    0
                )
            ),

        "macd":
            float(
                latest.get(
                    "macd",
                    0
                )
            ),

        "macd_signal":
            float(
                latest.get(
                    "macd_signal",
                    0
                )
            ),

        "bb_width":
            float(
                latest.get(
                    "bb_width",
                    0
                )
            ),
    }

    return feature_row


# =========================
# RANK STOCKS
# =========================
def rank_stocks():

    rankings = []
    _price_cache.clear()

    # Render free-tier timeout optimization:
    # - compact NIFTY_50 subset
    # - cached downloads (avoid duplicate requests)
    # - skip failures immediately and continue
    for symbol in NIFTY_50:

        try:

            logger.debug("Ranking %s", symbol)

            df = load_stock_data(symbol)

            if df is None:
                continue

            features = build_feature_row(df)

            X = pd.DataFrame([features])

            X = X[FEATURES]

            score = float(
                get_ranking_model().predict(X)[0]
            )

            rankings.append({

                "symbol":
                    symbol,

                "score":
                    round(score, 4)
            })

        except Exception as e:

            logger.warning("Failed ranking %s: %s", symbol, e)

    ranking_df = pd.DataFrame(rankings)

    if ranking_df.empty:
        raise ValueError(
            "No rankings generated"
        )

    ranking_df = (
        ranking_df
        .sort_values(
            by="score",
            ascending=False
        )
        .reset_index(drop=True)
    )

    return ranking_df


# =========================
# SIMULATE PORTFOLIO
# =========================
def simulate_portfolio(
    top_k=10
):

    rankings = rank_stocks()

    top_stocks = rankings.head(top_k)

    logger.info("Top stocks selected: %s", len(top_stocks))

    allocation = 1 / top_k

    portfolio_returns = []

    stock_results = []

    price_series = {}

    for _, row in top_stocks.iterrows():

        symbol = row["symbol"]

        try:

            # Reuse cached 2Y series from ranking pass and derive recent 1M return.
            df = _download_price_data(
                symbol=symbol,
                period="2y",
                interval="1d",
            )
            if df is None:
                continue

            close_prices = _flatten_close(df)
            if len(close_prices) < 2:
                continue

            recent = close_prices.tail(22)
            if len(recent) < 2:
                continue

            price_series[symbol] = recent
            start_price = float(recent.iloc[0])
            end_price = float(recent.iloc[-1])
            if start_price <= 0:
                continue

            ret = (
                end_price
                /
                start_price
            ) - 1

            weighted_ret = (
                ret
                * allocation
            )

            if np.isfinite(weighted_ret):
                portfolio_returns.append(
                    float(weighted_ret)
                    )

            stock_results.append({

                "symbol":
                    symbol,

                "score":
                    round(float(row["score"]), 4),

                "return_pct":
                    round(ret * 100, 2)
            })

            logger.debug("%s return %.2f%%", symbol, ret * 100)

        except Exception as e:

            logger.warning("Portfolio sim failed for %s: %s", symbol, e)

    total_return = float(
        np.nansum(portfolio_returns)
    )

    analytics = compute_portfolio_analytics(
        price_series,
        stock_results,
        period="1mo",
    )

    logger.info(
        "Portfolio simulation complete: top_k=%s return=%.2f%%",
        top_k,
        total_return * 100,
    )

    return {

    "portfolio_return":
        float(
            round(
                total_return * 100,
                2
            )
        ),

    "selected_stocks":
        stock_results,

    "analytics":
        analytics,
        }


# =========================
# ENTRY
# =========================
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    result = simulate_portfolio(top_k=10)
    logger.info("Result: %s", result)