"""Organization-scoped operations: PostgreSQL for canonical org profile/capacity; Neo4j for incidents + graph."""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import Any

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.neo4j_client import get_driver, managed_neo4j_session
from app.db.queries import organization_queries as oq
from app.db.sql.models.organization import Organization
from app.models.organization_models import (
    AcceptIncidentBody,
    CapacityUpdateRequest,
    OrganizationIncidentItem,
    OrganizationOverviewResponse,
    UpdateResponseStatusBody,
)
from app.domain import outbox_event_types as T
from app.services.organization_registration_service import project_organization_orm_to_neo4j
from app.services.outbox_service import enqueue_in_session

_log = logging.getLogger("pulsegrid.organization_service")


def _node_to_dict(node: Any) -> dict[str, Any]:
    if node is None:
        return {}
    if hasattr(node, "items"):
        return dict(node)
    return {}


def _org_props_neo(tx: Any, org_id: str) -> dict[str, Any] | None:
    rec = tx.run(oq.GET_ORGANIZATION, org_id=org_id).single()
    if rec is None or rec.get("o") is None:
        return None
    return _node_to_dict(rec["o"])


def _organization_exists(org_id: str, db: Session | None) -> bool:
    """True if the org is known in PostgreSQL and/or Neo4j (legacy)."""
    if db is not None:
        try:
            oid = uuid.UUID(str(org_id).strip())
        except ValueError:
            oid = None
        else:
            if db.get(Organization, oid) is not None:
                return True
    driver = get_driver()
    settings = get_settings()

    def read(tx: Any) -> bool:
        return _org_props_neo(tx, org_id) is not None

    with managed_neo4j_session(driver, settings) as session:
        return session.execute_read(read)


def _count_open_assigned_incidents_neo(org_id: str) -> int:
    driver = get_driver()
    settings = get_settings()

    def read(tx: Any) -> int:
        c = tx.run(oq.COUNT_ORG_INCIDENTS, org_id=org_id).single()
        return int(c["c"]) if c and c.get("c") is not None else 0

    with managed_neo4j_session(driver, settings) as session:
        return session.execute_read(read)


def get_overview(org_id: str, db: Session | None = None) -> OrganizationOverviewResponse:
    """Canonical capacity + identity from PostgreSQL when available; open incident count from Neo4j."""
    if db is not None:
        try:
            oid = uuid.UUID(str(org_id).strip())
        except ValueError:
            oid = None
        if oid is not None:
            org = db.get(Organization, oid)
            if org is not None:
                open_n = _count_open_assigned_incidents_neo(org_id)
                capacity = {
                    "beds_available": org.beds_available,
                    "oxygen_units": org.oxygen_units,
                    "ambulances_available": org.ambulances_available,
                    "shelter_units": org.shelter_units,
                    "food_capacity_units": org.food_capacity_units,
                    "rescue_units": org.rescue_units,
                }
                return OrganizationOverviewResponse(
                    organization_id=str(org.id),
                    name=org.name,
                    org_type=org.org_type,
                    zone_id=org.zone_id or "",
                    active=bool(org.is_active),
                    assigned_incidents_open=open_n,
                    capacity=capacity,
                )

    driver = get_driver()
    settings = get_settings()

    def read_neo(tx: Any) -> OrganizationOverviewResponse | None:
        props = _org_props_neo(tx, org_id)
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
        out = session.execute_read(read_neo)
    if out is None:
        raise HTTPException(status_code=404, detail="Organization not found.")
    return out


def list_incidents(org_id: str, db: Session | None = None) -> list[OrganizationIncidentItem]:
    if not _organization_exists(org_id, db):
        raise HTTPException(status_code=404, detail="Organization not found.")
    driver = get_driver()
    settings = get_settings()

    def read(tx: Any) -> list[OrganizationIncidentItem]:
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
        return session.execute_read(read)


def update_capacity(org_id: str, body: CapacityUpdateRequest, db: Session) -> dict[str, Any]:
    """Update canonical capacity on PostgreSQL, then project to Neo4j for matching/graph."""
    props = body.model_dump(exclude_none=True)
    if not props:
        return {"ok": True, "updated": {}, "neo4j_projection": "skipped"}

    try:
        oid = uuid.UUID(str(org_id).strip())
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid organization id.") from exc

    org = db.get(Organization, oid)
    if org is None:
        _log.warning(
            "organization_capacity_update_pg_miss_falling_back_neo",
            extra={"organization_id": org_id},
        )
        return _update_capacity_neo_only(org_id, props)

    field_map = (
        ("beds_available", "beds_available", int),
        ("oxygen_units", "oxygen_units", int),
        ("ambulances_available", "ambulances_available", int),
        ("shelter_units", "shelter_units", int),
        ("food_capacity_units", "food_capacity_units", int),
        ("rescue_units", "rescue_units", int),
        ("active", "is_active", bool),
    )
    for json_key, attr, caster in field_map:
        if json_key not in props:
            continue
        val = props[json_key]
        if json_key == "active":
            setattr(org, attr, bool(val))
        else:
            setattr(org, attr, max(0, int(val)))

    ts = datetime.now(tz=timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    db.add(org)
    enqueue_in_session(
        db,
        event_type=T.ORGANIZATION_CAPACITY_UPDATED,
        aggregate_type=T.AGG_ORGANIZATION,
        aggregate_id=str(oid),
        payload={"updated": props, "occurred_at": ts},
    )
    db.commit()
    db.refresh(org)

    projection = project_organization_orm_to_neo4j(db, org)
    if not projection.ok and not projection.skipped:
        _log.error(
            "organization_capacity_neo4j_projection_failed_post_commit",
            extra={"organization_id": org_id, "detail": projection.detail},
        )

    neo_status = "skipped" if projection.skipped else ("ok" if projection.ok else "failed")
    return {"ok": True, "updated": props, "neo4j_projection": neo_status}


def _update_capacity_neo_only(org_id: str, props: dict[str, Any]) -> dict[str, Any]:
    """Legacy organizations that exist only in Neo4j (pre-PostgreSQL)."""
    driver = get_driver()
    settings = get_settings()

    def write(tx: Any) -> dict[str, Any]:
        if _org_props_neo(tx, org_id) is None:
            raise HTTPException(status_code=404, detail="Organization not found.")
        tx.run(oq.SET_ORGAN_CAPACITY, org_id=org_id, props=props)
        return {"ok": True, "updated": props, "neo4j_projection": "legacy_neo_only"}

    with managed_neo4j_session(driver, settings) as session:
        return session.execute_write(write)


def accept_incident(org_id: str, body: AcceptIncidentBody, db: Session | None = None) -> dict[str, Any]:
    if not _organization_exists(org_id, db):
        raise HTTPException(status_code=404, detail="Organization not found.")
    driver = get_driver()
    settings = get_settings()

    def write(tx: Any) -> dict[str, Any]:
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


def update_response_status(org_id: str, body: UpdateResponseStatusBody, db: Session | None = None) -> dict[str, Any]:
    if not _organization_exists(org_id, db):
        raise HTTPException(status_code=404, detail="Organization not found.")
    driver = get_driver()
    settings = get_settings()

    def write(tx: Any) -> dict[str, Any]:
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
