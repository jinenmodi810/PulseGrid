"""API contracts for incident creation and tracking."""

from __future__ import annotations

from pydantic import BaseModel, Field

from app.models.response_tier_models import ResponseTierReason


class PriorityPreviewRequest(BaseModel):
    """Subset of incident fields for live priority preview (no persistence)."""

    severity: str = Field(default="medium")
    people_count: int = Field(default=1, ge=1, le=500)
    elderly: bool = False
    child_present: bool = False
    injury: bool = False
    oxygen_required: bool = False
    shelter_needed: bool = False
    food_needed: bool = False
    transport_needed: bool = False


class PriorityPreviewResponse(BaseModel):
    priority_score: float
    priority_label: str


class RejectedCandidate(BaseModel):
    volunteer_id: str
    name: str
    reason: str


class RejectedOrganizationCandidate(BaseModel):
    organization_id: str
    name: str
    reason: str


class CreateIncidentRequest(BaseModel):
    user_id: str = Field(..., min_length=1)
    incident_type: str = Field(..., min_length=1, max_length=120)
    severity: str = Field(default="medium", max_length=32)
    people_count: int = Field(default=1, ge=1, le=500)
    zone_id: str = Field(..., min_length=1, max_length=120)
    elderly: bool = False
    child_present: bool = False
    injury: bool = False
    oxygen_required: bool = False
    shelter_needed: bool = False
    food_needed: bool = False
    transport_needed: bool = False
    note: str = Field(default="", max_length=2000)
    # When true, corresponding field is replaced from the reporting user's Neo4j profile before scoring.
    use_profile_for_people_count: bool = Field(default=True)
    use_profile_for_elderly: bool = Field(default=True)
    use_profile_for_oxygen_required: bool = Field(default=True)
    # "form" | "voice_stub" — voice path prepares same engine; full STT/TTS is future work.
    intake_source: str = Field(default="form", max_length=32)


class EmergencyContactResponse(BaseModel):
    """Snapshot for ops / future SMS. TODO: wire outbound notifications."""

    name: str = ""
    phone: str = ""
    relationship: str = ""


class CreateIncidentResponse(BaseModel):
    incident_id: str
    zone_id: str = ""
    status: str
    priority_score: float
    priority_label: str
    assigned_helper: dict | None = None
    assigned_organization: dict | None = None
    response_tier: str = "pending"
    volunteer_candidate_allowed: bool = True
    organization_candidate_allowed: bool = False
    escalation_required: bool = False
    decision_summary: str = ""
    tier_reasons: list[ResponseTierReason] = Field(default_factory=list)
    rejected_candidates: list[RejectedCandidate] = Field(default_factory=list)
    rejected_organization_candidates: list[RejectedOrganizationCandidate] = Field(default_factory=list)
    eta_minutes: int | None = None
    ai_guidance: str = ""
    preferred_language: str = ""
    emergency_contact: EmergencyContactResponse | None = None
    profile_defaults_used: list[str] = Field(default_factory=list)


class IncidentDetailResponse(BaseModel):
    incident_id: str
    incident_type: str
    severity: str
    people_count: int
    zone_id: str
    status: str
    priority_score: float
    priority_label: str
    note: str = ""
    assigned_helper: dict | None = None
    assigned_organization: dict | None = None
    response_tier: str = "pending"
    volunteer_candidate_allowed: bool = True
    organization_candidate_allowed: bool = False
    escalation_required: bool = False
    decision_summary: str = ""
    tier_reasons: list[ResponseTierReason] = Field(default_factory=list)
    rejected_candidates: list[RejectedCandidate] = Field(default_factory=list)
    rejected_organization_candidates: list[RejectedOrganizationCandidate] = Field(default_factory=list)
    eta_minutes: int | None = None
    route_status: str = "pending"
    ai_guidance: str = ""
    created_at: str | None = None
    elderly: bool = False
    child_present: bool = False
    injury: bool = False
    oxygen_required: bool = False
    shelter_needed: bool = False
    food_needed: bool = False
    transport_needed: bool = False
    preferred_language: str = ""
    emergency_contact: EmergencyContactResponse | None = None
