"""Organization-scoped operations (incidents, capacity) — Neo4j."""

from __future__ import annotations

from typing import Any

from fastapi import HTTPException

from app.core.config import get_settings
from app.core.neo4j_client import get_driver, managed_neo4j_session
from app.db.queries import organization_queries as oq
from app.models.organization_models import (
    AcceptIncidentBody,
    CapacityUpdateRequest,
    OrganizationIncidentItem,
    OrganizationOverviewResponse,
    UpdateResponseStatusBody,
)


def _node_to_dict(node: Any) -> dict[str, Any]:
    if node is None:
        return {}
    if hasattr(node, "items"):
        return dict(node)
    return {}


def _org_props(tx: Any, org_id: str) -> dict[str, Any] | None:
    rec = tx.run(oq.GET_ORGANIZATION, org_id=org_id).single()
    if rec is None or rec.get("o") is None:
        return None
    return _node_to_dict(rec["o"])


def get_overview(org_id: str) -> OrganizationOverviewResponse:
    driver = get_driver()
    settings = get_settings()

    def read(tx: Any) -> OrganizationOverviewResponse | None:
        props = _org_props(tx, org_id)
        if props is None:
            return None
        c = tx.run(oq.COUNT_ORG_INCIDENTS, org_id=org_id).single()
        open_n = int(c["c"]) if c and c.get("c") is not None else 0
        cap_keys = (
            "beds_available",
            "oxygen_units",
            "ambulances_available",
            "shelter_units",
            "food_capacity_units",
            "rescue_units",
        )
        capacity = {k: props[k] for k in cap_keys if k in props and props[k] is not None}
        return OrganizationOverviewResponse(
            organization_id=str(props.get("id", org_id)),
            name=str(props.get("name", "")),
            org_type=str(props.get("org_type", "")),
            zone_id=str(props.get("zone_id", "")),
            active=bool(props.get("active", True)),
            assigned_incidents_open=open_n,
            capacity=capacity,
        )

    with managed_neo4j_session(driver, settings) as session:
        out = session.execute_read(read)
    if out is None:
        raise HTTPException(status_code=404, detail="Organization not found.")
    return out


def list_incidents(org_id: str) -> list[OrganizationIncidentItem]:
    driver = get_driver()
    settings = get_settings()

    def read(tx: Any) -> list[OrganizationIncidentItem] | None:
        if _org_props(tx, org_id) is None:
            return None
        rows = [dict(r) for r in tx.run(oq.LIST_ORGAN_INCIDENTS, org_id=org_id)]
        out: list[OrganizationIncidentItem] = []
        for r in rows:
            out.append(
                OrganizationIncidentItem(
                    incident_id=str(r.get("incident_id", "")),
                    incident_type=str(r.get("incident_type", "")),
                    severity=str(r.get("severity", "medium")),
                    status=str(r.get("status", "open")),
                    priority_label=str(r.get("priority_label", "MEDIUM")),
                    priority_score=float(r.get("priority_score") or 0),
                    zone_id=str(r.get("zone_id", "")),
                    assigned_volunteer_name=str(r.get("assigned_volunteer_name", "")),
                    response_tier=str(r.get("response_tier", "")),
                    escalation_required=bool(r.get("escalation_required", False)),
                    decision_summary=str(r.get("decision_summary", "")),
                    volunteer_support_active=bool(r.get("volunteer_support_active", False)),
                    created_at=str(r["created_at"]) if r.get("created_at") is not None else None,
                )
            )
        return out

    with managed_neo4j_session(driver, settings) as session:
        out = session.execute_read(read)
    if out is None:
        raise HTTPException(status_code=404, detail="Organization not found.")
    return out


def update_capacity(org_id: str, body: CapacityUpdateRequest) -> dict[str, Any]:
    props = body.model_dump(exclude_none=True)
    if not props:
        return {"ok": True, "updated": {}}
    driver = get_driver()
    settings = get_settings()

    def write(tx: Any) -> dict[str, Any]:
        if _org_props(tx, org_id) is None:
            raise HTTPException(status_code=404, detail="Organization not found.")
        tx.run(oq.SET_ORGAN_CAPACITY, org_id=org_id, props=props)
        return {"ok": True, "updated": props}

    with managed_neo4j_session(driver, settings) as session:
        return session.execute_write(write)


def accept_incident(org_id: str, body: AcceptIncidentBody) -> dict[str, Any]:
    driver = get_driver()
    settings = get_settings()

    def write(tx: Any) -> dict[str, Any]:
        if _org_props(tx, org_id) is None:
            raise HTTPException(status_code=404, detail="Organization not found.")
        rec = tx.run(
            oq.ACCEPT_ORG_INCIDENT,
            org_id=org_id,
            incident_id=body.incident_id,
        ).single()
        if rec is None:
            raise HTTPException(status_code=404, detail="Incident not assigned to this organization.")
        return {"ok": True, "incident_id": rec.get("incident_id"), "status": rec.get("status")}

    with managed_neo4j_session(driver, settings) as session:
        return session.execute_write(write)


def update_response_status(org_id: str, body: UpdateResponseStatusBody) -> dict[str, Any]:
    driver = get_driver()
    settings = get_settings()

    def write(tx: Any) -> dict[str, Any]:
        if _org_props(tx, org_id) is None:
            raise HTTPException(status_code=404, detail="Organization not found.")
        rec = tx.run(
            oq.UPDATE_ORG_RESPONSE_STATUS,
            org_id=org_id,
            incident_id=body.incident_id,
            status=body.status.strip(),
        ).single()
        if rec is None:
            raise HTTPException(status_code=404, detail="Incident not found for organization.")
        return {
            "ok": True,
            "incident_id": rec.get("incident_id"),
            "organization_response_status": rec.get("organization_response_status"),
        }

    with managed_neo4j_session(driver, settings) as session:
        return session.execute_write(write)
