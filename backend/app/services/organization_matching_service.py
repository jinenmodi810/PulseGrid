"""Organization / institutional matching — separate from volunteer scoring and tier rules."""

from __future__ import annotations

import json
import re
from typing import Any

from app.db.queries import matching_queries
from app.models.response_engine_models import ResponseEngineInput


def _norm(s: str) -> str:
    return (s or "").strip().lower()


def _tags(incident_type: str) -> set[str]:
    t = _norm(incident_type)
    tags: set[str] = set()
    if re.search(r"\bfood\b|food_support|hunger|meal", t):
        tags.add("food")
    if re.search(r"\bflood\b|flooding", t):
        tags.add("flood")
    if re.search(r"\bfire\b|wildfire|burn", t):
        tags.add("fire")
    if re.search(r"\bearthquake\b|seismic|collapse|structural", t):
        tags.add("earthquake")
    if re.search(r"\bmedical\b|clinic|hospital|ambulance|trauma", t):
        tags.add("medical")
    return tags


def _org_type_bucket(org_type: str) -> set[str]:
    o = _norm(org_type)
    out: set[str] = set()
    if "hospital" in o or "clinic" in o or "medical" in o:
        out.add("medical")
    if "fire" in o or "fd" in o or "brigade" in o:
        out.add("fire")
    if "rescue" in o or "emergency" in o or "response" in o:
        out.add("rescue")
    if "ngo" in o or "relief" in o or "charity" in o or "shelter" in o:
        out.add("ngo")
    if "food" in o or "kitchen" in o:
        out.add("food")
    return out or {"general"}


def _evaluate_org(
    row: dict[str, Any],
    *,
    same_zone: bool,
    zone_id: str,
    incident_type: str,
    injury: bool,
    oxygen_required: bool,
    shelter_needed: bool,
    food_needed: bool,
    transport_needed: bool,
    people_count: int,
) -> dict[str, Any]:
    hard: list[str] = []
    tags = _tags(incident_type)
    ot = _org_type_bucket(str(row.get("org_type") or ""))
    beds = int(row.get("beds_available") or 0)
    oxy = int(row.get("oxygen_units") or 0)
    amb = int(row.get("ambulances_available") or 0)
    shelter_u = int(row.get("shelter_units") or 0)
    food_u = int(row.get("food_capacity_units") or 0)
    rescue = int(row.get("rescue_units") or 0)

    if row.get("active") is False:
        hard.append("organization inactive")
    if row.get("verified") is False:
        hard.append("organization unverified")

    need_medical = bool(injury or oxygen_required or "medical" in tags)
    need_shelter = bool(shelter_needed or people_count >= 4)
    need_food = bool(food_needed or "food" in tags)
    need_rescue = bool("fire" in tags or "earthquake" in tags)

    if oxygen_required and oxy < 1:
        hard.append("no oxygen support")
    if injury and beds < 1 and amb < 1:
        hard.append("no available beds")
    if shelter_needed and shelter_u < 1:
        hard.append("shelter full")
    if "fire" in tags and rescue < 1 and amb < 1:
        hard.append("disaster type unsupported")
    if "earthquake" in tags and rescue < 1 and shelter_u < 1 and beds < 1:
        hard.append("disaster type unsupported")
    if need_medical and "medical" not in ot and "rescue" not in ot and "ngo" not in ot and beds < 1 and amb < 1:
        if injury or oxygen_required:
            hard.append("support type mismatch")

    if food_needed and food_u < 1 and "food" not in ot and "ngo" not in ot:
        hard.append("support type mismatch")

    if not same_zone and str(row.get("zone_id") or "") != zone_id:
        pass  # allowed fallback; soft penalty only

    score = 20.0
    if same_zone:
        score += 50.0
    else:
        score += 8.0
    if need_medical and ("medical" in ot or beds > 0 or amb > 0):
        score += 35.0
    if oxygen_required and oxy > 0:
        score += 40.0
    if shelter_needed and shelter_u > 0:
        score += 22.0
    if need_food and food_u > 0:
        score += 15.0
    if transport_needed and amb > 0:
        score += 18.0
    if need_rescue and rescue > 0:
        score += 30.0

    soft: list[str] = []
    if not same_zone:
        soft.append("zone not covered")

    return {"row": row, "same_zone": same_zone, "hard": hard, "soft": soft, "score": score}


