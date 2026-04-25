"""Create and persist users in PostgreSQL, then project into Neo4j."""

from __future__ import annotations

import logging

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import hash_password
from app.db.sql.models.user import User
from app.schemas.pg_data import PgUserCreateRequest
from app.services.neo4j_projection_service import ProjectionResult, project_user_with_retry

_log = logging.getLogger("pulsegrid.pg_user")


class DuplicateEmailError(Exception):
    """Raised when ``users.email`` unique constraint is violated."""


def create_user_with_projection(db: Session, body: PgUserCreateRequest) -> tuple[User, ProjectionResult]:
    """Insert ``users`` row, commit, then best-effort Neo4j projection (never rolls back PG)."""
    email_norm = str(body.email).strip().lower()
    user = User(
        email=email_norm,
        hashed_password=hash_password(body.password),
        phone=(body.phone.strip() if body.phone else None),
        display_name=body.full_name.strip(),
        role=body.role,
    )
    db.add(user)
    try:
        db.flush()
    except IntegrityError as exc:
        db.rollback()
        raise DuplicateEmailError(email_norm) from exc

    _log.info("postgresql_user_flush_ok", extra={"user_id": str(user.id), "email": email_norm})

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise DuplicateEmailError(email_norm) from exc

    db.refresh(user)
    _log.info("postgresql_user_committed", extra={"user_id": str(user.id)})

    settings = get_settings()
    projection = project_user_with_retry(
        settings=settings,
        user_id=str(user.id),
        email=user.email,
        full_name=user.display_name or "",
        phone=user.phone,
        role=user.role,
        max_attempts=1,
    )
    if not projection.ok and not projection.skipped:
        _log.error(
            "postgresql_user_neo4j_projection_failed_post_commit",
            extra={"user_id": str(user.id), "detail": projection.detail},
        )
    return user, projection
