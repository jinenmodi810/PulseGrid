"""Deterministic response-tier planning (mother brain input/output). AI must not set these tiers."""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class ResponseTierName(str, Enum):
    """Final operational routing class for an incident (after matching when applicable)."""

    volunteer_only = "volunteer_only"
    organization_only = "organization_only"
    volunteer_plus_organization = "volunteer_plus_organization"
    escalation_required = "escalation_required"


class ResponseTierReason(BaseModel):
    """Single explainable rule contribution."""

    code: str = Field(..., description="Stable machine code, e.g. medical_institutional")
    detail: str = Field(..., description="Human-readable explanation")


class ResponseTierInput(BaseModel):
    """Normalized snapshot passed to the tier engine (no Neo4j reads inside the engine)."""

    incident_type: str = ""
    severity: str = "medium"
    priority_score: float = 0.0
    priority_label: str = "MEDIUM"
    people_count: int = 1
    zone_id: str = ""
    injury: bool = False
    elderly: bool = False
    child_present: bool = False
    oxygen_required: bool = False
    shelter_needed: bool = False
    food_needed: bool = False
    transport_needed: bool = False
    note: str = ""
    # Victim profile (optional)
    household_size: int | None = None
    elderly_count: int | None = None
    mobility_concern: bool = False
    oxygen_dependency_profile: bool = False
    preferred_language: str = ""
    # Logistics hints (optional; TODO: Google Maps ETA, airlift)
    blocked_route: bool = False
    route_risk: str = ""  # e.g. high, medium, low
    estimated_eta_minutes: int | None = None


class ResponseTierPlan(BaseModel):
    """Pre-matching plan: which candidate pools to query and why."""

    intended_tier: ResponseTierName = Field(
        ...,
        description="Target collaboration shape before availability checks.",
    )
    seek_volunteer: bool = True
    seek_organization: bool = False
    reasons: list[ResponseTierReason] = Field(default_factory=list)
    decision_summary: str = ""
    # When true, matching failures for required assets should strongly consider escalation.
    high_acuity: bool = False


class ResponseTierDecision(BaseModel):
    """Final persisted/API decision after matching."""

    response_tier: str = Field(..., description="One of ResponseTierName values")
    escalation_required: bool = False
    volunteer_candidate_allowed: bool = True
    organization_candidate_allowed: bool = False
    reasons: list[ResponseTierReason] = Field(default_factory=list)
    decision_summary: str = ""
    assigned_volunteer: dict[str, Any] | None = None
    assigned_organization: dict[str, Any] | None = None
    rejected_volunteers: list[dict[str, str]] = Field(default_factory=list)
    rejected_organizations: list[dict[str, str]] = Field(default_factory=list)
