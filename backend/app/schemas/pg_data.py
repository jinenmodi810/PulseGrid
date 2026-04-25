"""API shapes for PostgreSQL-backed /data routes."""

from __future__ import annotations

from enum import Enum
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.db.sql.enums import UserRole


class Neo4jProjectionStatus(str, Enum):
    ok = "ok"
    failed = "failed"
    skipped = "skipped"


class PgUserCreateRequest(BaseModel):
    """Bootstrap / integration only — victims must use ``POST /auth/register-victim``."""

    full_name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    phone: str | None = Field(default=None, max_length=64)
    role: UserRole

    @field_validator("role")
    @classmethod
    def _use_auth_routes_for_profiles(cls, v: UserRole) -> UserRole:
        if v in (UserRole.victim, UserRole.volunteer):
            raise ValueError(
                "Victim and volunteer accounts must be created via "
                "POST /auth/register-victim or POST /auth/register-volunteer, not /data/users."
            )
        return v


class PgUserCreatedResponse(BaseModel):
    id: UUID
    email: EmailStr
    display_name: str | None
    phone: str | None
    role: UserRole
    is_active: bool
    neo4j_projection: Neo4jProjectionStatus
    neo4j_detail: str | None = None
