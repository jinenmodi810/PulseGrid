"""Graph-based volunteer matching — zone-first, profile-aware rule scoring."""

from __future__ import annotations

import json
from typing import Any

from app.core.config import get_settings
from app.core.neo4j_client import get_driver, managed_neo4j_session
from app.db.queries import matching_queries
from app.models.response_engine_models import ResponseEngineInput


def _coerce_str_list(val: Any) -> list[str]:
    if val is None:
        return []
    if isinstance(val, list):
        return [str(x) for x in val if x is not None and str(x).strip()]
    return [str(val)] if str(val).strip() else []


def _availability_blocked(availability: str) -> bool:
    a = (availability or "").lower()
    if not a.strip():
        return False
    return any(
        p in a
        for p in (
            "unavailable",
            "not available",
            "offline",
            "no availability",
        )
    )


def _transport_usable(transport_access: str) -> bool:
    t = (transport_access or "").lower().strip()
    return t not in ("", "none", "no")


def _volunteer_support_types(row: dict[str, Any]) -> set[str]:
    raw = row.get("support_types")
    if isinstance(raw, list) and raw:
        return {str(x).strip().lower() for x in raw if str(x).strip()}
    skills = _coerce_str_list(row.get("skills"))
    sk = (row.get("skill_type") or "").strip().lower()
    if not skills and sk:
        skills = [sk]
    out: set[str] = {"general_support"}
    for s in skills:
        sl = s.lower()
        if "medical" in sl:
            out.add("medical")
        if "logistics" in sl or "transport" in sl:
            out.add("transport")
        if "shelter" in sl:
            out.add("shelter")
        if "food" in sl:
            out.add("food")
        if "elder" in sl:
            out.add("elderly_support")
        if "child" in sl:
            out.add("child_support")
    return out


def _incident_support_needs(
    *,
    incident_type: str,
    transport_needed: bool,
    shelter_needed: bool,
    food_needed: bool,
    injury: bool,
    child_present: bool,
    elderly: bool,
) -> set[str]:
    needs: set[str] = set()
    it = (incident_type or "").lower()
    if "medical" in it or injury:
        needs.add("medical")
    if transport_needed:
        needs.add("transport")
    if shelter_needed:
        needs.add("shelter")
    if food_needed:
        needs.add("food")
    if elderly:
        needs.add("elderly_support")
    if child_present:
        needs.add("child_support")
    return needs


def _language_compatible(user_lang: str, volunteer_langs: list[str]) -> tuple[bool, str]:
    ul = (user_lang or "").strip().lower()
    if not ul or ul == "other":
        return True, ""
    vl = [str(x).strip().lower() for x in volunteer_langs if str(x).strip()]
    if not vl:
        return True, ""
    if ul in vl:
        return True, ""
    return False, "language mismatch"


def _support_compatible(incident_needs: set[str], volunteer_types: set[str]) -> tuple[bool, str]:
    if not incident_needs:
        return True, ""
    if "general_support" in volunteer_types:
        return True, ""
    if incident_needs.intersection(volunteer_types):
        return True, ""
    return False, "support type mismatch"


def _base_score(
    *,
    row: dict[str, Any],
    same_zone: bool,
    incident_type: str,
    transport_needed: bool,
    shelter_needed: bool,
) -> float:
    credits = float(row.get("credits") or 0)
    trust = float(row.get("trust_score") or 0.5)
    skill = (row.get("skill_type") or "").lower()
    transport = (row.get("transport_access") or "").lower()
    inc = (incident_type or "").lower()
    score = credits * 0.25 + trust * 20.0
    if same_zone:
        score += 42.0
    else:
        score += 10.0
    if inc and inc in skill:
        score += 20.0
    elif skill and (inc in ("medical", "logistics", "general") or skill in inc):
        score += 12.0
    if transport_needed and _transport_usable(transport):
        score += 14.0
    if shelter_needed and "logistics" in skill:
        score += 8.0
    return score


def _evaluate_candidate(
    row: dict[str, Any],
    *,
    same_zone: bool,
    incident_needs: set[str],
    incident_type: str,
    transport_needed: bool,
    shelter_needed: bool,
    food_needed: bool,
    injury: bool,
    child_present: bool,
    elderly: bool,
    user_preferred_language: str,
) -> dict[str, Any]:
    hard: list[str] = []
    if _availability_blocked(str(row.get("availability") or "")):
        hard.append("unavailable")
    if transport_needed and not _transport_usable(str(row.get("transport_access") or "")):
        hard.append("no transport access")

    vtypes = _volunteer_support_types(row)
    ok_sup, sup_reason = _support_compatible(incident_needs, vtypes)
    lang_ok, lang_reason = _language_compatible(user_preferred_language, _coerce_str_list(row.get("languages")))

    score = _base_score(
        row=row,
        same_zone=same_zone,
        incident_type=incident_type,
        transport_needed=transport_needed,
        shelter_needed=shelter_needed,
    )
    if not ok_sup:
        score -= 45.0
    if not lang_ok:
        score -= 28.0

    soft_notes: list[str] = []
    if not same_zone:
        soft_notes.append("outside primary zone")
    if sup_reason:
        soft_notes.append(sup_reason)
    if lang_reason:
        soft_notes.append(lang_reason)

    return {
        "row": row,
        "same_zone": same_zone,
        "hard": hard,
        "soft_notes": soft_notes,
        "score": score,
    }


