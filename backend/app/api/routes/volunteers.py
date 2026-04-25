"""Volunteer endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from app.api.deps.auth_deps import auth_principal, require_role
from app.models.volunteer import VolunteerRead
from app.models.volunteer_task_requests import VolunteerTaskItem
from app.services import volunteer_task_service

router = APIRouter(prefix="/volunteers", tags=["volunteers"])


def _coerce_str_list(val: object) -> list[str]:
    if val is None:
        return []
    if isinstance(val, list):
        return [str(x) for x in val if x is not None and str(x).strip()]
    return [str(val)] if str(val).strip() else []


def _to_volunteer_read(row: dict) -> VolunteerRead:
    skills = _coerce_str_list(row.get("skills"))
    sk = str(row.get("skill_type") or "").strip()
    if not skills and sk:
        skills = [sk]
    if not skills:
        skills = ["general"]
    trust = float(row.get("trust_score") or 0.5)
    trust = max(0.0, min(1.0, trust))
    return VolunteerRead(
        id=str(row.get("id", "")),
        display_name=str(row.get("display_name", "")),
        skills=skills,
        credits=int(row.get("credits") or 0),
        trust_score=trust,
        zone_id=str(row.get("zone_id") or ""),
        skill_type=sk,
        support_types=_coerce_str_list(row.get("support_types")) or ["general_support"],
        languages=_coerce_str_list(row.get("languages")) or ["en"],
        transport_access=str(row.get("transport_access") or ""),
        availability=str(row.get("availability") or ""),
    )


@router.get("/", response_model=list[VolunteerRead])
def list_volunteers(principal: dict[str, str] = Depends(auth_principal)) -> list[VolunteerRead]:
    require_role(principal, "volunteer", "organization", "victim")
    try:
        rows = volunteer_task_service.list_volunteers_brief_rows()
        return [_to_volunteer_read(r) for r in rows]
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/{volunteer_id}/tasks", response_model=list[VolunteerTaskItem])
def get_volunteer_tasks(volunteer_id: str, principal: dict[str, str] = Depends(auth_principal)) -> list[VolunteerTaskItem]:
    require_role(principal, "volunteer")
    if str(principal.get("sub") or "").strip() != str(volunteer_id).strip():
        raise HTTPException(status_code=403, detail="Volunteer id does not match session.")
    try:
        return volunteer_task_service.list_volunteer_tasks(volunteer_id)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/{volunteer_id}", response_model=VolunteerRead)
def get_volunteer(volunteer_id: str, principal: dict[str, str] = Depends(auth_principal)) -> VolunteerRead:
    require_role(principal, "volunteer")
    if str(principal.get("sub") or "").strip() != str(volunteer_id).strip():
        raise HTTPException(status_code=403, detail="Volunteer id does not match session.")
    row = volunteer_task_service.get_volunteer_row(volunteer_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Volunteer not found")
    return _to_volunteer_read(row)
