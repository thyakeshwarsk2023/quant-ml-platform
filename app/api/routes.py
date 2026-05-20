from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from sqlalchemy.orm import Session
from sqlalchemy import text

import json
import traceback
import logging
import threading
from pathlib import Path

from app.db.session import (
    get_db,
    SessionLocal
)
from app.core.config import settings

from app.services.backtest_service import (
    run_multi_strategy
)

from app.services.analytics_service import (
    get_stock_analytics
)

from app.services.forecast_service import (
    get_symbol_forecast
)

from app.core.utils.explainer import (
    explain_strategy
)

from app.core.utils.serialize import (
    equity_points,
    leaderboard_rows,
    safe_float,
    sanitize_portfolio_analytics,
    sanitize_stock_records,
)


# =========================
# 🚀 ROUTER
# =========================
router = APIRouter()

logger = logging.getLogger(__name__)

CACHE_DIR = Path("data_cache")
RANKINGS_CACHE_PATH = CACHE_DIR / "rankings.json"
PORTFOLIO_CACHE_PATH = CACHE_DIR / "portfolio.json"


def _load_json_cache(path: Path):
    """Load precomputed cache payload; return None if unavailable/corrupt."""
    try:
        if not path.exists():
            return None
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        logger.warning("Cache read failed for %s: %s", path, exc)
        return None


# =========================
# 🚀 IN-MEMORY JOB STORE
# =========================
scan_jobs = {}


# =========================
# 🚀 SCAN ENDPOINTS (STUB)
# =========================
@router.post("/scan/start")
def start_scan():
    return {
        "status": "error",
        "error": "Scanner feature not implemented yet"
    }


@router.get("/scan/status/{job_id}")
def get_scan_status(job_id: str):
    return {
        "status": "error",
        "error": "Scanner feature not implemented yet"
    }


@router.get("/scan/results/{job_id}")
def get_scan_results(job_id: str):
    return {
        "status": "error",
        "error": "Scanner feature not implemented yet"
    }


@router.get("/model/evaluate")
def model_evaluate():
    return {
        "status": "error",
        "error": "Model evaluation endpoint not implemented yet"
    }


# =========================
# 🚀 LSTM FORECAST
# =========================
@router.get("/forecast")
def stock_forecast(symbol: str, period: str = "6mo"):

    try:
        return get_symbol_forecast(symbol, period=period)

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e

    except Exception as e:
        logger.error(f"❌ FORECAST ERROR: {e}")
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail="Failed to generate forecast",
        ) from e


# =========================
# 🚀 STOCK ANALYTICS
# =========================
@router.get("/analytics")
def stock_analytics(symbol: str, period: str = "1y"):

    try:
        return get_stock_analytics(symbol, period=period)

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e

    except Exception as e:
        logger.error(f"❌ ANALYTICS ERROR: {e}")
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail="Failed to load stock analytics",
        ) from e


# =========================
# 🚀 RUN BACKTEST
# =========================
@router.get("/run-backtest")
def start_backtest(
    symbol: str,
    db: Session = Depends(get_db)
):

    result = db.execute(text("""
        INSERT INTO backtest_runs (

            symbol,
            initial_capital,
            status

        )
        VALUES (

            :symbol,
            100000,
            'running'

        )
        RETURNING id
    """), {

        "symbol": symbol
    })

    run_id = result.scalar()

    db.commit()

    # =========================
    # 🚀 BACKGROUND JOB
    # =========================
    def run_job():

        local_db = SessionLocal()

        try:

            logger.info(
                f"🚀 Running "
                f"{symbol}"
            )

            bt_result = run_multi_strategy(
                symbol
            )

            ret = float(
                bt_result.get(
                    "return",
                    0
                )
            )

            sharpe = float(
                bt_result.get(
                    "sharpe",
                    0
                )
            )

            dd = float(
                bt_result.get(
                    "max_drawdown",
                    0
                )
            )

            vol = float(
                bt_result.get(
                    "volatility",
                    0
                )
            )

            win_rate = float(
                bt_result.get(
                    "win_rate",
                    0
                )
            )

            pf = float(
                bt_result.get(
                    "profit_factor",
                    0
                )
            )

            ml_score = float(
                bt_result.get(
                    "ml_score",
                    0
                )
            )

            # =========================
            # 🚀 SAVE METRICS
            # =========================
            local_db.execute(text("""
                INSERT INTO metrics (

                    run_id,
                    return_pct,
                    sharpe,
                    max_drawdown,
                    volatility,
                    win_rate,
                    profit_factor,
                    ml_score

                )
                VALUES (

                    :id,
                    :ret,
                    :sharpe,
                    :dd,
                    :vol,
                    :wr,
                    :pf,
                    :ml
                )
            """), {

                "id": run_id,
                "ret": ret,
                "sharpe": sharpe,
                "dd": dd,
                "vol": vol,
                "wr": win_rate,
                "pf": pf,
                "ml": ml_score
            })

            # =========================
            # 🚀 EQUITY CURVE
            # =========================
            local_db.execute(text("""
                DELETE FROM equity_curve
                WHERE run_id=:id
            """), {

                "id": run_id
            })

            equity_rows = [

                {

                    "id": run_id,

                    "ts":
                        p["timestamp"],

                    "eq":
                        float(
                            p["equity"]
                        )
                }

                for p in bt_result.get(
                    "equity_curve",
                    []
                )
            ]

            if equity_rows:

                local_db.execute(text("""
                    INSERT INTO equity_curve (

                        run_id,
                        timestamp,
                        equity

                    )
                    VALUES (

                        :id,
                        :ts,
                        :eq
                    )
                """), equity_rows)

            # =========================
            # 🚀 COMPLETE
            # =========================
            local_db.execute(text("""
                UPDATE backtest_runs
                SET status='completed'
                WHERE id=:id
            """), {

                "id": run_id
            })

            local_db.commit()

            logger.info(
                f"✅ Completed "
                f"{symbol}"
            )

        except Exception as e:

            logger.error(
                f"❌ Failed "
                f"{symbol}: {e}"
            )

            traceback.print_exc()

            local_db.rollback()

            local_db.execute(text("""
                UPDATE backtest_runs
                SET status='failed'
                WHERE id=:id
            """), {

                "id": run_id
            })

            local_db.commit()

        finally:

            local_db.close()

    threading.Thread(
        target=run_job,
        daemon=True
    ).start()

    return {

        "status":
            "started",

        "run_id":
            int(run_id) if run_id is not None else None
    }


