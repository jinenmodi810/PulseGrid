"""Admin inspection API (hackathon session header). TODO: JWT + RBAC."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException

from app.core.config import get_settings
from app.models.admin_inspection_models import (
    AdminAssignmentItem,
    AdminIncidentDetailResponse,
    AdminIncidentItem,
    AdminOverviewResponse,
    AdminRewardItem,
    AdminSupportNetworkResponse,
    AdminUserItem,
    AdminVolunteerItem,
)
from app.services import admin_inspection_service


def require_admin_session(
    x_admin_session: Annotated[str | None, Header(alias="X-Admin-Session")] = None,
) -> None:
    """Gate admin reads with the same marker issued by POST /auth/admin-login."""
    settings = get_settings()
    # TODO(Phase1): Replace header marker with Bearer JWT and scoped admin claims.
    expected = (settings.ADMIN_SESSION_MARKER or "").strip()
    got = (x_admin_session or "").strip()
    if not expected or got != expected:
        raise HTTPException(status_code=401, detail="Admin session required.")


router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(require_admin_session)],
)


@router.get("/ping")
def admin_ping() -> dict[str, bool | str]:
    """Minimal check that routing + session guard work (no Neo4j)."""
    return {"ok": True, "guard": "passed"}


@router.get("/overview", response_model=AdminOverviewResponse)
def get_overview() -> AdminOverviewResponse:
    return admin_inspection_service.get_overview()


@router.get("/users", response_model=list[AdminUserItem])
def get_users() -> list[AdminUserItem]:
    return admin_inspection_service.list_users()


@router.get("/volunteers", response_model=list[AdminVolunteerItem])
def get_volunteers() -> list[AdminVolunteerItem]:
    return admin_inspection_service.list_volunteers()


@router.get("/incidents", response_model=list[AdminIncidentItem])
def get_incidents() -> list[AdminIncidentItem]:
    return admin_inspection_service.list_incidents()


@router.get("/incidents/{incident_id}", response_model=AdminIncidentDetailResponse)
def get_incident(incident_id: str) -> AdminIncidentDetailResponse:
    detail = admin_inspection_service.get_incident_detail(incident_id)
    if detail is None:
        raise HTTPException(status_code=404, detail="Incident not found.")
    return detail


@router.get("/assignments", response_model=list[AdminAssignmentItem])
def get_assignments() -> list[AdminAssignmentItem]:
    return admin_inspection_service.list_assignments()


@router.get("/rewards", response_model=list[AdminRewardItem])
def get_rewards() -> list[AdminRewardItem]:
    return admin_inspection_service.list_rewards()


@router.get("/support-network", response_model=AdminSupportNetworkResponse)
def get_support_network() -> AdminSupportNetworkResponse:
    return admin_inspection_service.get_support_network()
