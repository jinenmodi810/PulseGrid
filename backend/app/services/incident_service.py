"""Create and read incidents in Neo4j (orchestration)."""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from typing import Any

from app.core.config import get_settings
from app.core.neo4j_client import get_driver, managed_neo4j_session
from app.db.queries import incident_queries
from app.models.incident_requests import (
    CreateIncidentRequest,
    CreateIncidentResponse,
    EmergencyContactResponse,
    IncidentDetailResponse,
    PriorityPreviewRequest,
    PriorityPreviewResponse,
    RejectedCandidate,
    RejectedOrganizationCandidate,
)
from app.models.response_engine_models import ResponseEngineInput
from app.models.response_tier_models import ResponseTierReason
from app.services import graph_matching_service, organization_matching_service, priority_service
from app.services.response_tier_service import (
    augment_tier_reasons_for_matching,
    determine_response_tier,
    finalize_response_after_matching,
    merge_plan_reasons,
)


def _ai_guidance_placeholder(*, incident_type: str, zone_id: str, preferred_language: str = "") -> str:
    # TODO(Phase1): stream Gemini with graph context and multilingual prompts; keep placeholder for hackathon stability.
    lang = (preferred_language or "en").strip() or "en"
    return (
        f"Stabilize {incident_type} response in {zone_id} (reporter language {lang}): confirm shelter intake, "
        f"verify oxygen logistics if flagged, and debrief volunteers after handoff."
    )


def preview_priority(body: PriorityPreviewRequest) -> PriorityPreviewResponse:
    score, label = priority_service.preview_from_request(body)
    return PriorityPreviewResponse(priority_score=score, priority_label=label)


