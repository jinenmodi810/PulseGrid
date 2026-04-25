"""FastAPI dependencies for relational database access."""

from __future__ import annotations

from collections.abc import Generator

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.db.sql.session import get_session_factory


def get_db_optional() -> Generator[Session | None, None, None]:
    """Yield a session when ``DATABASE_URL`` is set; otherwise ``None`` (legacy Neo4j-only paths)."""
    factory = get_session_factory()
    if factory is None:
        yield None
        return
    db = factory()
    try:
        yield db
    finally:
        db.close()


def get_db() -> Generator[Session, None, None]:
    """Yield a request-scoped SQLAlchemy session (commit/rollback owned by caller/services)."""
    factory = get_session_factory()
    if factory is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="PostgreSQL is not configured (set DATABASE_URL).",
        )
    db = factory()
    try:
        yield db
    finally:
        db.close()
