"""HTTP surface for PostgreSQL system-of-record operations (alongside legacy Neo4j routes)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps.db_deps import get_db
from app.core.config import get_settings
from app.db.sql.session import ping_database
from app.schemas.pg_data import Neo4jProjectionStatus, PgUserCreateRequest, PgUserCreatedResponse
from app.services.pg_user_service import DuplicateEmailError, create_user_with_projection

router = APIRouter(prefix="/data", tags=["data-postgresql"])


@router.get("/health/postgres")
def postgres_health() -> dict:
    """Whether DATABASE_URL is set and the server answers ``SELECT 1``."""
    settings = get_settings()
    configured = bool((settings.DATABASE_URL or "").strip())
    return {
        "postgresql_configured": configured,
        "postgresql_reachable": ping_database() if configured else False,
        "pg_write_routes_enabled": settings.PG_WRITE_ROUTES_ENABLED,
    }


@router.post("/users", response_model=PgUserCreatedResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    body: PgUserCreateRequest,
    db: Session = Depends(get_db),
) -> PgUserCreatedResponse:
    """Create a user in PostgreSQL and project to Neo4j (gated by ``PG_WRITE_ROUTES_ENABLED``)."""
    settings = get_settings()
    if not settings.PG_WRITE_ROUTES_ENABLED:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="PG write routes are disabled (set PG_WRITE_ROUTES_ENABLED=true for local use).",
        )
    try:
        user, projection = create_user_with_projection(db, body)
    except DuplicateEmailError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered.") from None

    neo_status = Neo4jProjectionStatus.skipped if projection.skipped else (
        Neo4jProjectionStatus.ok if projection.ok else Neo4jProjectionStatus.failed
    )
    return PgUserCreatedResponse(
        id=user.id,
        email=user.email,
        display_name=user.display_name,
        phone=user.phone,
        role=user.role,
        is_active=user.is_active,
        neo4j_projection=neo_status,
        neo4j_detail=projection.detail,
    )