def create_incident(body: CreateIncidentRequest) -> CreateIncidentResponse:
    incident_id = str(uuid.uuid4())
    created_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

    def work(tx: Any) -> dict[str, Any]:
        profile: dict[str, Any] | None = None
        if body.user_id:
            rec = tx.run(incident_queries.GET_USER_PROFILE_FOR_INCIDENT, user_id=body.user_id).single()
            if rec is not None:
                profile = dict(rec)

        profile_defaults_used: list[str] = []
        people_count = int(body.people_count)
        if body.use_profile_for_people_count and profile is not None:
            hz = profile.get("household_size")
            if hz is not None:
                people_count = max(1, int(hz))
                profile_defaults_used.append("people_count")

        elderly = bool(body.elderly)
        if body.use_profile_for_elderly and profile is not None:
            if int(profile.get("elderly_count") or 0) > 0:
                elderly = True
                profile_defaults_used.append("elderly")

        oxygen_required = bool(body.oxygen_required)
        if body.use_profile_for_oxygen_required and profile is not None:
            if bool(profile.get("oxygen_dependency")):
                oxygen_required = True
                profile_defaults_used.append("oxygen_required")

        preferred_language = ""
        emergency_contact: EmergencyContactResponse | None = None
        ec_name = ""
        ec_phone = ""
        ec_rel = ""
        if profile is not None:
            preferred_language = str(profile.get("preferred_language") or "en").strip() or "en"
            ec_name = str(profile.get("emergency_contact_name") or "").strip()
            ec_phone = str(profile.get("emergency_contact_phone") or "").strip()
            ec_rel = str(profile.get("emergency_contact_relationship") or "").strip()
            if ec_name or ec_phone:
                emergency_contact = EmergencyContactResponse(name=ec_name, phone=ec_phone, relationship=ec_rel)

        hz = int(profile.get("household_size") or 0) if profile else 0
        ec_n = int(profile.get("elderly_count") or 0) if profile else 0
        mobility = bool(profile.get("mobility_concern")) if profile else False
        oxy_prof = bool(profile.get("oxygen_dependency")) if profile else False

        score, label = priority_service.compute_priority_score_and_label(
            severity=body.severity,
            people_count=people_count,
            elderly=elderly,
            child_present=body.child_present,
            injury=body.injury,
            oxygen_required=oxygen_required,
            shelter_needed=body.shelter_needed,
            food_needed=body.food_needed,
            transport_needed=body.transport_needed,
        )
        guidance = _ai_guidance_placeholder(
            incident_type=body.incident_type,
            zone_id=body.zone_id,
            preferred_language=preferred_language,
        )

        tx.run(
            """
            MERGE (i:Incident {id: $incident_id})
            SET i.title = $title,
                i.incident_type = $incident_type,
                i.severity = $severity,
                i.people_count = $people_count,
                i.zone_id = $zone_id,
                i.elderly = $elderly,
                i.child_present = $child_present,
                i.injury = $injury,
                i.oxygen_required = $oxygen_required,
                i.shelter_needed = $shelter_needed,
                i.food_needed = $food_needed,
                i.transport_needed = $transport_needed,
                i.note = $note,
                i.priority_score = $priority_score,
                i.priority_label = $priority_label,
                i.status = 'open',
                i.created_at = $created_at,
                i.route_status = 'pending',
                i.ai_guidance = $ai_guidance,
                i.rejected_json = '[]',
                i.rejected_org_json = '[]',
                i.tier_reasons_json = '[]',
                i.decision_summary = '',
                i.assigned_volunteer_id = null,
                i.assigned_volunteer_name = null,
                i.eta_minutes = null,
                i.preferred_language = $preferred_language,
                i.emergency_contact_name = $ec_name,
                i.emergency_contact_phone = $ec_phone,
                i.emergency_contact_relationship = $ec_rel,
                i.mobility_concern = $mobility_concern,
                i.intake_source = $intake_source
            """,
            incident_id=incident_id,
            title=f"{body.incident_type} — {body.zone_id}",
            incident_type=body.incident_type,
            severity=body.severity,
            people_count=people_count,
            zone_id=body.zone_id,
            elderly=elderly,
            child_present=body.child_present,
            injury=body.injury,
            oxygen_required=oxygen_required,
            shelter_needed=body.shelter_needed,
            food_needed=body.food_needed,
            transport_needed=body.transport_needed,
            note=body.note,
            priority_score=score,
            priority_label=label,
            created_at=created_at,
            ai_guidance=guidance,
            preferred_language=preferred_language,
            ec_name=ec_name,
            ec_phone=ec_phone,
            ec_rel=ec_rel,
            mobility_concern=mobility,
            intake_source=(body.intake_source or "form").strip() or "form",
        )

        tx.run(
            incident_queries.LINK_USER_REPORTED_OPTIONAL,
            incident_id=incident_id,
            user_id=body.user_id,
        )
        tx.run(
            incident_queries.LINK_INCIDENT_TO_ZONE,
            incident_id=incident_id,
            zone_id=body.zone_id,
            zone_name=body.zone_id,
        )

        engine = ResponseEngineInput.from_create_context(
            body=body,
            people_count=people_count,
            elderly=elderly,
            oxygen_required=oxygen_required,
            preferred_language=preferred_language,
            mobility_concern=mobility,
            household_size=hz if hz > 0 else None,
            elderly_count=ec_n if ec_n > 0 else None,
            oxygen_dependency_profile=oxy_prof,
            priority_score=score,
            priority_label=label,
        )
        plan = determine_response_tier(engine.to_response_tier_input())

        if plan.seek_volunteer:
            match_result = graph_matching_service.find_best_volunteer_assignment(tx, engine)
        else:
            match_result = {"selected": None, "rejected": [], "eta_minutes": None}

        selected = match_result["selected"]
        rejected_raw: list[dict[str, str]] = list(match_result["rejected"])
        eta = match_result.get("eta_minutes")

        if plan.seek_organization:
            org_match = organization_matching_service.find_best_organization_assignment(tx, engine)
        else:
            org_match = {"selected": None, "rejected": [], "eta_minutes": None}

        org_rejected_raw: list[dict[str, str]] = list(org_match.get("rejected") or [])
        vol_selected = bool(selected and selected.get("id"))
        org_sel = org_match.get("selected")
        org_selected = bool(org_sel and org_sel.get("id"))

        response_tier, escalation_required, decision_summary = finalize_response_after_matching(
            plan,
            volunteer_selected=vol_selected,
            organization_selected=org_selected,
            severity=body.severity,
            priority_label=label,
        )
        escalation_required = bool(
            escalation_required
            or str(label or "").upper() == "CRITICAL"
            or str(body.severity or "").lower() == "critical"
            or float(score) >= 9.0
        )

        assigned_helper = None
        status = "open"
        if vol_selected and selected and selected.get("id"):
            tx.run(
                incident_queries.ASSIGN_VOLUNTEER_TO_INCIDENT,
                volunteer_id=selected["id"],
                incident_id=incident_id,
            )
            status = "assigned"
            assigned_helper = {"id": selected["id"], "name": selected.get("name") or ""}
            tx.run(
                """
                MATCH (i:Incident {id: $id})
                SET i.status = $status,
                    i.assigned_volunteer_id = $vid,
                    i.assigned_volunteer_name = $vname,
                    i.eta_minutes = $eta
                """,
                id=incident_id,
                status=status,
                vid=selected["id"],
                vname=selected.get("name") or "",
                eta=eta,
            )
        else:
            tx.run(
                """
                MATCH (i:Incident {id: $id})
                SET i.status = 'open', i.eta_minutes = null
                """,
                id=incident_id,
            )

        org_oid: str | None = None
        org_oname = ""
        org_otype = ""
        if org_selected and org_sel:
            org_oid = str(org_sel.get("id") or "")
            org_oname = str(org_sel.get("name") or "")
            org_otype = str(org_sel.get("org_type") or "")

        if org_oid:
            tx.run(
                incident_queries.ASSIGN_ORGANIZATION_TO_INCIDENT,
                org_id=org_oid,
                incident_id=incident_id,
            )

        augment = augment_tier_reasons_for_matching(
            plan,
            volunteer_selected=vol_selected,
            organization_selected=org_selected,
            rejected_volunteers=rejected_raw,
            rejected_organizations=org_rejected_raw,
        )
        tier_reason_models: list[ResponseTierReason] = merge_plan_reasons(plan, augment)
        tier_reasons_json = json.dumps([r.model_dump() for r in tier_reason_models])

        vol_cand = bool(plan.seek_volunteer)
        org_cand = bool(plan.seek_organization)

        tx.run(
            """
            MATCH (i:Incident {id: $id})
            SET i.assigned_organization_id = $oid,
                i.assigned_organization_name = $oname,
                i.assigned_organization_type = $otype,
                i.response_tier = $rt,
                i.escalation_required = $esc,
                i.decision_summary = $dsum,
                i.tier_reasons_json = $trj,
                i.rejected_json = $rj,
                i.rejected_org_json = $roj,
                i.volunteer_candidate_allowed = $vca,
                i.organization_candidate_allowed = $oca
            """,
            id=incident_id,
            oid=org_oid,
            oname=org_oname,
            otype=org_otype,
            rt=response_tier,
            esc=escalation_required,
            dsum=decision_summary,
            trj=tier_reasons_json,
            rj=graph_matching_service.rejected_to_json(rejected_raw),
            roj=organization_matching_service.rejected_org_to_json(org_rejected_raw),
            vca=vol_cand,
            oca=org_cand,
        )

        assigned_organization = None
        if org_oid:
            assigned_organization = {"id": org_oid, "name": org_oname, "org_type": org_otype}

        return {
            "incident_id": incident_id,
            "zone_id": body.zone_id,
            "status": status,
            "priority_score": score,
            "priority_label": label,
            "assigned_helper": assigned_helper,
            "assigned_organization": assigned_organization,
            "response_tier": response_tier,
            "volunteer_candidate_allowed": vol_cand,
            "organization_candidate_allowed": org_cand,
            "escalation_required": escalation_required,
            "decision_summary": decision_summary,
            "tier_reasons": tier_reason_models,
            "rejected": rejected_raw,
            "rejected_organizations": org_rejected_raw,
            "eta_minutes": eta,
            "ai_guidance": guidance,
            "preferred_language": preferred_language,
            "emergency_contact": emergency_contact,
            "profile_defaults_used": profile_defaults_used,
        }

    driver = get_driver()
    settings = get_settings()
    with managed_neo4j_session(driver, settings) as session:
        payload = session.execute_write(work)

    rejected_models = [RejectedCandidate(**r) for r in payload["rejected"]]
    org_rej = [RejectedOrganizationCandidate(**r) for r in payload.get("rejected_organizations") or []]
    ec = payload.get("emergency_contact")
    tr = list(payload.get("tier_reasons") or [])
    return CreateIncidentResponse(
        incident_id=payload["incident_id"],
        zone_id=str(payload.get("zone_id") or ""),
        status=payload["status"],
        priority_score=payload["priority_score"],
        priority_label=payload["priority_label"],
        assigned_helper=payload["assigned_helper"],
        assigned_organization=payload.get("assigned_organization"),
        response_tier=str(payload.get("response_tier") or "pending"),
        volunteer_candidate_allowed=bool(payload.get("volunteer_candidate_allowed", True)),
        organization_candidate_allowed=bool(payload.get("organization_candidate_allowed", False)),
        escalation_required=bool(payload.get("escalation_required", False)),
        decision_summary=str(payload.get("decision_summary") or ""),
        tier_reasons=tr,
        rejected_candidates=rejected_models,
        rejected_organization_candidates=org_rej,
        eta_minutes=payload["eta_minutes"],
        ai_guidance=payload["ai_guidance"],
        preferred_language=str(payload.get("preferred_language") or ""),
        emergency_contact=ec if isinstance(ec, EmergencyContactResponse) else None,
        profile_defaults_used=list(payload.get("profile_defaults_used") or []),
    )


