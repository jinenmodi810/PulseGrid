"""Incident record schema reserved for future PostgreSQL migration.

Current runtime incident lifecycle (create/list/detail/assign/complete/coordinator actions)
is Neo4j-primary in ``app/services/incident_service.py`` and related task/coordinator services.
"""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, Float, ForeignKey, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.sql.base import Base
from app.db.sql.enums import IncidentSeverity, IncidentStatus
from app.db.sql.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.db.sql.models.incident_assignment import IncidentAssignment
    from app.db.sql.models.incident_event import IncidentEvent
    from app.db.sql.models.organization import Organization
    from app.db.sql.models.user import User


class Incident(TimestampMixin, Base):
    __tablename__ = "incidents"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("organizations.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    reporter_user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    incident_type: Mapped[str | None] = mapped_column(String(128), nullable=True, index=True)
    status: Mapped[IncidentStatus] = mapped_column(
        Enum(IncidentStatus, name="incident_status", native_enum=False, length=32),
        nullable=False,
        default=IncidentStatus.open,
        index=True,
    )
    severity: Mapped[IncidentSeverity] = mapped_column(
        Enum(IncidentSeverity, name="incident_severity", native_enum=False, length=32),
        nullable=False,
        default=IncidentSeverity.medium,
        index=True,
    )
    priority_score: Mapped[float | None] = mapped_column(Float, nullable=True, index=True)
    priority_label: Mapped[str | None] = mapped_column(String(64), nullable=True)
    zone_id: Mapped[str | None] = mapped_column(String(128), nullable=True, index=True)
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    closed_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    organization: Mapped["Organization | None"] = relationship(back_populates="incidents")
    reporter: Mapped["User"] = relationship(back_populates="incidents_reported")
    assignments: Mapped[list["IncidentAssignment"]] = relationship(back_populates="incident")
    events: Mapped[list["IncidentEvent"]] = relationship(back_populates="incident")
