"""Victim / resident profile (1:1 with ``users`` row where role is victim).

``account_id`` is the PostgreSQL ``users.id`` (canonical id used in JWT and Neo4j :User).
Display name and household fields mirror ``RegisterVictimAuthRequest`` / Flutter payload.
"""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, Integer, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.sql.base import Base
from app.db.sql.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.db.sql.models.user import User
    from app.db.sql.models.zone import Zone


class VictimProfile(TimestampMixin, Base):
    __tablename__ = "victim_profiles"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account_id: Mapped[uuid.UUID] = mapped_column(
        "account_id",
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    preferred_language: Mapped[str] = mapped_column(String(32), nullable=False, default="en", server_default="en")
    home_zone_id: Mapped[str] = mapped_column(
        String(120),
        ForeignKey("zones.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    household_size: Mapped[int | None] = mapped_column(Integer, nullable=True)
    elderly_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    mobility_concern: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")
    oxygen_dependency: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")
    emergency_contact_name: Mapped[str] = mapped_column(String(200), nullable=False)
    emergency_contact_phone: Mapped[str] = mapped_column(String(40), nullable=False)
    emergency_contact_relationship: Mapped[str] = mapped_column(
        String(120), nullable=False, default="", server_default=""
    )

    user: Mapped["User"] = relationship(back_populates="victim_profile", foreign_keys=[account_id])
    zone: Mapped["Zone"] = relationship(back_populates="victim_profiles")
