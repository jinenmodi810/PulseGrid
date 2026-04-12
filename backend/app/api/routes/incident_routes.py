"""Incident lifecycle: preview, create, read, list."""

from __future__ import annotations

from fastapi import APIRouter, BackgroundTasks, HTTPException

from app.models.incident import IncidentRead
from app.models.incident_requests import (
    CreateIncidentRequest,
    CreateIncidentResponse,
    IncidentDetailResponse,
    PriorityPreviewRequest,
    PriorityPreviewResponse,
)
from app.models.voice_sos_intake import VoiceSosIntakePreviewResponse
from app.models.volunteer_task_requests import (
    AcceptTaskResponse,
    CompleteTaskResponse,
    CoordinatorIncidentActionResponse,
    CoordinatorNoteRequest,
    ReassignRequest,
    VolunteerIdBody,
)
from app.realtime import broadcaster
from app.services import coordinator_service, incident_service, volunteer_task_service

router = APIRouter(prefix="/incidents", tags=["incidents"])


@router.post("/preview-priority", response_model=PriorityPreviewResponse)
def post_preview_priority(body: PriorityPreviewRequest) -> PriorityPreviewResponse:
    return incident_service.preview_priority(body)


@router.post("/voice-intake/preview", response_model=VoiceSosIntakePreviewResponse)
def post_voice_intake_preview() -> VoiceSosIntakePreviewResponse:
    """TODO(voice): Accept audio/transcript; return VoiceSosIntakeStub for confirmation before POST /incidents."""
    return VoiceSosIntakePreviewResponse()


@router.post("/", response_model=CreateIncidentResponse, status_code=201)
async def post_create_incident(
    body: CreateIncidentRequest,
    background_tasks: BackgroundTasks,
) -> CreateIncidentResponse:
    try:
        resp = incident_service.create_incident(body)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    background_tasks.add_task(broadcaster.after_incident_created, resp)
    return resp


@router.get("/{incident_id}", response_model=IncidentDetailResponse)
def get_incident(incident_id: str) -> IncidentDetailResponse:
    detail = incident_service.get_incident_detail(incident_id)
    if detail is None:
        raise HTTPException(status_code=404, detail="Incident not found")
    return detail


@router.post("/{incident_id}/accept", response_model=AcceptTaskResponse)
async def post_accept_task(
    incident_id: str,
    body: VolunteerIdBody,
    background_tasks: BackgroundTasks,
) -> AcceptTaskResponse:
    try:
        resp = volunteer_task_service.accept_task(volunteer_id=body.volunteer_id, incident_id=incident_id)
    except HTTPException:
        raise
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    background_tasks.add_task(broadcaster.after_incident_accepted, volunteer_id=body.volunteer_id, resp=resp)
    return resp


@router.post("/{incident_id}/complete", response_model=CompleteTaskResponse)
async def post_complete_task(
    incident_id: str,
    body: VolunteerIdBody,
    background_tasks: BackgroundTasks,
) -> CompleteTaskResponse:
    try:
        resp = volunteer_task_service.complete_task(volunteer_id=body.volunteer_id, incident_id=incident_id)
    except HTTPException:
        raise
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    background_tasks.add_task(broadcaster.after_incident_completed, volunteer_id=body.volunteer_id, resp=resp)
    return resp


@router.post("/{incident_id}/reassign", response_model=CoordinatorIncidentActionResponse)
async def post_reassign(
    incident_id: str,
    body: ReassignRequest,
    background_tasks: BackgroundTasks,
) -> CoordinatorIncidentActionResponse:
    try:
        resp = coordinator_service.reassign_incident(incident_id=incident_id, new_volunteer_id=body.new_volunteer_id)
    except HTTPException:
        raise
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    background_tasks.add_task(
        broadcaster.after_incident_reassigned,
        incident_id=incident_id,
        new_volunteer_id=body.new_volunteer_id,
        resp=resp,
    )
    return resp


@router.post("/{incident_id}/escalate", response_model=CoordinatorIncidentActionResponse)
async def post_escalate(
    incident_id: str,
    background_tasks: BackgroundTasks,
    body: CoordinatorNoteRequest = CoordinatorNoteRequest(),
) -> CoordinatorIncidentActionResponse:
    note = body.note
    try:
        resp = coordinator_service.escalate_incident(incident_id=incident_id, note=note)
    except HTTPException:
        raise
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    background_tasks.add_task(broadcaster.after_incident_escalated, incident_id=incident_id, resp=resp)
    return resp


@router.post("/{incident_id}/block-route", response_model=CoordinatorIncidentActionResponse)
async def post_block_route(
    incident_id: str,
    background_tasks: BackgroundTasks,
    body: CoordinatorNoteRequest = CoordinatorNoteRequest(),
) -> CoordinatorIncidentActionResponse:
    reason = body.note
    try:
        resp = coordinator_service.block_route(incident_id=incident_id, reason=reason)
    except HTTPException:
        raise
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    background_tasks.add_task(broadcaster.after_route_blocked, incident_id=incident_id, resp=resp)
    return resp


@router.get("/", response_model=list[IncidentRead])
def list_incidents() -> list[IncidentRead]:
    rows = incident_service.list_incidents()
    out: list[IncidentRead] = []
    for r in rows:
        created = r.get("created_at")
        if hasattr(created, "isoformat"):
            created = created.isoformat()
        elif created is not None:
            created = str(created)
        out.append(
            IncidentRead(
                id=str(r.get("id", "")),
                title=str(r.get("title", "Incident")),
                status=str(r.get("status", "open")),
                severity=str(r.get("severity", "medium")),
                created_at=created,
            )
        )
    return out
