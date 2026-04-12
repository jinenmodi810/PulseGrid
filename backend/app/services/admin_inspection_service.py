"""Admin inspection: read Neo4j graph into API models (no mock data)."""

from __future__ import annotations

import json
from datetime import date, datetime, time
from typing import Any, Callable, TypeVar

from neo4j import unit_of_work
from neo4j.time import DateTime as Neo4jDateTime

from app.core.config import get_settings
from app.core.neo4j_client import get_driver, managed_neo4j_session
from app.db.queries import admin_inspection_queries as q
from app.models.admin_inspection_models import (
    AdminAssignmentItem,
    AdminIncidentDetailResponse,
    AdminIncidentItem,
    AdminIncidentReporter,
    AdminIncidentVolunteer,
    AdminIncidentZone,
    AdminOverviewResponse,
    AdminRejectedItem,
    AdminRewardItem,
    AdminSupportNetworkResponse,
    AdminUserItem,
    AdminVolunteerItem,
)

_T = TypeVar("_T")


def _execute_read(session: Any, work: Callable[[Any], _T]) -> _T:
    """Bound Neo4j read work so slow Aura / heavy graph cannot hang HTTP clients indefinitely."""
    timeout = float(get_settings().NEO4J_TRANSACTION_TIMEOUT)
    if timeout <= 0:
        return session.execute_read(work)
    return session.execute_read(unit_of_work(timeout=timeout)(work))


def _serialize_value(val: Any) -> Any:
    if val is None:
        return None
    if isinstance(val, Neo4jDateTime):
        return val.to_native().isoformat().replace("+00:00", "Z")
    if isinstance(val, datetime):
        return val.isoformat().replace("+00:00", "Z")
    if isinstance(val, (date, time)):
        return val.isoformat()
    if isinstance(val, (int, float, str, bool)):
        return val
    if isinstance(val, bytes):
        return val.decode("utf-8", errors="replace")
    if isinstance(val, dict):
        return {str(k): _serialize_value(v) for k, v in val.items()}
    if isinstance(val, (list, tuple)):
        return [_serialize_value(x) for x in val]
    return str(val)


def _node_to_props(node: Any) -> dict[str, Any]:
    if node is None:
        return {}
    if hasattr(node, "items"):
        return {str(k): _serialize_value(v) for k, v in dict(node).items()}
    return {}


def _scalar_count(tx: Any, cypher: str) -> int:
    rec = tx.run(cypher).single()
    if rec is None or rec.get("c") is None:
        return 0
    return int(rec["c"])


def _overview_tx(tx: Any) -> AdminOverviewResponse:
    # TODO(Phase1): filters by zone/time window; pagination not applicable for overview.
    total_users = _scalar_count(tx, q.COUNT_USERS)
    total_volunteers = _scalar_count(tx, q.COUNT_VOLUNTEERS)
    total_incidents = _scalar_count(tx, q.COUNT_INCIDENTS)
    active_incidents = _scalar_count(tx, q.COUNT_ACTIVE_INCIDENTS)
    pending_incidents = _scalar_count(tx, q.COUNT_PENDING_INCIDENTS)
    accepted_incidents = _scalar_count(tx, q.COUNT_ACCEPTED_INCIDENTS)
    resolved_incidents = _scalar_count(tx, q.COUNT_RESOLVED_INCIDENTS)
    total_hospitals = _scalar_count(tx, q.COUNT_HOSPITALS)
    total_shelters = _scalar_count(tx, q.COUNT_SHELTERS)
    total_support_contacts = _scalar_count(tx, q.COUNT_SUPPORT_CONTACTS)
    total_zones = _scalar_count(tx, q.COUNT_ZONES)
    total_rewards = _scalar_count(tx, q.COUNT_REWARDS)
    total_assigned_incidents = _scalar_count(tx, q.COUNT_DISTINCT_ASSIGNED_INCIDENTS)
    total_completed_incidents = _scalar_count(tx, q.COUNT_COMPLETED_INCIDENTS)

    agg = tx.run(q.AGG_VOLUNTEER_TRUST_AND_CREDITS).single()
    avg_trust = float(agg["avg_trust"]) if agg and agg.get("avg_trust") is not None else 0.0
    sum_credits = int(agg["sum_credits"]) if agg and agg.get("sum_credits") is not None else 0

    return AdminOverviewResponse(
        total_users=total_users,
        total_volunteers=total_volunteers,
        total_incidents=total_incidents,
        active_incidents=active_incidents,
        pending_incidents=pending_incidents,
        accepted_incidents=accepted_incidents,
        resolved_incidents=resolved_incidents,
        total_hospitals=total_hospitals,
        total_shelters=total_shelters,
        total_support_contacts=total_support_contacts,
        total_zones=total_zones,
        total_rewards=total_rewards,
        total_assigned_incidents=total_assigned_incidents,
        total_completed_incidents=total_completed_incidents,
        average_volunteer_trust_score=round(avg_trust, 4),
        total_volunteer_credits=sum_credits,
    )


