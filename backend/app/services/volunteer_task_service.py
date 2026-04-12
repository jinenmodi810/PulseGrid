"""Volunteer task list, accept, and complete — Neo4j-backed."""

from __future__ import annotations

from typing import Any

from fastapi import HTTPException

from app.core.config import get_settings
from app.core.neo4j_client import get_driver, managed_neo4j_session
from app.db.queries import volunteer_task_queries as vtq
from app.models.volunteer_task_requests import (
    AcceptTaskResponse,
    CompleteTaskResponse,
    VolunteerRewardSnapshot,
    VolunteerTaskItem,
)


def _node_props(node: Any) -> dict[str, Any]:
    if node is None:
        return {}
    if hasattr(node, "items"):
        return dict(node)  # type: ignore[arg-type]
    return {}


def _row_to_task(incident: Any, zone_id: str, task_source: str) -> VolunteerTaskItem:
    p = _node_props(incident)
    iid = str(p.get("id", ""))
    return VolunteerTaskItem(
        incident_id=iid,
        incident_type=str(p.get("incident_type", "") or p.get("title", "Incident")),
        priority_label=str(p.get("priority_label", "MEDIUM")),
        priority_score=float(p.get("priority_score") or 0),
        zone_id=zone_id or str(p.get("zone_id", "")),
        status=str(p.get("status", "open")),
        note=str(p.get("note", "")),
        eta_minutes=int(p["eta_minutes"]) if p.get("eta_minutes") is not None else None,
        route_status=str(p.get("route_status", "pending")),
        shelter_needed=bool(p.get("shelter_needed", False)),
        food_needed=bool(p.get("food_needed", False)),
        transport_needed=bool(p.get("transport_needed", False)),
        elderly=bool(p.get("elderly", False)),
        child_present=bool(p.get("child_present", False)),
        injury=bool(p.get("injury", False)),
        oxygen_required=bool(p.get("oxygen_required", False)),
        task_source=task_source,
        response_tier=str(p.get("response_tier", "") or ""),
        decision_summary=str(p.get("decision_summary", "") or "")[:400],
    )


def list_volunteer_tasks(volunteer_id: str) -> list[VolunteerTaskItem]:
    driver = get_driver()
    settings = get_settings()

    def read(tx: Any) -> list[VolunteerTaskItem]:
        assigned = [
            _row_to_task(rec["incident"], str(rec.get("zone_id") or ""), str(rec.get("task_source") or "assigned"))
            for rec in tx.run(vtq.LIST_ASSIGNED_TASKS, volunteer_id=volunteer_id)
        ]
        nearby = [
            _row_to_task(rec["incident"], str(rec.get("zone_id") or ""), str(rec.get("task_source") or "nearby_open"))
            for rec in tx.run(vtq.LIST_NEARBY_OPEN_TASKS, volunteer_id=volunteer_id)
        ]
        by_id: dict[str, VolunteerTaskItem] = {}
        for t in assigned:
            by_id[t.incident_id] = t
        for t in nearby:
            if t.incident_id not in by_id:
                by_id[t.incident_id] = t
        out = list(by_id.values())
        out.sort(key=lambda x: (-x.priority_score, x.incident_id))
        return out

    with managed_neo4j_session(driver, settings) as session:
        return session.execute_read(read)


def accept_task(*, volunteer_id: str, incident_id: str) -> AcceptTaskResponse:
    driver = get_driver()
    settings = get_settings()

    def write(tx: Any) -> dict[str, Any] | None:
        rec = tx.run(vtq.ACCEPT_TASK, volunteer_id=volunteer_id, incident_id=incident_id).single()
        if rec is None:
            return None
        p = _node_props(rec["incident"])
        return {
            "incident_id": str(p.get("id", incident_id)),
            "status": str(p.get("status", "accepted")),
            "priority_label": str(p.get("priority_label", "")),
            "zone_id": str(p.get("zone_id", "")),
        }

    with managed_neo4j_session(driver, settings) as session:
        row = session.execute_write(write)
    if row is None:
        raise HTTPException(status_code=400, detail="Cannot accept this task for this volunteer.")
    return AcceptTaskResponse(**row)


def complete_task(*, volunteer_id: str, incident_id: str) -> CompleteTaskResponse:
    driver = get_driver()
    settings = get_settings()

    def write(tx: Any) -> dict[str, Any] | None:
        rec = tx.run(vtq.COMPLETE_TASK, volunteer_id=volunteer_id, incident_id=incident_id).single()
        if rec is None:
            return None
        p = _node_props(rec["incident"])
        return {
            "incident_id": str(p.get("id", incident_id)),
            "status": str(p.get("status", "resolved")),
            "volunteer_id": str(rec.get("volunteer_id", volunteer_id)),
            "credits": int(rec.get("credits") or 0),
            "trust_score": float(rec.get("trust_score") or 0),
        }

    with managed_neo4j_session(driver, settings) as session:
        row = session.execute_write(write)
    if row is None:
        raise HTTPException(status_code=400, detail="Cannot complete this task (check assignment or already resolved).")
    snap = VolunteerRewardSnapshot(
        volunteer_id=row["volunteer_id"],
        credits=row["credits"],
        trust_score=row["trust_score"],
    )
    return CompleteTaskResponse(incident_id=row["incident_id"], status=row["status"], volunteer=snap)


def get_volunteer_row(volunteer_id: str) -> dict[str, Any] | None:
    driver = get_driver()
    settings = get_settings()

    def read(tx: Any) -> dict[str, Any] | None:
        rec = tx.run(vtq.GET_VOLUNTEER_PROPS, volunteer_id=volunteer_id).single()
        return dict(rec) if rec else None

    with managed_neo4j_session(driver, settings) as session:
        return session.execute_read(read)


def list_volunteers_brief_rows() -> list[dict[str, Any]]:
    driver = get_driver()
    settings = get_settings()

    def read(tx: Any) -> list[dict[str, Any]]:
        return [dict(r) for r in tx.run(vtq.LIST_VOLUNTEERS_BRIEF)]

    with managed_neo4j_session(driver, settings) as session:
        return session.execute_read(read)
