"""Responder / volunteer profile linked to a ``users`` row (role volunteer)."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Any

from sqlalchemy import Boolean, Float, ForeignKey, Integer, String, Uuid, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.sql.base import Base
from app.db.sql.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.db.sql.models.user import User
    from app.db.sql.models.zone import Zone


class ResponderProfile(TimestampMixin, Base):
    __tablename__ = "responder_profiles"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    display_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    skills: Mapped[list[Any]] = mapped_column(JSONB, nullable=False, server_default=text("'[]'::jsonb"))
    languages: Mapped[list[Any]] = mapped_column(JSONB, nullable=False, server_default=text("'[]'::jsonb"))
    support_types: Mapped[list[Any]] = mapped_column(JSONB, nullable=False, server_default=text("'[]'::jsonb"))
    zone_id: Mapped[str | None] = mapped_column(
        String(128),
        ForeignKey("zones.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    availability: Mapped[str | None] = mapped_column(String(255), nullable=True)
    transport_access: Mapped[str | None] = mapped_column(String(80), nullable=True)
    verified: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))
    skill_type: Mapped[str | None] = mapped_column(String(120), nullable=True)
    credits: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    trust_score: Mapped[float] = mapped_column(Float, nullable=False, server_default=text("0.5"))

    user: Mapped["User"] = relationship(back_populates="responder_profile")
    zone: Mapped["Zone | None"] = relationship(back_populates="responder_profiles")
