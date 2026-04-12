"""API contracts for Gemini-backed guidance (explanation layer only — not operational truth)."""

from __future__ import annotations

from pydantic import BaseModel, Field


class GuidanceResponse(BaseModel):
    """Single guidance or summary message returned to clients."""

    role: str = Field(..., description="affected_user | volunteer | coordinator")
    language: str = Field(default="en", description="Effective language tag for the message")
    message: str = Field(..., description="Human-readable guidance or summary")
    fallback_used: bool = Field(default=False, description="True when template text was used instead of Gemini")
    generated_at: str | None = Field(default=None, description="ISO-8601 timestamp when generated")


class AffectedUserGuidanceRequest(BaseModel):
    """Server loads incident + reporter context from Neo4j; only incident_id is required from clients."""

    incident_id: str = Field(..., min_length=1)


class VolunteerGuidanceRequest(BaseModel):
    incident_id: str = Field(..., min_length=1)
    volunteer_id: str | None = Field(
        default=None,
        description="Optional; when omitted, assigned volunteer from graph is used if present.",
    )


class CoordinatorSummaryRequest(BaseModel):
    incident_id: str = Field(..., min_length=1)


class IncidentGuidanceBundleResponse(BaseModel):
    """Convenience GET payload for mobile clients."""

    incident_id: str
    affected_user: GuidanceResponse
    coordinator_summary: GuidanceResponse | None = None
