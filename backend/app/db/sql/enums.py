"""Enumerations stored as constrained strings in PostgreSQL."""

from __future__ import annotations

import enum


class UserRole(str, enum.Enum):
    victim = "victim"
    volunteer = "volunteer"
    organization = "organization"
    admin = "admin"


class IncidentStatus(str, enum.Enum):
    open = "open"
    triaged = "triaged"
    assigned = "assigned"
    in_progress = "in_progress"
    resolved = "resolved"
    cancelled = "cancelled"


class IncidentSeverity(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class AssignmentStatus(str, enum.Enum):
    pending = "pending"
    accepted = "accepted"
    declined = "declined"
    completed = "completed"
    revoked = "revoked"