def get_overview() -> AdminOverviewResponse:
    driver = get_driver()
    settings = get_settings()

    def read(tx: Any) -> AdminOverviewResponse:
        return _overview_tx(tx)

    with managed_neo4j_session(driver, settings) as session:
        return _execute_read(session, read)


def _map_user_row(r: dict[str, Any]) -> AdminUserItem:
    fs = r.get("family_size")
    created = r.get("created_at")
    return AdminUserItem(
        user_id=str(r.get("user_id") or ""),
        name=str(r.get("name") or ""),
        phone=str(r.get("phone") or ""),
        language=str(r.get("language") or ""),
        zone_id=str(r.get("zone_id") or ""),
        family_size=int(fs) if fs is not None else None,
        created_at=_serialize_value(created) if created is not None else None,
    )


def list_users() -> list[AdminUserItem]:
    # TODO(Phase1): pagination, search by phone/name, zone filter.
    driver = get_driver()
    settings = get_settings()

    def read(tx: Any) -> list[AdminUserItem]:
        rows = [dict(rec) for rec in tx.run(q.LIST_USERS)]
        return [_map_user_row(row) for row in rows]

    with managed_neo4j_session(driver, settings) as session:
        return _execute_read(session, read)


def _normalize_languages(raw: Any) -> list[str]:
    if raw is None:
        return []
    if isinstance(raw, list):
        return [str(x) for x in raw if x is not None]
    return [str(raw)]


def _map_volunteer_row(r: dict[str, Any]) -> AdminVolunteerItem:
    return AdminVolunteerItem(
        volunteer_id=str(r.get("volunteer_id") or ""),
        name=str(r.get("name") or ""),
        phone=str(r.get("phone") or ""),
        skill_type=str(r.get("skill_type") or ""),
        languages=_normalize_languages(r.get("languages")),
        zone_id=str(r.get("zone_id") or ""),
        availability=str(r.get("availability") or ""),
        verified=bool(r.get("verified", False)),
        trust_score=float(r.get("trust_score") or 0.0),
        credits=int(r.get("credits") or 0),
        assigned_incident_count=int(r.get("assigned_incident_count") or 0),
        completed_incident_count=int(r.get("completed_incident_count") or 0),
    )


def list_volunteers() -> list[AdminVolunteerItem]:
    # TODO(Phase1): pagination, search, zone/skill filters.
    driver = get_driver()
    settings = get_settings()

    def read(tx: Any) -> list[AdminVolunteerItem]:
        return [_map_volunteer_row(dict(rec)) for rec in tx.run(q.LIST_VOLUNTEERS)]

    with managed_neo4j_session(driver, settings) as session:
        return _execute_read(session, read)


def _map_incident_row(r: dict[str, Any]) -> AdminIncidentItem:
    pc = r.get("people_count")
    created = r.get("created_at")
    return AdminIncidentItem(
        incident_id=str(r.get("incident_id") or ""),
        incident_type=str(r.get("incident_type") or ""),
        severity=str(r.get("severity") or ""),
        priority_score=float(r.get("priority_score") or 0.0),
        priority_label=str(r.get("priority_label") or ""),
        status=str(r.get("status") or ""),
        zone_id=str(r.get("zone_id") or ""),
        people_count=int(pc) if pc is not None else 1,
        created_at=_serialize_value(created) if created is not None else None,
        reported_by_user_id=str(r["reported_by_user_id"]) if r.get("reported_by_user_id") else None,
        assigned_volunteer_id=str(r["assigned_volunteer_id"]) if r.get("assigned_volunteer_id") else None,
        elderly=bool(r.get("elderly", False)),
        child_present=bool(r.get("child_present", False)),
        injury=bool(r.get("injury", False)),
        oxygen_required=bool(r.get("oxygen_required", False)),
        shelter_needed=bool(r.get("shelter_needed", False)),
        food_needed=bool(r.get("food_needed", False)),
        transport_needed=bool(r.get("transport_needed", False)),
        note=str(r.get("note") or ""),
    )


def list_incidents() -> list[AdminIncidentItem]:
    # TODO(Phase1): pagination, status/zone filters, full-text search on note.
    driver = get_driver()
    settings = get_settings()

    def read(tx: Any) -> list[AdminIncidentItem]:
        return [_map_incident_row(dict(rec)) for rec in tx.run(q.LIST_INCIDENTS_ADMIN)]

    with managed_neo4j_session(driver, settings) as session:
        return _execute_read(session, read)


