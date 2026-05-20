"""
Precompute lightweight cache files for Render free-tier stability.

This script avoids repeated ML inference on every API request by generating:
- data_cache/rankings.json
- data_cache/portfolio.json
"""

from __future__ import annotations

import json
from pathlib import Path

from app.core.utils.serialize import (
    safe_float,
    sanitize_portfolio_analytics,
    sanitize_stock_records,
)
from app.ml.portfolio_backtest import rank_stocks, simulate_portfolio

CACHE_DIR = Path("data_cache")
RANKINGS_CACHE_PATH = CACHE_DIR / "rankings.json"
PORTFOLIO_CACHE_PATH = CACHE_DIR / "portfolio.json"


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=True), encoding="utf-8")


def main() -> None:
    # Render free-tier optimization:
    # precompute ranking/portfolio once, then serve cached JSON near-instantly.
    ranking_df = rank_stocks()
    ranking_results = [
        {"symbol": str(row["symbol"]), "score": round(float(row["score"]), 4)}
        for _, row in ranking_df.iterrows()
    ]

    portfolio_raw = simulate_portfolio(top_k=10)
    selected = sanitize_stock_records(portfolio_raw.get("selected_stocks", []))
    portfolio_payload = {
        "status": "success",
        "portfolio_size": len(selected),
        "portfolio_return": safe_float(portfolio_raw.get("portfolio_return", 0)),
        "selected_stocks": selected,
        "analytics": sanitize_portfolio_analytics(portfolio_raw.get("analytics")),
    }

    rankings_payload = {
        "status": "success",
        "top_k": len(ranking_results),
        "results": ranking_results,
    }

    _write_json(RANKINGS_CACHE_PATH, rankings_payload)
    _write_json(PORTFOLIO_CACHE_PATH, portfolio_payload)

    print(f"Cache generated: {RANKINGS_CACHE_PATH} and {PORTFOLIO_CACHE_PATH}")


if __name__ == "__main__":
    main()
