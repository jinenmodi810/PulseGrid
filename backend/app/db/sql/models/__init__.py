"""Import order registers all mappers on shared Base.metadata."""

from __future__ import annotations

from app.db.sql.models.user import User
from app.db.sql.models.zone import Zone
from app.db.sql.models.organization import Organization
from app.db.sql.models.incident import Incident
from app.db.sql.models.responder_profile import ResponderProfile
from app.db.sql.models.victim_profile import VictimProfile
from app.db.sql.models.incident_assignment import IncidentAssignment
from app.db.sql.models.incident_event import IncidentEvent
from app.db.sql.models.event_outbox import EventOutbox

__all__ = [
    "User",
    "Zone",
    "Organization",
    "Incident",
    "ResponderProfile",
    "VictimProfile",
    "IncidentAssignment",
    "IncidentEvent",
    "EventOutbox",
]
