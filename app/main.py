import logging
import json
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import Depends, FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.api.routes import router
from app.core.config import settings
from app.core.logging_config import setup_logging
from app.db.session import check_database_connection, get_db

logger = logging.getLogger(__name__)

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

origins = [
    "http://localhost:5173",
    "https://quant-ml-platform-jfs39x556-thyakesh-s-projects.vercel.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
def home():
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
