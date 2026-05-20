"""Lightweight portfolio risk/return metrics and benchmark helpers."""

from __future__ import annotations

import numpy as np
import pandas as pd
import yfinance as yf

BENCHMARK_TICKER = "^NSEI"
BENCHMARK_LABEL = "NIFTY50"
TRADING_DAYS = 252


def _flatten_close(df: pd.DataFrame) -> pd.Series:
    if df is None or df.empty:
        return pd.Series(dtype=float)

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    close = df["Close"]
    if isinstance(close, pd.DataFrame):
        close = close.iloc[:, 0]
    return pd.to_numeric(close, errors="coerce").dropna()


def annualized_sharpe(daily_returns: np.ndarray) -> float:
    r = np.asarray(daily_returns, dtype=float)
    r = r[np.isfinite(r)]
    if r.size < 2:
        return 0.0
    std = float(np.std(r, ddof=1))
    if std < 1e-12:
        return 0.0
    return float(np.mean(r) / std * np.sqrt(TRADING_DAYS))


def annualized_volatility_pct(daily_returns: np.ndarray) -> float:
    r = np.asarray(daily_returns, dtype=float)
    r = r[np.isfinite(r)]
    if r.size < 2:
        return 0.0
    return float(np.std(r, ddof=1) * np.sqrt(TRADING_DAYS) * 100)


def total_return_pct(daily_returns: np.ndarray) -> float:
    r = np.asarray(daily_returns, dtype=float)
    r = r[np.isfinite(r)]
    if r.size == 0:
        return 0.0
    compounded = float(np.prod(1.0 + r) - 1.0)
    return round(compounded * 100, 2)


def fetch_benchmark_daily_returns(period: str = "1mo") -> np.ndarray:
    try:
        df = yf.download(
            BENCHMARK_TICKER,
            period=period,
            interval="1d",
            progress=False,
            auto_adjust=True,
        )
        close = _flatten_close(df)
        if close.size < 2:
            return np.array([])
        return close.pct_change().dropna().to_numpy()
    except Exception:
        return np.array([])


def build_equal_weight_returns(
    price_series: dict[str, pd.Series],
) -> np.ndarray:
    if not price_series:
        return np.array([])

    returns_df = pd.DataFrame(
        {symbol: series.pct_change() for symbol, series in price_series.items()}
    )
    returns_df = returns_df.dropna(how="all")
    if returns_df.empty:
        return np.array([])

    port = returns_df.mean(axis=1).dropna()
    return port.to_numpy()


def summarize_performers(stock_results: list[dict]) -> tuple[dict | None, dict | None]:
    if not stock_results:
        return None, None

    ranked = sorted(
        stock_results,
        key=lambda s: float(s.get("return_pct", 0) or 0),
        reverse=True,
    )
    best = ranked[0]
    worst = ranked[-1]

    def _card(row: dict) -> dict:
        return {
            "symbol": str(row.get("symbol", "")),
            "return_pct": round(float(row.get("return_pct", 0) or 0), 2),
            "score": round(float(row.get("score", 0) or 0), 4),
        }

    return _card(best), _card(worst)


def compute_portfolio_analytics(
    price_series: dict[str, pd.Series],
    stock_results: list[dict],
    period: str = "1mo",
) -> dict:
    port_returns = build_equal_weight_returns(price_series)
    bench_returns = fetch_benchmark_daily_returns(period=period)

    port_return_compounded = total_return_pct(port_returns)
    bench_return_compounded = total_return_pct(bench_returns)

    best, worst = summarize_performers(stock_results)

    return {
        "sharpe_ratio": round(annualized_sharpe(port_returns), 3),
        "volatility_pct": round(annualized_volatility_pct(port_returns), 2),
        "period": period,
        "benchmark": {
            "label": BENCHMARK_LABEL,
            "ticker": BENCHMARK_TICKER,
            "return_pct": bench_return_compounded,
            "excess_return_pct": round(
                port_return_compounded - bench_return_compounded, 2
            ),
        },
        "best_performer": best,
        "worst_performer": worst,
    }
