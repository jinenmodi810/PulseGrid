"""Geographic / service zones (canonical ids align with Flutter ``kAuthZoneIds``)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.sql.base import Base
from app.db.sql.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.db.sql.models.responder_profile import ResponderProfile
    from app.db.sql.models.victim_profile import VictimProfile


class Zone(TimestampMixin, Base):
    __tablename__ = "zones"

    id: Mapped[str] = mapped_column(String(120), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)

    victim_profiles: Mapped[list["VictimProfile"]] = relationship(back_populates="zone")
    responder_profiles: Mapped[list["ResponderProfile"]] = relationship(back_populates="zone")
