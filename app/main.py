import logging
import json
from contextlib import asynccontextmanager
from pathlib import Path
from time import perf_counter
from uuid import uuid4
from fastapi import Depends, FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from app.api.routes import router
from app.core.config import settings
from app.core.logging_config import setup_logging
from app.db.session import check_database_connection, get_db

logger = logging.getLogger(__name__)

FRONTEND_DIST = Path(__file__).resolve().parent.parent / "frontend" / "dist"
SPA_ROUTES = {"rankings", "portfolio", "backtests", "scanner", "analytics"}

CACHE_FILES = (
    Path("data_cache/rankings.json"),
    Path("data_cache/portfolio.json"),
)


def _log_cache_status() -> None:
    """
    Render production startup diagnostics:
    confirm cache file existence and JSON readability.
    """
    for cache_path in CACHE_FILES:
        if not cache_path.exists():
            logger.warning("Cache missing at startup: %s", cache_path)
            continue
        try:
            payload = json.loads(cache_path.read_text(encoding="utf-8"))
            if isinstance(payload, dict):
                logger.info("Cache load success: %s", cache_path)
            else:
                logger.warning("Cache load failed (invalid payload type): %s", cache_path)
        except Exception as exc:
            logger.warning("Cache load failed for %s: %s", cache_path, exc)


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    logger.info("Starting Quant ML API (env=%s)", settings.ENVIRONMENT)
    _log_cache_status()

    db_status = check_database_connection()
    if db_status.get("ok"):
        logger.info("Database connection verified at startup")
    else:
        logger.warning(
            "Database not ready at startup: %s",
            db_status.get("error", "unknown"),
        )

    yield
    logger.info("Shutting down Quant ML API")


app = FastAPI(
    title="Quant ML Research Platform",
    description=(
        "ML-driven quantitative research platform for stock ranking, "
        "strategy backtesting, and portfolio simulation."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_origin_regex=settings.CORS_ORIGIN_REGEX or None,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def request_diagnostics(request: Request, call_next):
    request_id = request.headers.get("x-request-id", str(uuid4()))
    started = perf_counter()
    try:
        response = await call_next(request)
    except Exception:
        logger.exception(
            "Request failed request_id=%s method=%s path=%s",
            request_id,
            request.method,
            request.url.path,
        )
        raise

    duration_ms = int((perf_counter() - started) * 1000)
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Response-Time-ms"] = str(duration_ms)
    if duration_ms > 10000:
        logger.warning(
            "Slow request request_id=%s method=%s path=%s duration_ms=%s",
            request_id,
            request.method,
            request.url.path,
            duration_ms,
        )
    return response


@app.middleware("http")
async def spa_fallback_middleware(request: Request, call_next):
    path = request.url.path.strip("/")
    accept = request.headers.get("accept", "")
    if request.method == "GET" and "text/html" in accept:
        route_root = path.split("/")[0] if path else ""
        if route_root in SPA_ROUTES and (FRONTEND_DIST / "index.html").is_file():
            return FileResponse(FRONTEND_DIST / "index.html")
    return await call_next(request)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error on %s %s", request.method, request.url.path)
    detail = "Internal server error"
    if not settings.is_production:
        detail = str(exc)
    return JSONResponse(status_code=500, content={"status": "error", "detail": detail})


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"status": "error", "detail": exc.errors()},
    )


@app.get("/")
def home(request: Request):
    index_file = FRONTEND_DIST / "index.html"
    accept = request.headers.get("accept", "")
    if index_file.is_file() and "text/html" in accept:
        return FileResponse(index_file)
    return {
        "message": "Quant ML API Running",
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health")
def health():
    """Liveness probe — returns 200 if the process is up."""
    return {
        "status": "ok",
        "environment": settings.ENVIRONMENT,
        "version": "1.0.0",
    }


@app.get("/health/ready")
def health_ready():
    """Readiness probe — includes database connectivity."""
    db = check_database_connection()
    status = "ok" if db.get("ok") else "degraded"
    code = 200 if db.get("ok") else 503
    return JSONResponse(
        status_code=code,
        content={
            "status": status,
            "database": "connected" if db.get("ok") else "disconnected",
            "error": db.get("error"),
            "environment": settings.ENVIRONMENT,
        },
    )


@app.get("/test-db")
def test_db(db: Session = Depends(get_db)):
    from sqlalchemy import text

    try:
        result = db.execute(text("SELECT 1"))
        return {"database": "connected", "result": result.scalar()}
    except Exception as exc:
        logger.exception("test-db failed")
        return {"database": "failed", "error": str(exc)}


app.include_router(router)

# Mount frontend assets for production / unified full-stack serving
if (FRONTEND_DIST / "assets").is_dir():
    app.mount("/assets", StaticFiles(directory=str(FRONTEND_DIST / "assets")), name="assets")


@app.get("/{full_path:path}")
def catch_all_spa(full_path: str, request: Request):
    index_file = FRONTEND_DIST / "index.html"
    static_file = FRONTEND_DIST / full_path

    # Serve static files directly from dist (favicon.svg, icons.svg, etc.)
    if full_path and static_file.is_file():
        return FileResponse(static_file)

    accept = request.headers.get("accept", "")
    route_root = full_path.split("/")[0] if full_path else ""
    if index_file.is_file() and ("text/html" in accept or route_root in SPA_ROUTES):
        return FileResponse(index_file)

    return JSONResponse(
        status_code=404,
        content={"status": "error", "detail": f"Path /{full_path} not found"}
    )