def _incident_item_from_props(props: dict[str, Any], incident_id: str) -> AdminIncidentItem:
    row = {
        "incident_id": props.get("id", incident_id),
        "incident_type": props.get("incident_type") or props.get("title") or "",
        "severity": props.get("severity") or "medium",
        "priority_score": props.get("priority_score") or 0,
        "priority_label": props.get("priority_label") or "MEDIUM",
        "status": props.get("status") or "open",
        "zone_id": props.get("zone_id") or "",
        "people_count": props.get("people_count") or 1,
        "created_at": props.get("created_at"),
        "reported_by_user_id": None,
        "assigned_volunteer_id": props.get("assigned_volunteer_id"),
        "elderly": props.get("elderly", False),
        "child_present": props.get("child_present", False),
        "injury": props.get("injury", False),
        "oxygen_required": props.get("oxygen_required", False),
        "shelter_needed": props.get("shelter_needed", False),
        "food_needed": props.get("food_needed", False),
        "transport_needed": props.get("transport_needed", False),
        "note": props.get("note") or "",
    }
    return _map_incident_row(row)


def _parse_rejected_json(raw: Any) -> list[AdminRejectedItem]:
    if raw is None:
        return []
    s = raw if isinstance(raw, str) else json.dumps(raw)
    try:
        parsed = json.loads(s) if isinstance(s, str) else []
    except json.JSONDecodeError:
        return []
    out: list[AdminRejectedItem] = []
    if not isinstance(parsed, list):
        return out
    for item in parsed:
        if isinstance(item, dict):
            out.append(
                AdminRejectedItem(
                    volunteer_id=str(item.get("volunteer_id", "")),
                    name=str(item.get("name", "")),
                    reason=str(item.get("reason", "")),
                )
            )
    return out


