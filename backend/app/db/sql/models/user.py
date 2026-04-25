"""Application account (system of record): credentials + role.

Victim display and household data live in ``VictimProfile``. Optional ``display_name`` supports
bootstrap / non-victim rows until volunteer/org profile tables exist.
"""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Enum, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.sql.base import Base
from app.db.sql.enums import UserRole
from app.db.sql.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.db.sql.models.incident import Incident
    from app.db.sql.models.organization import Organization
    from app.db.sql.models.responder_profile import ResponderProfile
    from app.db.sql.models.victim_profile import VictimProfile


class User(TimestampMixin, Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(320), nullable=False, unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    display_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, name="user_role", native_enum=False, length=32),
        nullable=False,
        index=True,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default="true")

    organizations_owned: Mapped[list["Organization"]] = relationship(
        back_populates="owner",
        foreign_keys="Organization.owner_user_id",
    )
    incidents_reported: Mapped[list["Incident"]] = relationship(back_populates="reporter")
    responder_profile: Mapped["ResponderProfile | None"] = relationship(
        back_populates="user",
        uselist=False,
    )
    victim_profile: Mapped["VictimProfile | None"] = relationship(
        back_populates="user",
        uselist=False,
    )