def get_incident_detail(incident_id: str) -> IncidentDetailResponse | None:
    driver = get_driver()
    settings = get_settings()
    with managed_neo4j_session(driver, settings) as session:

        def read(tx: Any) -> dict[str, Any] | None:
            rec = tx.run(incident_queries.GET_INCIDENT_DETAIL, incident_id=incident_id).single()
            if rec is None:
                return None
            i = rec["incident"]
            node = dict(i)
            assigned_id = rec.get("assigned_id")
            assigned_name = rec.get("assigned_name")
            return {
                "node": node,
                "assigned_id": assigned_id,
                "assigned_name": assigned_name,
                "assigned_organization_id": rec.get("assigned_organization_id"),
                "assigned_organization_name": rec.get("assigned_organization_name"),
                "assigned_organization_type": rec.get("assigned_organization_type"),
                "response_tier": rec.get("response_tier"),
                "volunteer_candidate_allowed": rec.get("volunteer_candidate_allowed"),
                "organization_candidate_allowed": rec.get("organization_candidate_allowed"),
                "escalation_required": rec.get("escalation_required"),
                "decision_summary": rec.get("decision_summary"),
                "tier_reasons_json": rec.get("tier_reasons_json"),
                "rejected_org_json": rec.get("rejected_org_json"),
            }

        row = session.execute_read(read)
    if row is None:
        return None

    node = row["node"]
    rejected: list[RejectedCandidate] = []
    raw = node.get("rejected_json") or "[]"
    try:
        parsed = json.loads(raw) if isinstance(raw, str) else []
        for item in parsed:
            if isinstance(item, dict) and "volunteer_id" in item:
                rejected.append(
                    RejectedCandidate(
                        volunteer_id=str(item.get("volunteer_id", "")),
                        name=str(item.get("name", "")),
                        reason=str(item.get("reason", "")),
                    )
                )
    except json.JSONDecodeError:
        pass

    rejected_org: list[RejectedOrganizationCandidate] = []
    raw_org = row.get("rejected_org_json") or node.get("rejected_org_json") or "[]"
    try:
        parsed_org = json.loads(raw_org) if isinstance(raw_org, str) else []
        for item in parsed_org:
            if isinstance(item, dict) and "organization_id" in item:
                rejected_org.append(
                    RejectedOrganizationCandidate(
                        organization_id=str(item.get("organization_id", "")),
                        name=str(item.get("name", "")),
                        reason=str(item.get("reason", "")),
                    )
                )
    except json.JSONDecodeError:
        pass

    tier_reasons: list[ResponseTierReason] = []
    raw_tr = row.get("tier_reasons_json") or node.get("tier_reasons_json") or "[]"
    try:
        parsed_tr = json.loads(raw_tr) if isinstance(raw_tr, str) else []
        for item in parsed_tr:
            if isinstance(item, dict) and "code" in item and "detail" in item:
                tier_reasons.append(ResponseTierReason(code=str(item["code"]), detail=str(item["detail"])))
    except json.JSONDecodeError:
        pass

    decision_summary = str(row.get("decision_summary") or node.get("decision_summary") or "")

    assigned = None
    aid = row.get("assigned_id")
    aname = row.get("assigned_name")
    if aid:
        assigned = {"id": str(aid), "name": str(aname or "")}

    org_oid = row.get("assigned_organization_id") or node.get("assigned_organization_id")
    org_oname = row.get("assigned_organization_name") or node.get("assigned_organization_name")
    org_otype = row.get("assigned_organization_type") or node.get("assigned_organization_type")
    assigned_organization = None
    if org_oid:
        assigned_organization = {
            "id": str(org_oid),
            "name": str(org_oname or ""),
            "org_type": str(org_otype or ""),
        }
    response_tier = str(row.get("response_tier") or node.get("response_tier") or "pending")
    volunteer_candidate_allowed = bool(
        row.get("volunteer_candidate_allowed")
        if row.get("volunteer_candidate_allowed") is not None
        else node.get("volunteer_candidate_allowed", True)
    )
    organization_candidate_allowed = bool(
        row.get("organization_candidate_allowed")
        if row.get("organization_candidate_allowed") is not None
        else node.get("organization_candidate_allowed", False)
    )
    escalation_required = bool(row.get("escalation_required") if row.get("escalation_required") is not None else node.get("escalation_required", False))

    ecn = str(node.get("emergency_contact_name") or "").strip()
    ecp = str(node.get("emergency_contact_phone") or "").strip()
    ecr = str(node.get("emergency_contact_relationship") or "").strip()
    emergency = (
        EmergencyContactResponse(name=ecn, phone=ecp, relationship=ecr) if (ecn or ecp) else None
    )

    return IncidentDetailResponse(
        incident_id=str(node.get("id", incident_id)),
        incident_type=str(node.get("incident_type", "")),
        severity=str(node.get("severity", "medium")),
        people_count=int(node.get("people_count") or 1),
        zone_id=str(node.get("zone_id", "")),
        status=str(node.get("status", "open")),
        priority_score=float(node.get("priority_score") or 0),
        priority_label=str(node.get("priority_label", "MEDIUM")),
        note=str(node.get("note", "")),
        assigned_helper=assigned,
        assigned_organization=assigned_organization,
        response_tier=response_tier,
        volunteer_candidate_allowed=volunteer_candidate_allowed,
        organization_candidate_allowed=organization_candidate_allowed,
        escalation_required=escalation_required,
        decision_summary=decision_summary,
        tier_reasons=tier_reasons,
        rejected_candidates=rejected,
        rejected_organization_candidates=rejected_org,
        eta_minutes=int(node["eta_minutes"]) if node.get("eta_minutes") is not None else None,
        route_status=str(node.get("route_status", "pending")),
        ai_guidance=str(node.get("ai_guidance", "")),
        created_at=str(node.get("created_at")) if node.get("created_at") else None,
        elderly=bool(node.get("elderly", False)),
        child_present=bool(node.get("child_present", False)),
        injury=bool(node.get("injury", False)),
        oxygen_required=bool(node.get("oxygen_required", False)),
        shelter_needed=bool(node.get("shelter_needed", False)),
        food_needed=bool(node.get("food_needed", False)),
        transport_needed=bool(node.get("transport_needed", False)),
        preferred_language=str(node.get("preferred_language", "") or ""),
        emergency_contact=emergency,
    )


def list_incidents() -> list[dict[str, Any]]:
    driver = get_driver()
    settings = get_settings()
    with managed_neo4j_session(driver, settings) as session:

        def read(tx: Any) -> list[dict[str, Any]]:
            return [dict(r) for r in tx.run(incident_queries.LIST_INCIDENTS_FULL)]

        return session.execute_read(read)