def _build_status_history(
    *,
    incident_props: dict[str, Any],
    task_events: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    # TODO(Phase1): persist append-only StatusChange nodes instead of synthesizing from graph + props.
    history: list[dict[str, Any]] = []
    created = incident_props.get("created_at")
    if created is not None:
        history.append(
            {
                "status": "created",
                "at": _serialize_value(created),
                "detail": "Incident node created",
            }
        )
    st = incident_props.get("status")
    if st:
        history.append({"status": str(st), "at": None, "detail": "Current status on Incident node"})
    for ev in task_events:
        vid = ev.get("volunteer_id")
        if vid is None:
            continue
        at = ev.get("at")
        history.append(
            {
                "event": ev.get("event"),
                "volunteer_id": str(vid),
                "at": _serialize_value(at) if at is not None else None,
            }
        )
    return history


def _relationships_summary(incoming: list[Any], outgoing: list[Any]) -> str:
    lines: list[str] = []
    for group in (incoming or [], outgoing or []):
        for line in group:
            if line:
                lines.append(str(line))
    return "\n".join(sorted(set(lines)))


def get_incident_detail(incident_id: str) -> AdminIncidentDetailResponse | None:
    driver = get_driver()
    settings = get_settings()

    def read(tx: Any) -> AdminIncidentDetailResponse | None:
        rec = tx.run(q.GET_INCIDENT_ADMIN, incident_id=incident_id).single()
        if rec is None or rec.get("incident") is None:
            return None
        inc = _node_to_props(rec["incident"])
        reporter = rec.get("reporter")
        assignee = rec.get("assignee")
        zone = rec.get("zone")
        reporter_zone_id = str(rec.get("reporter_zone_id") or "")

        graph = tx.run(q.INCIDENT_GRAPH_LINES, incident_id=incident_id).single()
        incoming = graph.get("incoming") if graph else []
        outgoing = graph.get("outgoing") if graph else []

        ev_row = tx.run(q.INCIDENT_TASK_EVENTS, incident_id=incident_id).single()
        raw_events = ev_row.get("events") if ev_row else []
        task_events: list[dict[str, Any]] = []
        if isinstance(raw_events, list):
            for m in raw_events:
                if isinstance(m, dict) and m.get("volunteer_id"):
                    task_events.append(
                        {
                            "event": m.get("event"),
                            "volunteer_id": m.get("volunteer_id"),
                            "at": m.get("at"),
                        }
                    )

        item = _incident_item_from_props(inc, incident_id)
        uid = _node_to_props(reporter).get("id")
        if uid:
            item = item.model_copy(update={"reported_by_user_id": str(uid)})
        aid = _node_to_props(assignee).get("id")
        if aid:
            item = item.model_copy(update={"assigned_volunteer_id": str(aid)})

        reporting_user = None
        if reporter is not None:
            rp = _node_to_props(reporter)
            reporting_user = AdminIncidentReporter(
                user_id=str(rp.get("id", "")),
                name=str(rp.get("full_name", "")),
                phone=str(rp.get("phone", "")),
                zone_id=reporter_zone_id,
            )

        assigned_volunteer = None
        if assignee is not None:
            vp = _node_to_props(assignee)
            assigned_volunteer = AdminIncidentVolunteer(
                volunteer_id=str(vp.get("id", "")),
                name=str(vp.get("display_name", "")),
                phone=str(vp.get("phone", "")),
            )

        zone_model = None
        if zone is not None:
            zp = _node_to_props(zone)
            zone_model = AdminIncidentZone(
                zone_id=str(zp.get("id", "")),
                name=str(zp.get("name", zp.get("id", ""))),
            )

        rejected = _parse_rejected_json(inc.get("rejected_json"))
        summary = _relationships_summary(
            list(incoming) if incoming else [],
            list(outgoing) if outgoing else [],
        )
        status_history = _build_status_history(incident_props=inc, task_events=task_events)

        return AdminIncidentDetailResponse(
            incident=item,
            reporting_user=reporting_user,
            assigned_volunteer=assigned_volunteer,
            zone=zone_model,
            route_status=str(inc.get("route_status", "") or ""),
            ai_guidance=str(inc.get("ai_guidance", "") or ""),
            rejected_candidates=rejected,
            status_history=status_history,
            relationships_summary=summary,
        )

    with managed_neo4j_session(driver, settings) as session:
        return _execute_read(session, read)


def list_assignments() -> list[AdminAssignmentItem]:
    # TODO(Phase1): filter by zone/status; pagination.
    driver = get_driver()
    settings = get_settings()

    def read(tx: Any) -> list[AdminAssignmentItem]:
        items: list[AdminAssignmentItem] = []
        for rec in tx.run(q.LIST_ASSIGNMENTS):
            r = dict(rec)
            at = r.get("assigned_at")
            items.append(
                AdminAssignmentItem(
                    incident_id=str(r.get("incident_id") or ""),
                    volunteer_id=str(r.get("volunteer_id") or ""),
                    volunteer_name=str(r.get("volunteer_name") or ""),
                    status=str(r.get("status") or ""),
                    zone_id=str(r.get("zone_id") or ""),
                    priority_label=str(r.get("priority_label") or ""),
                    assigned_at=_serialize_value(at) if at is not None else None,
                )
            )
        return items

    with managed_neo4j_session(driver, settings) as session:
        return _execute_read(session, read)


def list_rewards() -> list[AdminRewardItem]:
    # TODO(Phase1): pagination; min credits filter.
    driver = get_driver()
    settings = get_settings()

    def read(tx: Any) -> list[AdminRewardItem]:
        out: list[AdminRewardItem] = []
        for rec in tx.run(q.LIST_REWARDS_SUMMARY):
            r = dict(rec)
            out.append(
                AdminRewardItem(
                    volunteer_id=str(r.get("volunteer_id") or ""),
                    volunteer_name=str(r.get("volunteer_name") or ""),
                    credits=int(r.get("credits") or 0),
                    trust_score=float(r.get("trust_score") or 0.0),
                    earned_reward_count=int(r.get("earned_reward_count") or 0),
                    completed_incident_count=int(r.get("completed_incident_count") or 0),
                )
            )
        return out

    with managed_neo4j_session(driver, settings) as session:
        return _execute_read(session, read)


def get_support_network() -> AdminSupportNetworkResponse:
    driver = get_driver()
    settings = get_settings()

    def read(tx: Any) -> AdminSupportNetworkResponse:
        hospitals = []
        for rec in tx.run(q.LIST_HOSPITALS_PROPS):
            props = rec.get("props")
            hospitals.append(_serialize_value(dict(props)) if props is not None else {})
        shelters = []
        for rec in tx.run(q.LIST_SHELTERS_PROPS):
            props = rec.get("props")
            shelters.append(_serialize_value(dict(props)) if props is not None else {})
        contacts = []
        for rec in tx.run(q.LIST_SUPPORT_CONTACTS_PROPS):
            props = rec.get("props")
            contacts.append(_serialize_value(dict(props)) if props is not None else {})
        zones = []
        for rec in tx.run(q.LIST_ZONES_ADMIN):
            z = dict(rec)
            zones.append(
                {
                    "zone_id": str(z.get("zone_id") or ""),
                    "name": str(z.get("name") or ""),
                }
            )
        return AdminSupportNetworkResponse(
            hospitals=hospitals,
            shelters=shelters,
            support_contacts=contacts,
            zones=zones,
        )

    with managed_neo4j_session(driver, settings) as session:
        return _execute_read(session, read)
