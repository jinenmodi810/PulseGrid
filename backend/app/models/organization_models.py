"""API contracts for organization operations."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class OrganizationOverviewResponse(BaseModel):
    organization_id: str
    name: str
    org_type: str = ""
    zone_id: str = ""
    active: bool = True
    assigned_incidents_open: int = 0
    capacity: dict[str, Any] = Field(default_factory=dict)


class OrganizationIncidentItem(BaseModel):
    incident_id: str
    incident_type: str = ""
    severity: str = "medium"
    status: str = "open"
    priority_label: str = "MEDIUM"
    priority_score: float = 0.0
    zone_id: str = ""
    assigned_volunteer_name: str = ""
    response_tier: str = ""
    escalation_required: bool = False
    decision_summary: str = ""
    volunteer_support_active: bool = False
    created_at: str | None = None


class CapacityUpdateRequest(BaseModel):
    """Partial capacity fields; merged onto Organization node."""

    beds_available: int | None = None
    oxygen_units: int | None = None
    ambulances_available: int | None = None
    shelter_units: int | None = None
    food_capacity_units: int | None = None
    rescue_units: int | None = None
    active: bool | None = None


class AcceptIncidentBody(BaseModel):
    incident_id: str = Field(..., min_length=1)


class UpdateResponseStatusBody(BaseModel):
    incident_id: str = Field(..., min_length=1)
    status: str = Field(..., min_length=1, max_length=120)
