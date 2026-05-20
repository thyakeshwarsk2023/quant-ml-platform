from sqlalchemy import text
import logging
import pandas as pd
import yfinance as yf

from app.core.strategy.rsi import RSIStrategy
from app.core.strategy.moving_average import MovingAverageStrategy
from app.core.strategy.combined_strategy import CombinedStrategy

from app.core.backtest.engine import BacktestEngine
from app.core.data.loader import load_data
from app.core.portfolio.portfolio import Portfolio

from app.ml.ranker import predict_score
from app.ml.features import add_all_features

logger = logging.getLogger(__name__)


# =========================
# 🔥 STRATEGY SELECTOR
# =========================
def get_strategy(
    name,
    data,
    params=None
):

    params = params or {}

    if name == "rsi":

        return RSIStrategy(
            data,
            **params
        )

    elif name == "ma":

        return MovingAverageStrategy(
            data,
            **params
        )

    elif name == "hybrid":

        return CombinedStrategy(
            data,
            **params
        )

    else:
        raise ValueError(
            f"Unknown strategy: {name}"
        )


# =========================
# 🔥 MARKET FEATURES (LIVE)
# =========================
def get_market_features(symbol):

    try:

        df = yf.download(
            symbol,
            period="3mo",
            interval="1d"
        )

        # =========================
        # FIX MULTIINDEX
        # =========================
        if isinstance(
            df.columns,
            pd.MultiIndex
        ):
            df.columns = (
                df.columns
                .get_level_values(0)
            )

        if df.empty:
            return {}

        # =========================
        # FEATURE ENGINEERING
        # =========================
        df = add_all_features(df)

        if df.empty:
            return {}

        latest = df.iloc[-1]

        return {

            # BASIC FEATURES
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

    except Exception as e:

        logger.warning(
            f"Market features failed "
            f"for {symbol}: {e}"
        )

        return {}


# =========================
# 🔥 SINGLE BACKTEST
# =========================
def run_backtest_sync(
    symbol: str,
    strategy_name="hybrid",
    strategy_params=None
):

    # =========================
    # LOAD DATA
    # =========================
    data = load_data(symbol)

    if data is None or data.empty:

        raise ValueError(
            f"No data for {symbol}"
        )

    # =========================
    # STRATEGY
    # =========================
    strategy = get_strategy(
        strategy_name,
        data,
        strategy_params or {}
    )

    # =========================
    # PORTFOLIO
    # =========================
    portfolio = Portfolio(100000)

    # =========================
    # ENGINE
    # =========================
    engine = BacktestEngine(
        data,
        strategy,
        portfolio
    )

    # =========================
    # RUN BACKTEST
    # =========================
    result = engine.run()

    # =========================
    # EXTRA DATA
    # =========================
    result["prices"] = (
        data["Close"]
        .tolist()
    )

    result["symbol"] = symbol

    result["strategy"] = strategy_name

    result["strategy_params"] = (
        strategy_params or {}
    )

    return result


# =========================
# 🔥 MULTI-STRATEGY (ML)
# =========================
def run_multi_strategy(symbol: str):

    # =========================
    # STRATEGY CONFIGS
    # =========================
    strategy_configs = [

        # RSI
        (
            "rsi",
            {"period": 7}
        ),

        (
            "rsi",
            {"period": 14}
        ),

        (
            "rsi",
            {"period": 21}
        ),

        # MOVING AVERAGE
        (
            "ma",
            {
                "short": 10,
                "long": 20
            }
        ),

        (
            "ma",
            {
                "short": 20,
                "long": 50
            }
        ),

        (
            "ma",
            {
                "short": 50,
                "long": 200
            }
        ),

        # HYBRID
        (
            "hybrid",
            {
                "short": 10,
                "long": 50,
                "rsi_period": 14
            }
        ),

        (
            "hybrid",
            {
                "short": 20,
                "long": 100,
                "rsi_period": 21
            }
        ),
    ]

    results = []

    # =========================
    # MARKET FEATURES
    # =========================
    market_features = (
        get_market_features(symbol)
    )

    # =========================
    # STRATEGY LOOP
    # =========================
    for strategy_name, params in strategy_configs:

        try:

            logger.info(
                f"Running "
                f"{strategy_name} "
                f"{params}"
            )

            # =========================
            # BACKTEST
            # =========================
            res = run_backtest_sync(
                symbol=symbol,
                strategy_name=strategy_name,
                strategy_params=params
            )

            # =========================
            # EXTRACT METRICS
            # =========================
            sharpe = float(
                res.get("sharpe", 0)
            )

            dd = float(
                res.get(
                    "max_drawdown",
                    0
                )
            )

            volatility = float(
                res.get(
                    "volatility",
                    0
                )
            )

            win_rate = float(
                res.get(
                    "win_rate",
                    0
                )
            )

            profit_factor = float(
                res.get(
                    "profit_factor",
                    0
                )
            )

            # =========================
            # ML INPUT
            # =========================
            ml_input = {

                # STRATEGY METRICS
                "sharpe":
                    sharpe,

                "max_drawdown":
                    dd,

                "risk_reward":
                    sharpe
                    / (dd + 0.001),

                "stability":
                    sharpe
                    / (volatility + 0.001),

                "consistency":
                    win_rate
                    * profit_factor,

                "win_quality":
                    win_rate
                    * sharpe,

                # MARKET FEATURES
                **market_features
            }

            # =========================
            # ML SCORE
            # =========================
            ml_score = predict_score(
                ml_input
            )

            res["ml_score"] = (
                float(ml_score)
            )

            results.append(res)

        except Exception as e:

            logger.warning(
                f"{symbol} "
                f"{strategy_name} "
                f"{params} failed: {e}"
            )

    # =========================
    # VALIDATION
    # =========================
    if not results:

        raise ValueError(
            f"No strategy worked "
            f"for {symbol}"
        )

    # =========================
    # BEST STRATEGY
    # =========================
    best = max(
        results,
        key=lambda x: x.get(
            "ml_score",
            0
        )
    )

    return best


# =========================
# 🔥 SYNC DB READ
# =========================
def get_equity(db, run_id: int):

    result = db.execute(text("""
        SELECT
            timestamp,
            equity
        FROM equity_curve
        WHERE run_id = :id
        ORDER BY timestamp
    """), {
        "id": run_id
    })

    rows = result.fetchall()

    return [

        {
            "timestamp": str(r[0]),
            "equity": float(r[1])
        }

        for r in rows
    ]