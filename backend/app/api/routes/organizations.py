"""Organization operations — institutional response (Neo4j-backed)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from app.api.deps.auth_deps import auth_principal, require_role
from app.api.deps.db_deps import get_db, get_db_optional
from app.models.organization_models import (
    AcceptIncidentBody,
    CapacityUpdateRequest,
    OrganizationIncidentItem,
    OrganizationOverviewResponse,
    UpdateResponseStatusBody,
)
from sqlalchemy.orm import Session

from app.services import organization_service

router = APIRouter(prefix="/organizations", tags=["organizations"])


@router.get("/{organization_id}/overview", response_model=OrganizationOverviewResponse)
def get_org_overview(
    organization_id: str,
    principal: dict[str, str] = Depends(auth_principal),
    db: Session | None = Depends(get_db_optional),
) -> OrganizationOverviewResponse:
    require_role(principal, "organization")
    if str(principal.get("sub") or "").strip() != str(organization_id).strip():
        raise HTTPException(status_code=403, detail="Organization id does not match session.")
    return organization_service.get_overview(organization_id, db)


@router.get("/{organization_id}/incidents", response_model=list[OrganizationIncidentItem])
def list_org_incidents(
    organization_id: str,
    principal: dict[str, str] = Depends(auth_principal),
    db: Session | None = Depends(get_db_optional),
) -> list[OrganizationIncidentItem]:
    require_role(principal, "organization")
    if str(principal.get("sub") or "").strip() != str(organization_id).strip():
        raise HTTPException(status_code=403, detail="Organization id does not match session.")
    return organization_service.list_incidents(organization_id, db)


@router.post("/{organization_id}/capacity-update")
def post_capacity_update(
    organization_id: str,
    body: CapacityUpdateRequest,
    principal: dict[str, str] = Depends(auth_principal),
    db: Session = Depends(get_db),
) -> dict:
    """Capacity is canonical in PostgreSQL; Neo4j is re-projected for graph/matching."""
    require_role(principal, "organization")
    if str(principal.get("sub") or "").strip() != str(organization_id).strip():
        raise HTTPException(status_code=403, detail="Organization id does not match session.")
    return organization_service.update_capacity(organization_id, body, db)


@router.post("/{organization_id}/accept-incident")
def post_accept_incident(
    organization_id: str,
    body: AcceptIncidentBody,
    principal: dict[str, str] = Depends(auth_principal),
    db: Session | None = Depends(get_db_optional),
) -> dict:
    require_role(principal, "organization")
    if str(principal.get("sub") or "").strip() != str(organization_id).strip():
        raise HTTPException(status_code=403, detail="Organization id does not match session.")
    return organization_service.accept_incident(organization_id, body, db)


@router.post("/{organization_id}/update-response-status")
def post_update_response_status(
    organization_id: str,
    body: UpdateResponseStatusBody,
    principal: dict[str, str] = Depends(auth_principal),
    db: Session | None = Depends(get_db_optional),
) -> dict:
    require_role(principal, "organization")
    if str(principal.get("sub") or "").strip() != str(organization_id).strip():
        raise HTTPException(status_code=403, detail="Organization id does not match session.")
    return organization_service.update_response_status(organization_id, body, db)
