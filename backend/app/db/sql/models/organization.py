"""Organization entity (system of record)."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, Integer, String, Uuid, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.sql.base import Base
from app.db.sql.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.db.sql.models.incident import Incident
    from app.db.sql.models.user import User


class Organization(TimestampMixin, Base):
    __tablename__ = "organizations"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    legal_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    contact_email: Mapped[str] = mapped_column(String(320), nullable=False, unique=True, index=True)
    hashed_password: Mapped[str | None] = mapped_column(String(255), nullable=True)
    contact_phone: Mapped[str | None] = mapped_column(String(64), nullable=True)
    contact_name: Mapped[str] = mapped_column(String(200), nullable=False, server_default=text("''"))
    org_type: Mapped[str] = mapped_column(String(80), nullable=False, server_default=text("'ngo'"))
    zone_id: Mapped[str | None] = mapped_column(
        String(128),
        ForeignKey("zones.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    coverage_zone_ids: Mapped[list[str]] = mapped_column(JSONB, nullable=False, server_default=text("'[]'::jsonb"))
    beds_available: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    oxygen_units: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    ambulances_available: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    shelter_units: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    food_capacity_units: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    rescue_units: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    owner_user_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default="true")

    owner: Mapped["User | None"] = relationship(
        back_populates="organizations_owned",
        foreign_keys=[owner_user_id],
    )
    incidents: Mapped[list["Incident"]] = relationship(back_populates="organization")
