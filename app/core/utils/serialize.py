"""Coerce API payloads to JSON-serializable Python types."""

from __future__ import annotations

import math
from typing import Any, Iterable


def safe_float(value: Any, default: float = 0.0) -> float:
    if value is None:
        return default
    try:
        number = float(value)
    except (TypeError, ValueError):
        return default
    if not math.isfinite(number):
        return default
    return number


def equity_points(rows: Iterable) -> list[dict[str, Any]]:
    points: list[dict[str, Any]] = []
    for row in rows:
        if row[0] is None or row[1] is None:
            continue
        points.append(
            {
                "timestamp": str(row[0]),
                "equity": safe_float(row[1]),
            }
        )
    return points


def leaderboard_rows(
    rows: Iterable,
    explain_fn,
) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for row in rows:
        sharpe = safe_float(row[1])
        ret = safe_float(row[2])
        ml_score = safe_float(row[3])
        items.append(
            {
                "symbol": str(row[0]) if row[0] is not None else "",
                "sharpe": sharpe,
                "return": ret,
                "ml_score": ml_score,
                "explanation": explain_fn(
                    {
                        "return": ret,
                        "sharpe": sharpe,
                        "drawdown": 0,
                    }
                ),
            }
        )
    return items


def ranking_records(df) -> list[dict[str, Any]]:
    return [
        {
            "symbol": str(row["symbol"]),
            "score": round(safe_float(row["score"]), 4),
        }
        for _, row in df.iterrows()
    ]


def sanitize_forecast(forecast: dict[str, Any] | None) -> dict[str, Any]:
    """Ensure LSTM forecast dict is JSON-safe."""
    if not forecast:
        return {
            "horizon": "1d",
            "available": False,
            "trend": "neutral",
            "confidence_pct": 0.0,
            "predicted_return_pct": 0.0,
            "predicted_price": None,
            "last_close": None,
            "model_loaded": False,
            "method": "unavailable",
        }

    return {
        "horizon": str(forecast.get("horizon", "1d")),
        "available": bool(forecast.get("available")),
        "trend": str(forecast.get("trend", "neutral")),
        "confidence_pct": round(safe_float(forecast.get("confidence_pct")), 1),
        "predicted_return": round(safe_float(forecast.get("predicted_return")), 6),
        "predicted_return_pct": round(
            safe_float(forecast.get("predicted_return_pct")), 3
        ),
        "predicted_price": (
            round(safe_float(forecast["predicted_price"]), 4)
            if forecast.get("predicted_price") is not None
            else None
        ),
        "last_close": (
            round(safe_float(forecast["last_close"]), 4)
            if forecast.get("last_close") is not None
            else None
        ),
        "model_loaded": bool(forecast.get("model_loaded")),
        "method": str(forecast.get("method", "unknown")),
        "error": forecast.get("error"),
    }


def sanitize_performer(row: dict | None) -> dict[str, Any] | None:
    if not row or not isinstance(row, dict):
        return None
    return {
        "symbol": str(row.get("symbol", "")),
        "return_pct": round(safe_float(row.get("return_pct")), 2),
        "score": round(safe_float(row.get("score")), 4),
    }


def sanitize_portfolio_analytics(analytics: dict | None) -> dict[str, Any]:
    if not analytics or not isinstance(analytics, dict):
        return {
            "sharpe_ratio": 0.0,
            "volatility_pct": 0.0,
            "period": "1mo",
            "benchmark": {
                "label": "NIFTY50",
                "ticker": "^NSEI",
                "return_pct": 0.0,
                "excess_return_pct": 0.0,
            },
            "best_performer": None,
            "worst_performer": None,
        }

    benchmark = analytics.get("benchmark") or {}
    return {
        "sharpe_ratio": round(safe_float(analytics.get("sharpe_ratio")), 3),
        "volatility_pct": round(safe_float(analytics.get("volatility_pct")), 2),
        "period": str(analytics.get("period", "1mo")),
        "benchmark": {
            "label": str(benchmark.get("label", "NIFTY50")),
            "ticker": str(benchmark.get("ticker", "^NSEI")),
            "return_pct": round(safe_float(benchmark.get("return_pct")), 2),
            "excess_return_pct": round(
                safe_float(benchmark.get("excess_return_pct")), 2
            ),
        },
        "best_performer": sanitize_performer(analytics.get("best_performer")),
        "worst_performer": sanitize_performer(analytics.get("worst_performer")),
    }


def sanitize_stock_records(stocks: list | None) -> list[dict[str, Any]]:
    cleaned: list[dict[str, Any]] = []
    for stock in stocks or []:
        if not isinstance(stock, dict):
            continue
        cleaned.append(
            {
                "symbol": str(stock.get("symbol", "")),
                "score": round(safe_float(stock.get("score")), 4),
                "return_pct": round(safe_float(stock.get("return_pct")), 2),
            }
        )
    return cleaned
