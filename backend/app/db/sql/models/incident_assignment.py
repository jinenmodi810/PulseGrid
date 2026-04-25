"""Assignment schema reserved for future PostgreSQL incident migration.

Current assignment lifecycle is Neo4j-primary (see volunteer/coordinator services).
"""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text, Uuid, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.sql.base import Base
from app.db.sql.enums import AssignmentStatus
from app.db.sql.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.db.sql.models.incident import Incident
    from app.db.sql.models.user import User


class IncidentAssignment(TimestampMixin, Base):
    __tablename__ = "incident_assignments"
    __table_args__ = (UniqueConstraint("incident_id", "responder_user_id", name="uq_assignment_incident_responder"),)

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    incident_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("incidents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    responder_user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    status: Mapped[AssignmentStatus] = mapped_column(
        Enum(AssignmentStatus, name="assignment_status", native_enum=False, length=32),
        nullable=False,
        default=AssignmentStatus.pending,
        index=True,
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    assigned_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    incident: Mapped["Incident"] = relationship(back_populates="assignments")
    responder: Mapped["User"] = relationship(foreign_keys=[responder_user_id])
