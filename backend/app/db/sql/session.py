"""SQLAlchemy engine and session factory (lazy, keyed off Settings.DATABASE_URL)."""

from __future__ import annotations

import logging
from typing import Callable, Optional

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings

_log = logging.getLogger("pulsegrid.pg")

_engine: Optional[Engine] = None
_SessionLocal: Optional[Callable[[], Session]] = None


def _build_engine(url: str) -> Engine:
    return create_engine(
        url,
        pool_pre_ping=True,
        future=True,
        echo=False,
    )


def get_engine() -> Engine | None:
    """Return a process-wide engine, or None if DATABASE_URL is unset."""
    global _engine, _SessionLocal
    url = (get_settings().DATABASE_URL or "").strip()
    if not url:
        return None
    if _engine is None:
        _log.info("initializing_postgresql_engine")
        _engine = _build_engine(url)
        _SessionLocal = sessionmaker(bind=_engine, autoflush=False, autocommit=False, future=True)
    return _engine


def get_session_factory() -> Callable[[], Session] | None:
    """Session factory bound to the shared engine, or None if PostgreSQL is not configured."""
    eng = get_engine()
    if eng is None:
        return None
    assert _SessionLocal is not None
    return _SessionLocal


def ping_database() -> bool:
    """Run a trivial query; returns False if not configured or connection fails."""
    factory = get_session_factory()
    if factory is None:
        return False
    try:
        with factory() as session:
            session.execute(text("SELECT 1"))
        return True
    except Exception:
        _log.exception("postgresql_ping_failed")
        return False


def dispose_sql_engine() -> None:
    """Release connection pools (call from application lifespan on shutdown)."""
    global _engine, _SessionLocal
    if _engine is not None:
        _log.info("disposing_postgresql_engine")
        _engine.dispose()
        _engine = None
        _SessionLocal = None