# =========================
# 🚀 EQUITY CURVE
# =========================
@router.get("/equity/{run_id}")
def equity(
    run_id: int,
    db: Session = Depends(get_db)
):

    try:

        result = db.execute(text("""
            SELECT timestamp, equity
            FROM equity_curve
            WHERE run_id = :id
            ORDER BY timestamp
        """), {

            "id": run_id
        })

        rows = result.fetchall()

        return equity_points(rows)

    except Exception as e:

        logger.error(
            f"❌ EQUITY ERROR: {e}"
        )

        return []


# =========================
# 🚀 LEADERBOARD
# =========================
@router.get("/leaderboard")
def leaderboard(
    db: Session = Depends(get_db)
):
    # Optional free-tier safeguard: skip expensive leaderboard query.
    if str(getattr(settings, "ENABLE_LEADERBOARD", "true")).lower() in {"0", "false", "no"}:
        return []

    try:

        result = db.execute(text("""
            SELECT DISTINCT ON (r.symbol)

                r.symbol,
                m.sharpe,
                m.return_pct,
                m.ml_score

            FROM metrics m

            JOIN backtest_runs r
            ON m.run_id = r.id

            ORDER BY
                r.symbol,
                m.ml_score DESC
        """))

        rows = result.fetchall()

        return leaderboard_rows(rows, explain_strategy)

    except Exception as e:

        logger.error(
            f"❌ LEADERBOARD ERROR: {e}"
        )

        return []


# =========================
# 🚀 STOCK RANKINGS
# =========================
@router.get("/rankings")
def rankings(top_k: int = 10):
    # Render free-tier optimization:
    # Serve precomputed rankings cache and avoid repeated ML inference per request.
    cached = _load_json_cache(RANKINGS_CACHE_PATH)
    if not cached:
        return {
            "status": "error",
            "top_k": top_k,
            "results": [],
            "error": "Rankings cache unavailable. Please run generate_rankings_cache.py",
        }

    try:
        cached_results = cached.get("results", [])
        sanitized = []
        for row in cached_results:
            if not isinstance(row, dict):
                continue
            sanitized.append(
                {
                    "symbol": str(row.get("symbol", "")),
                    "score": round(safe_float(row.get("score")), 4),
                }
            )
        top = sanitized[: max(int(top_k), 0)]

        return {
            "status": "success",
            "top_k": top_k,
            "results": top,
        }

    except Exception as e:

        logger.error(
            f"❌ RANKINGS ERROR: {e}"
        )

        traceback.print_exc()

        return {

            "status":
                "error",

            "top_k":
                top_k,

            "results":
                [],

            "error":
                str(e)
        }


# =========================
# 🚀 PORTFOLIO
# =========================
@router.get("/portfolio")
def portfolio(top_k: int = 10):
    # Render free-tier optimization:
    # Use precomputed portfolio cache to keep endpoint response near-instant.
    cached = _load_json_cache(PORTFOLIO_CACHE_PATH)
    if not cached:
        return {
            "status": "error",
            "portfolio_size": 0,
            "portfolio_return": 0,
            "selected_stocks": [],
            "analytics": sanitize_portfolio_analytics(None),
            "error": "Portfolio cache unavailable. Please run generate_rankings_cache.py",
        }

    try:
        selected = sanitize_stock_records(
            cached.get(
                "selected_stocks",
                []
            )
        )

        return {

            "status":
                "success",

            "portfolio_size":
                len(selected) or top_k,

            "portfolio_return":
                safe_float(
                    cached.get(
                        "portfolio_return",
                        0
                    )
                ),

            "selected_stocks":
                selected,

            "analytics":
                sanitize_portfolio_analytics(
                    cached.get("analytics")
                ),
        }

    except Exception as e:

        logger.error(
            f"❌ PORTFOLIO ERROR: {e}"
        )

        traceback.print_exc()

        return {

            "status":
                "error",

            "portfolio_size":
                0,

            "portfolio_return":
                0,

            "selected_stocks":
                [],

            "analytics":
                sanitize_portfolio_analytics(None),

            "error":
                str(e)
        }