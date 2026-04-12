"""AI guidance endpoints — Gemini explains; Neo4j + services own operational truth."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from app.models.ai_guidance_models import (
    AffectedUserGuidanceRequest,
    CoordinatorSummaryRequest,
    GuidanceResponse,
    IncidentGuidanceBundleResponse,
    VolunteerGuidanceRequest,
)
from app.services import ai_guidance_service

router = APIRouter(prefix="/ai", tags=["ai"])


@router.post("/guidance/affected-user", response_model=GuidanceResponse)
def post_affected_user_guidance(body: AffectedUserGuidanceRequest) -> GuidanceResponse:
    return ai_guidance_service.generate_affected_user_guidance(body)


@router.post("/guidance/volunteer", response_model=GuidanceResponse)
def post_volunteer_guidance(body: VolunteerGuidanceRequest) -> GuidanceResponse:
    return ai_guidance_service.generate_volunteer_guidance(body)


@router.post("/guidance/coordinator-summary", response_model=GuidanceResponse)
def post_coordinator_summary(body: CoordinatorSummaryRequest) -> GuidanceResponse:
    return ai_guidance_service.generate_coordinator_summary(body)


@router.get("/incidents/{incident_id}/guidance", response_model=IncidentGuidanceBundleResponse)
def get_incident_guidance(
    incident_id: str,
    include_coordinator: bool = Query(default=False, description="Also generate coordinator triage summary"),
) -> IncidentGuidanceBundleResponse:
    # TODO: optional Redis / Incident node cache with websocket invalidation.
    bundle = ai_guidance_service.get_incident_guidance_bundle(
        incident_id=incident_id,
        include_coordinator=include_coordinator,
    )
    if bundle is None:
        raise HTTPException(status_code=404, detail="Incident not found.")
    return bundle
