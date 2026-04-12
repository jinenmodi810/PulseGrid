"""Hospital / shelter assignment (Phase 1: capacity + REFERRED_TO graph rules)."""

from __future__ import annotations

from app.models.assignment_result import AssignmentResultRead


def assign_destination(*, incident_id: str, destination_id: str) -> AssignmentResultRead:
    # TODO(Phase1): validate beds, geography, and policy via Neo4j.
    return AssignmentResultRead(
        incident_id=incident_id,
        assigned_resource_id=destination_id,
        accepted=True,
        rejection_reasons=[],
    )
