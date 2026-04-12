"""Single normalized input for response tier + matching (mother engine). No scattered dict reads in callers."""

from __future__ import annotations

from pydantic import BaseModel, Field

from app.models.incident_requests import CreateIncidentRequest
from app.models.response_tier_models import ResponseTierInput


def normalize_severity_1_to_5(severity: str, *, priority_label: str = "") -> int:
    """Map free-text severity + urgent label to 1–5 for analytics and future ML hooks."""
    s = (severity or "").strip().lower()
    base = {"low": 1, "medium": 2, "moderate": 2, "high": 3, "critical": 5, "severe": 5}.get(s, 2)
    u = (priority_label or "").upper()
    if "CRITICAL" in u or "URGENT" in u:
        return max(base, 5)
    if "HIGH" in u:
        return max(base, 3)
    return base


class ResponseEngineInput(BaseModel):
    """Unified decisioning snapshot built once per SOS (after profile merge)."""

    disaster_type: str = Field(default="", description="Same as incident_type in API")
    severity: str = "medium"
    severity_normalized: int = 2
    people_count: int = 1
    zone_id: str = ""
    oxygen_required: bool = False
    elderly: bool = False
    child_present: bool = False
    injury: bool = False
    shelter_needed: bool = False
    food_needed: bool = False
    transport_needed: bool = False
    mobility_concern: bool = False
    preferred_language: str = ""
    note: str = ""
    household_size: int | None = None
    elderly_count: int | None = None
    oxygen_dependency_profile: bool = False
    priority_score: float = 0.0
    priority_label: str = "MEDIUM"
    intake_source: str = "form"
    # TODO(geo): lat/lng on incident + geodesic distance when mobile clients send coordinates.
    latitude: float | None = None
    longitude: float | None = None
    # TODO(logistics): Google Maps ETA, traffic, route blockage, airlift recommendation — wire from external APIs.
    blocked_route: bool = False
    route_risk: str = ""
    estimated_eta_minutes: int | None = None

    def to_response_tier_input(self) -> ResponseTierInput:
        return ResponseTierInput(
            incident_type=self.disaster_type,
            severity=self.severity,
            priority_score=self.priority_score,
            priority_label=self.priority_label,
            people_count=self.people_count,
            zone_id=self.zone_id,
            injury=self.injury,
            elderly=self.elderly,
            child_present=self.child_present,
            oxygen_required=self.oxygen_required,
            shelter_needed=self.shelter_needed,
            food_needed=self.food_needed,
            transport_needed=self.transport_needed,
            note=self.note,
            household_size=self.household_size,
            elderly_count=self.elderly_count,
            mobility_concern=self.mobility_concern,
            oxygen_dependency_profile=self.oxygen_dependency_profile,
            preferred_language=self.preferred_language,
            blocked_route=self.blocked_route,
            route_risk=self.route_risk,
            estimated_eta_minutes=self.estimated_eta_minutes,
        )

    @classmethod
    def from_create_context(
        cls,
        *,
        body: CreateIncidentRequest,
        people_count: int,
        elderly: bool,
        oxygen_required: bool,
        preferred_language: str,
        mobility_concern: bool,
        household_size: int | None,
        elderly_count: int | None,
        oxygen_dependency_profile: bool,
        priority_score: float,
        priority_label: str,
    ) -> ResponseEngineInput:
        sev_norm = normalize_severity_1_to_5(body.severity, priority_label=priority_label)
        return cls(
            disaster_type=body.incident_type.strip(),
            severity=body.severity,
            severity_normalized=sev_norm,
            people_count=max(1, int(people_count)),
            zone_id=body.zone_id.strip(),
            oxygen_required=oxygen_required,
            elderly=elderly,
            child_present=body.child_present,
            injury=body.injury,
            shelter_needed=body.shelter_needed,
            food_needed=body.food_needed,
            transport_needed=body.transport_needed,
            mobility_concern=mobility_concern,
            preferred_language=preferred_language,
            note=body.note,
            household_size=household_size,
            elderly_count=elderly_count,
            oxygen_dependency_profile=oxygen_dependency_profile,
            priority_score=priority_score,
            priority_label=priority_label,
            intake_source=(body.intake_source or "form").strip() or "form",
        )
