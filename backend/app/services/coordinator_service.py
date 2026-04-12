"""Coordinator mutations on incidents — Neo4j-backed."""

from __future__ import annotations

from typing import Any

from fastapi import HTTPException

from app.core.config import get_settings
from app.core.neo4j_client import get_driver, managed_neo4j_session
from app.db.queries import coordinator_queries as cq
from app.models.volunteer_task_requests import CoordinatorIncidentActionResponse


def _node_props(node: Any) -> dict[str, Any]:
    if node is None:
        return {}
    if hasattr(node, "items"):
        return dict(node)  # type: ignore[arg-type]
    return {}


def reassign_incident(*, incident_id: str, new_volunteer_id: str) -> CoordinatorIncidentActionResponse:
    driver = get_driver()
    settings = get_settings()

    def write(tx: Any) -> dict[str, Any] | None:
        rec = tx.run(cq.REASSIGN_INCIDENT, incident_id=incident_id, new_volunteer_id=new_volunteer_id).single()
        if rec is None:
            return None
        p = _node_props(rec["incident"])
        return {
            "incident_id": str(p.get("id", incident_id)),
            "status": str(p.get("status", "assigned")),
            "route_status": str(p.get("route_status")) if p.get("route_status") is not None else None,
        }

    with managed_neo4j_session(driver, settings) as session:
        row = session.execute_write(write)
    if row is None:
        raise HTTPException(status_code=404, detail="Incident or volunteer not found.")
    return CoordinatorIncidentActionResponse(**row)


def escalate_incident(*, incident_id: str, note: str = "") -> CoordinatorIncidentActionResponse:
    driver = get_driver()
    settings = get_settings()

    def write(tx: Any) -> dict[str, Any] | None:
        rec = tx.run(cq.ESCALATE_INCIDENT, incident_id=incident_id, note=note).single()
        if rec is None:
            return None
        p = _node_props(rec["incident"])
        return {
            "incident_id": str(p.get("id", incident_id)),
            "status": str(p.get("status", "escalated")),
            "route_status": str(p.get("route_status")) if p.get("route_status") is not None else None,
        }

    with managed_neo4j_session(driver, settings) as session:
        row = session.execute_write(write)
    if row is None:
        raise HTTPException(status_code=404, detail="Incident not found.")
    return CoordinatorIncidentActionResponse(**row)


def block_route(*, incident_id: str, reason: str = "") -> CoordinatorIncidentActionResponse:
    driver = get_driver()
    settings = get_settings()

    def write(tx: Any) -> dict[str, Any] | None:
        rec = tx.run(cq.BLOCK_ROUTE, incident_id=incident_id, reason=reason).single()
        if rec is None:
            return None
        p = _node_props(rec["incident"])
        return {
            "incident_id": str(p.get("id", incident_id)),
            "status": str(p.get("status", "open")),
            "route_status": str(p.get("route_status", "blocked")),
        }

    with managed_neo4j_session(driver, settings) as session:
        row = session.execute_write(write)
    if row is None:
        raise HTTPException(status_code=404, detail="Incident not found.")
    return CoordinatorIncidentActionResponse(**row)