def find_best_volunteer_assignment(tx: Any, engine: ResponseEngineInput) -> dict[str, Any]:
    """Return selected volunteer dict or None, rejected list with reasons, eta_minutes."""
    zone_id = engine.zone_id
    incident_type = engine.disaster_type
    transport_needed = engine.transport_needed
    shelter_needed = engine.shelter_needed
    food_needed = engine.food_needed
    injury = engine.injury
    child_present = engine.child_present
    elderly = engine.elderly
    user_preferred_language = engine.preferred_language

    incident_needs = _incident_support_needs(
        incident_type=incident_type,
        transport_needed=transport_needed,
        shelter_needed=shelter_needed,
        food_needed=food_needed,
        injury=injury,
        child_present=child_present,
        elderly=elderly,
    )

    same_zone_rows: list[dict[str, Any]] = [
        dict(r) for r in tx.run(matching_queries.VOLUNTEERS_IN_ZONE, zone_id=zone_id)
    ]
    other_zone_rows: list[dict[str, Any]] = [
        dict(r) for r in tx.run(matching_queries.VOLUNTEERS_OTHER_ZONES, zone_id=zone_id)
    ]

    evaluated: list[dict[str, Any]] = []
    for row in same_zone_rows:
        evaluated.append(
            _evaluate_candidate(
                row,
                same_zone=True,
                incident_needs=incident_needs,
                incident_type=incident_type,
                transport_needed=transport_needed,
                shelter_needed=shelter_needed,
                food_needed=food_needed,
                injury=injury,
                child_present=child_present,
                elderly=elderly,
                user_preferred_language=user_preferred_language,
            )
        )
    for row in other_zone_rows:
        evaluated.append(
            _evaluate_candidate(
                row,
                same_zone=False,
                incident_needs=incident_needs,
                incident_type=incident_type,
                transport_needed=transport_needed,
                shelter_needed=shelter_needed,
                food_needed=food_needed,
                injury=injury,
                child_present=child_present,
                elderly=elderly,
                user_preferred_language=user_preferred_language,
            )
        )

    if not evaluated:
        return {"selected": None, "rejected": [], "eta_minutes": None}

    eligible = [e for e in evaluated if not e["hard"]]
    eligible.sort(key=lambda e: e["score"], reverse=True)

    rejected: list[dict[str, str]] = []

    def rejection_reason(e: dict[str, Any]) -> str:
        if e["hard"]:
            return "; ".join(e["hard"])
        parts = [f"score {e['score']:.1f}"]
        parts.extend([n for n in e["soft_notes"] if n])
        return "; ".join(parts)

    if eligible:
        best = eligible[0]
        selected = {"id": best["row"].get("id"), "name": best["row"].get("name") or "Volunteer"}
        for e in eligible[1:8]:
            vid = str(e["row"].get("id") or "")
            nm = str(e["row"].get("name") or "")
            rejected.append({"volunteer_id": vid, "name": nm, "reason": rejection_reason(e)})
        for e in evaluated:
            if e is best:
                continue
            if e in eligible[1:8]:
                continue
            if e["hard"] and len(rejected) < 12:
                vid = str(e["row"].get("id") or "")
                nm = str(e["row"].get("name") or "")
                rejected.append({"volunteer_id": vid, "name": nm, "reason": rejection_reason(e)})
        eta = 18 if best["same_zone"] else 32
        return {"selected": selected, "rejected": rejected, "eta_minutes": eta}

    evaluated.sort(key=lambda e: e["score"], reverse=True)
    for e in evaluated[:10]:
        vid = str(e["row"].get("id") or "")
        nm = str(e["row"].get("name") or "")
        rejected.append({"volunteer_id": vid, "name": nm, "reason": rejection_reason(e)})
    return {"selected": None, "rejected": rejected, "eta_minutes": None}


def rejected_to_json(rejected: list[dict[str, str]]) -> str:
    return json.dumps(rejected)


def list_volunteer_ids_in_zone(tx: Any, zone_id: str) -> list[str]:
    ids: list[str] = []
    for r in tx.run(matching_queries.VOLUNTEERS_IN_ZONE, zone_id=zone_id):
        rid = r.get("id")
        if rid:
            ids.append(str(rid))
    return ids


def list_volunteer_ids_in_zone_sync(zone_id: str) -> list[str]:
    """Read-only fan-out helper for realtime (outside incident write transaction)."""
    if not zone_id.strip():
        return []
    driver = get_driver()
    settings = get_settings()

    def read(tx: Any) -> list[str]:
        return list_volunteer_ids_in_zone(tx, zone_id)

    with managed_neo4j_session(driver, settings) as session:
        return session.execute_read(read)


def get_best_match(*, incident_id: str, candidate_ids: list[str]) -> dict[str, Any]:
    """Lightweight response for coordinator snapshot demos. TODO: Neo4j-backed ranking."""
    return {
        "incident_id": incident_id,
        "candidate_ids": list(candidate_ids),
        "note": "Matching preview — use incident creation flow for real graph assignment.",
    }
