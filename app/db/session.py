import logging
import os
from collections.abc import Generator

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import NullPool

load_dotenv(dotenv_path=".env")

logger = logging.getLogger(__name__)


def _normalize_database_url(url: str) -> str:
    """Normalize Neon/Heroku-style URLs for SQLAlchemy + psycopg2."""
    url = url.strip()
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+psycopg2://", 1)
    elif url.startswith("postgresql://") and "+psycopg2" not in url:
        url = url.replace("postgresql://", "postgresql+psycopg2://", 1)
    return url


DATABASE_URL = os.getenv("DATABASE_URL", "").strip()

engine = None
SessionLocal = None


def _init_engine() -> None:
    global engine, SessionLocal

    if SessionLocal is not None:
        return

    if not DATABASE_URL:
        logger.warning("DATABASE_URL is not set — database endpoints will fail")
        SessionLocal = sessionmaker()
        return

    normalized = _normalize_database_url(DATABASE_URL)
    connect_args = {}
    if "sslmode" not in normalized.lower() and (
        "neon.tech" in normalized.lower() or os.getenv("DATABASE_SSL", "").lower() == "true"
    ):
        connect_args["sslmode"] = "require"

    engine_options = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
        "connect_args": connect_args,
    }

    if os.getenv("VERCEL"):
        engine_options["poolclass"] = NullPool
    else:
        engine_options.update(
            {
                "pool_size": int(os.getenv("DB_POOL_SIZE", "2")),
                "max_overflow": int(os.getenv("DB_MAX_OVERFLOW", "2")),
                "pool_timeout": int(os.getenv("DB_POOL_TIMEOUT", "10")),
            }
        )

    engine = create_engine(normalized, **engine_options)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    logger.info("Database engine initialized")


def get_db() -> Generator[Session, None, None]:
    _init_engine()
    if engine is None:
        raise RuntimeError("DATABASE_URL is not configured")
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_database_connection() -> dict:
    """Lightweight DB probe for health checks."""
    _init_engine()
    if engine is None:
        return {"ok": False, "error": "DATABASE_URL not configured"}

    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"ok": True}
    except Exception as exc:
        logger.exception("Database health check failed")
        return {"ok": False, "error": str(exc)}
