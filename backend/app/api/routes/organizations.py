"""Organization operations — institutional response (Neo4j-backed)."""

from __future__ import annotations

from fastapi import APIRouter

from app.models.organization_models import (
    AcceptIncidentBody,
    CapacityUpdateRequest,
    OrganizationIncidentItem,
    OrganizationOverviewResponse,
    UpdateResponseStatusBody,
)
from app.services import organization_service

router = APIRouter(prefix="/organizations", tags=["organizations"])


@router.get("/{organization_id}/overview", response_model=OrganizationOverviewResponse)
def get_org_overview(organization_id: str) -> OrganizationOverviewResponse:
    return organization_service.get_overview(organization_id)


@router.get("/{organization_id}/incidents", response_model=list[OrganizationIncidentItem])
def list_org_incidents(organization_id: str) -> list[OrganizationIncidentItem]:
    return organization_service.list_incidents(organization_id)


@router.post("/{organization_id}/capacity-update")
def post_capacity_update(organization_id: str, body: CapacityUpdateRequest) -> dict:
    return organization_service.update_capacity(organization_id, body)


@router.post("/{organization_id}/accept-incident")
def post_accept_incident(organization_id: str, body: AcceptIncidentBody) -> dict:
    return organization_service.accept_incident(organization_id, body)


@router.post("/{organization_id}/update-response-status")
def post_update_response_status(organization_id: str, body: UpdateResponseStatusBody) -> dict:
    return organization_service.update_response_status(organization_id, body)