def find_best_organization_assignment(tx: Any, engine: ResponseEngineInput) -> dict[str, Any]:
    """Return selected organization dict or None, rejected list, optional eta placeholder."""
    zone_id = engine.zone_id
    incident_type = engine.disaster_type
    injury = engine.injury
    oxygen_required = engine.oxygen_required
    shelter_needed = engine.shelter_needed
    food_needed = engine.food_needed
    transport_needed = engine.transport_needed
    people_count = engine.people_count

    in_zone = [dict(r) for r in tx.run(matching_queries.ORGANIZATIONS_IN_ZONE, zone_id=zone_id)]
    fallback = [dict(r) for r in tx.run(matching_queries.ORGANIZATIONS_FALLBACK)]
    seen: set[str] = set()
    rows: list[tuple[dict[str, Any], bool]] = []
    for r in in_zone:
        oid = str(r.get("id") or "")
        if oid and oid not in seen:
            seen.add(oid)
            rows.append((r, True))
    for r in fallback:
        oid = str(r.get("id") or "")
        if oid and oid not in seen:
            seen.add(oid)
            rows.append((r, str(r.get("zone_id") or "") == zone_id))

    evaluated = [
        _evaluate_org(
            r,
            same_zone=same_zone,
            zone_id=zone_id,
            incident_type=incident_type,
            injury=injury,
            oxygen_required=oxygen_required,
            shelter_needed=shelter_needed,
            food_needed=food_needed,
            transport_needed=transport_needed,
            people_count=max(1, int(people_count or 1)),
        )
        for r, same_zone in rows
    ]

    if not evaluated:
        return {"selected": None, "rejected": [], "eta_minutes": None}

    eligible = [e for e in evaluated if not e["hard"]]
    eligible.sort(key=lambda e: e["score"], reverse=True)
    rejected: list[dict[str, str]] = []

    def reason(e: dict[str, Any]) -> str:
        if e["hard"]:
            return "; ".join(e["hard"])
        parts = [f"score {e['score']:.1f}"] + e["soft"]
        return "; ".join(p for p in parts if p)

    if eligible:
        best = eligible[0]
        selected = {
            "id": best["row"].get("id"),
            "name": best["row"].get("name") or "Organization",
            "org_type": str(best["row"].get("org_type") or ""),
        }
        for e in eligible[1:8]:
            oid = str(e["row"].get("id") or "")
            nm = str(e["row"].get("name") or "")
            rejected.append({"organization_id": oid, "name": nm, "reason": reason(e)})
        for e in evaluated:
            if e is best or e in eligible[1:8]:
                continue
            if e["hard"] and len(rejected) < 14:
                oid = str(e["row"].get("id") or "")
                nm = str(e["row"].get("name") or "")
                rejected.append({"organization_id": oid, "name": nm, "reason": reason(e)})
        eta = 25 if best["same_zone"] else 45
        return {"selected": selected, "rejected": rejected, "eta_minutes": eta}

    evaluated.sort(key=lambda e: e["score"], reverse=True)
    for e in evaluated[:12]:
        oid = str(e["row"].get("id") or "")
        nm = str(e["row"].get("name") or "")
        rejected.append({"organization_id": oid, "name": nm, "reason": reason(e)})
    return {"selected": None, "rejected": rejected, "eta_minutes": None}


def rejected_org_to_json(rejected: list[dict[str, str]]) -> str:
    return json.dumps(rejected)
