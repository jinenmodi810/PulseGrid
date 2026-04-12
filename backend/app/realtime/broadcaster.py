"""Fire-and-forget JSON events to WebSocket channels after successful Neo4j writes."""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from typing import Any

from app.models.incident_requests import CreateIncidentResponse
from app.services import graph_matching_service
from app.models.volunteer_task_requests import (
    AcceptTaskResponse,
    CompleteTaskResponse,
    CoordinatorIncidentActionResponse,
)
from app.realtime.connection_manager import connection_manager as ws_connections
from app.realtime import event_types as E


def _ts() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _payload(**fields: Any) -> dict[str, Any]:
    out: dict[str, Any] = {"timestamp": _ts()}
    out.update({k: v for k, v in fields.items() if v is not None})
    return out


async def broadcast_dashboard_updated() -> None:
    await ws_connections.broadcast_json(
        "dashboard",
        _payload(event=E.DASHBOARD_UPDATED),
    )


async def broadcast_incident_update(incident_id: str, payload: dict[str, Any]) -> None:
    body = _payload(**payload)
    if "incident_id" not in body and incident_id:
        body["incident_id"] = incident_id
    await ws_connections.broadcast_json(f"incident:{incident_id}", body)


async def broadcast_volunteer_update(volunteer_id: str, payload: dict[str, Any]) -> None:
    body = _payload(**payload)
    if "volunteer_id" not in body and volunteer_id:
        body["volunteer_id"] = volunteer_id
    await ws_connections.broadcast_json(f"volunteer:{volunteer_id}", body)


async def broadcast_organization_update(organization_id: str, payload: dict[str, Any]) -> None:
    body = _payload(**payload)
    if "organization_id" not in body and organization_id:
        body["organization_id"] = organization_id
    await ws_connections.broadcast_json(f"organization:{organization_id}", body)


async def after_incident_created(resp: CreateIncidentResponse) -> None:
    iid = resp.incident_id
    common = dict(
        event=E.INCIDENT_CREATED,
        incident_id=iid,
        status=resp.status,
        priority_label=resp.priority_label,
        response_tier=resp.response_tier,
        decision_summary=resp.decision_summary,
    )
    await ws_connections.broadcast_json("dashboard", _payload(**common))
    await broadcast_incident_update(iid, common)
    helper = resp.assigned_helper
    if helper and helper.get("id"):
        vid = str(helper["id"])
        assigned = dict(
            event=E.INCIDENT_ASSIGNED,
            incident_id=iid,
            volunteer_id=vid,
            status=resp.status,
            priority_label=resp.priority_label,
        )
        await ws_connections.broadcast_json("dashboard", _payload(**assigned))
        await broadcast_volunteer_update(vid, assigned)

    org = resp.assigned_organization
    if org and org.get("id"):
        oid = str(org["id"])
        org_evt = dict(
            event=E.INCIDENT_CREATED,
            incident_id=iid,
            organization_id=oid,
            status=resp.status,
            priority_label=resp.priority_label,
            response_tier=resp.response_tier,
            decision_summary=resp.decision_summary,
        )
        await broadcast_organization_update(oid, org_evt)

    if (
        resp.volunteer_candidate_allowed
        and resp.zone_id
        and not (helper or {}).get("id")
    ):
        zone_evt = dict(
            event=E.INCIDENT_OPEN_IN_ZONE,
            incident_id=iid,
            zone_id=resp.zone_id,
            status=resp.status,
            priority_label=resp.priority_label,
            response_tier=resp.response_tier,
        )
        body = _payload(**zone_evt)
        ids = await asyncio.to_thread(graph_matching_service.list_volunteer_ids_in_zone_sync, resp.zone_id)
        for vid in ids:
            await ws_connections.broadcast_json(f"volunteer:{vid}", body)

    await broadcast_dashboard_updated()


async def after_incident_accepted(*, volunteer_id: str, resp: AcceptTaskResponse) -> None:
    iid = resp.incident_id
    p = dict(
        event=E.INCIDENT_ACCEPTED,
        incident_id=iid,
        volunteer_id=volunteer_id,
        status=resp.status,
        priority_label=resp.priority_label,
    )
    await ws_connections.broadcast_json("dashboard", _payload(**p))
    await broadcast_incident_update(iid, p)
    await broadcast_volunteer_update(volunteer_id, p)
    await broadcast_dashboard_updated()


async def after_incident_completed(*, volunteer_id: str, resp: CompleteTaskResponse) -> None:
    iid = resp.incident_id
    credits = resp.volunteer.credits
    done = dict(
        event=E.INCIDENT_COMPLETED,
        incident_id=iid,
        volunteer_id=volunteer_id,
        status=resp.status,
        credits=credits,
    )
    credits_evt = dict(
        event=E.VOLUNTEER_CREDITS_UPDATED,
        incident_id=iid,
        volunteer_id=volunteer_id,
        status=resp.status,
        credits=credits,
    )
    await ws_connections.broadcast_json("dashboard", _payload(**done))
    await broadcast_incident_update(iid, done)
    await broadcast_volunteer_update(volunteer_id, done)
    await broadcast_volunteer_update(volunteer_id, credits_evt)
    await broadcast_dashboard_updated()


async def after_incident_reassigned(*, incident_id: str, new_volunteer_id: str, resp: CoordinatorIncidentActionResponse) -> None:
    p = dict(
        event=E.INCIDENT_ASSIGNED,
        incident_id=incident_id,
        volunteer_id=new_volunteer_id,
        status=resp.status,
    )
    await ws_connections.broadcast_json("dashboard", _payload(**p))
    await broadcast_incident_update(incident_id, p)
    await broadcast_volunteer_update(new_volunteer_id, p)
    await broadcast_dashboard_updated()


async def after_incident_escalated(*, incident_id: str, resp: CoordinatorIncidentActionResponse) -> None:
    p = dict(
        event=E.INCIDENT_ESCALATED,
        incident_id=incident_id,
        status=resp.status,
    )
    await ws_connections.broadcast_json("dashboard", _payload(**p))
    await broadcast_incident_update(incident_id, p)
    await broadcast_dashboard_updated()


async def after_route_blocked(*, incident_id: str, resp: CoordinatorIncidentActionResponse) -> None:
    p = dict(
        event=E.ROUTE_BLOCKED,
        incident_id=incident_id,
        status=resp.status,
        route_status=resp.route_status,
    )
    await ws_connections.broadcast_json("dashboard", _payload(**p))
    await broadcast_incident_update(incident_id, p)
    await broadcast_dashboard_updated()
