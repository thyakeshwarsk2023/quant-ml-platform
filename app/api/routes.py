from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
)

from sqlalchemy.orm import Session
from sqlalchemy import text, insert
from app.models.backtest import EquityCurve

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
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            logger.warning("Cache payload is not an object for %s", path)
            return None
        return payload
    except Exception as exc:
        logger.warning("Cache read failed for %s: %s", path, exc)
        return None


# =========================
# 🚀 IN-MEMORY JOB STORE & CACHES
# =========================
try:
    from cachetools import TTLCache
except ImportError:
    import time
    class TTLCache(dict):  # type: ignore[no-redef]
        def __init__(self, maxsize=50, ttl=3600):
            super().__init__()
            self._ttl = ttl
            self._times: dict = {}
        def __getitem__(self, key):
            if super().__contains__(key) and time.time() - self._times.get(key, 0) < self._ttl:
                return super().__getitem__(key)
            self.pop(key, None)
            self._times.pop(key, None)
            raise KeyError(key)
        def __setitem__(self, key, value):
            if len(self) >= 50 and key not in self:
                oldest = min(self._times, key=self._times.get) if self._times else None
                if oldest:
                    self.pop(oldest, None)
                    self._times.pop(oldest, None)
            super().__setitem__(key, value)
            self._times[key] = time.time()
        def get(self, key, default=None):
            try:
                return self[key]
            except KeyError:
                return default
        def __contains__(self, key):
            return super().__contains__(key) and time.time() - self._times.get(key, 0) < self._ttl

scan_jobs_lock = threading.Lock()
# Bounded LRU/TTL job store (max 50 jobs, 1 hour expiration)
scan_jobs = TTLCache(maxsize=50, ttl=3600)
_leaderboard_cache = {"data": None, "timestamp": 0.0}
_leaderboard_lock = threading.Lock()
LEADERBOARD_TTL_SECONDS = 60.0


# =========================
# 🚀 SCAN ENDPOINTS
# =========================
@router.post("/scan/start")
def start_scan():
    import uuid
    from concurrent.futures import ThreadPoolExecutor, as_completed
    from app.services.scan_service import process_symbol
    from app.core.data.nifty50 import NIFTY_50

    job_id = str(uuid.uuid4())
    with scan_jobs_lock:
        scan_jobs[job_id] = {
            "status": "running",
            "progress": 0,
            "results": [],
            "error": None
        }

    def _worker():
        try:
            # Scan top symbols from NIFTY_50 plus benchmark AAPL
            symbols = list(NIFTY_50[:10])
            if "AAPL" not in symbols:
                symbols.insert(0, "AAPL")

            total = len(symbols)
            results = []
            completed_count = 0

            # Bounded pool of 4 workers parallelizes scans cleanly
            with ThreadPoolExecutor(max_workers=4) as executor:
                future_to_sym = {
                    executor.submit(process_symbol, sym): sym
                    for sym in symbols
                }
                for future in as_completed(future_to_sym):
                    sym = future_to_sym[future]
                    completed_count += 1
                    try:
                        res = future.result()
                        if res:
                            results.append(res)
                    except Exception as sym_err:
                        logger.warning("Scan failed for symbol %s: %s", sym, sym_err)

                    with scan_jobs_lock:
                        if job_id in scan_jobs:
                            scan_jobs[job_id]["progress"] = int((completed_count / total) * 100)

            results.sort(key=lambda x: x.get("score", 0), reverse=True)
            with scan_jobs_lock:
                if job_id in scan_jobs:
                    scan_jobs[job_id]["results"] = results
                    scan_jobs[job_id]["status"] = "completed"
                    scan_jobs[job_id]["progress"] = 100
            logger.info("Scan job %s completed with %d results", job_id, len(results))

        except Exception as exc:
            logger.exception("Scan job %s failed: %s", job_id, exc)
            with scan_jobs_lock:
                if job_id in scan_jobs:
                    scan_jobs[job_id]["status"] = "failed"
                    scan_jobs[job_id]["error"] = str(exc)

    threading.Thread(target=_worker, daemon=True).start()
    return {
        "status": "started",
        "job_id": job_id
    }


@router.get("/scan/status/{job_id}")
def get_scan_status(job_id: str):
    with scan_jobs_lock:
        job = scan_jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Scan job not found")
    return {
        "job_id": job_id,
        "status": job["status"],
        "progress": job.get("progress", 0),
        "error": job.get("error")
    }


@router.get("/scan/results/{job_id}")
def get_scan_results(job_id: str):
    with scan_jobs_lock:
        job = scan_jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Scan job not found")
    return job.get("results", [])


@router.get("/model/evaluate")
def model_evaluate():
    try:
        from app.ml.evaluate import evaluate_model
        return evaluate_model()
    except Exception as exc:
        logger.exception("Model evaluate error: %s", exc)
        return {
            "status": "error",
            "error": str(exc)
        }


# =========================
# 🚀 LSTM FORECAST
# =========================
@router.get("/forecast")
def stock_forecast(
    symbol: str = Query(..., min_length=1, max_length=20, pattern=r"^[A-Za-z0-9\.\^_\-]+$"),
    period: str = Query("6mo", max_length=10, pattern=r"^[0-9]+[a-z]+$|^max$|^ytd$"),
):

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
def stock_analytics(
    symbol: str = Query(..., min_length=1, max_length=20, pattern=r"^[A-Za-z0-9\.\^_\-]+$"),
    period: str = Query("1y", max_length=10, pattern=r"^[0-9]+[a-z]+$|^max$|^ytd$"),
):

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
    symbol: str = Query(..., min_length=1, max_length=20, pattern=r"^[A-Za-z0-9\.\^_\-]+$"),
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
                    "run_id": run_id,
                    "timestamp": str(p["timestamp"])[:10],
                    "equity": float(p["equity"]),
                }
                for p in bt_result.get(
                    "equity_curve",
                    []
                )
            ]

            if equity_rows:
                local_db.execute(insert(EquityCurve), equity_rows)

            final_cap = (
                float(equity_rows[-1]["equity"])
                if equity_rows
                else None
            )

            # =========================
            # 🚀 COMPLETE
            # =========================
            local_db.execute(text("""
                UPDATE backtest_runs
                SET status='completed',
                    final_capital=:final_cap
                WHERE id=:id
            """), {
                "id": run_id,
                "final_cap": final_cap,
            })

            local_db.commit()

            # Invalidate leaderboard cache so fresh backtest appears immediately
            with _leaderboard_lock:
                _leaderboard_cache["data"] = None

            logger.info(
                f"✅ Completed {symbol} (run {run_id})"
            )

        except Exception as e:

            logger.error(
                f"❌ Failed {symbol} (run {run_id}): {e}"
            )

            traceback.print_exc()

            local_db.rollback()

            try:
                local_db.execute(text("""
                    UPDATE backtest_runs
                    SET status='failed'
                    WHERE id=:id
                """), {
                    "id": run_id
                })

                local_db.commit()
            except Exception as update_err:
                logger.error(f"Failed to update run status to failed: {update_err}")

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
            ORDER BY id ASC
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
# 🚀 RUN STATUS
# =========================
@router.get("/run-status/{run_id}")
def run_status(
    run_id: int,
    db: Session = Depends(get_db)
):
    try:
        run = db.execute(text("""
            SELECT id, symbol, status, initial_capital, final_capital
            FROM backtest_runs
            WHERE id = :id
        """), {"id": run_id}).fetchone()

        if not run:
            raise HTTPException(status_code=404, detail="Run not found")

        metrics_row = db.execute(text("""
            SELECT return_pct, sharpe, max_drawdown, volatility, win_rate, profit_factor, ml_score
            FROM metrics
            WHERE run_id = :id
        """), {"id": run_id}).fetchone()

        metrics_data = None
        if metrics_row:
            metrics_data = {
                "return_pct": safe_float(metrics_row[0]),
                "sharpe": safe_float(metrics_row[1]),
                "max_drawdown": safe_float(metrics_row[2]),
                "volatility": safe_float(metrics_row[3]),
                "win_rate": safe_float(metrics_row[4]),
                "profit_factor": safe_float(metrics_row[5]),
                "ml_score": safe_float(metrics_row[6]),
            }

        return {
            "id": run[0],
            "symbol": run[1],
            "status": run[2],
            "initial_capital": safe_float(run[3], 100000.0),
            "final_capital": safe_float(run[4]) if run[4] is not None else None,
            "metrics": metrics_data,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ RUN STATUS ERROR: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch run status") from e


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

    import time
    now = time.time()
    with _leaderboard_lock:
        if _leaderboard_cache["data"] is not None and (now - _leaderboard_cache["timestamp"] < LEADERBOARD_TTL_SECONDS):
            return _leaderboard_cache["data"]

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
        data = leaderboard_rows(rows, explain_strategy)

        with _leaderboard_lock:
            _leaderboard_cache["data"] = data
            _leaderboard_cache["timestamp"] = now

        return data

    except Exception as e:

        logger.error(
            f"❌ LEADERBOARD ERROR: {e}"
        )

        return []


# =========================
# 🚀 STOCK RANKINGS
# =========================
@router.get("/rankings")
def rankings(top_k: int = Query(10, ge=1, le=100)):
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
def portfolio(top_k: int = Query(10, ge=1, le=100)):
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