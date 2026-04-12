"""
Load JSON seed files into Neo4j using MERGE (idempotent).

Run from the `backend/` directory:
  python -m app.db.seed_data_loader

Or:
  python seed_data_loader.py
"""

from __future__ import annotations

import logging
from pathlib import Path

from dotenv import load_dotenv

from app.core.config import clear_settings_cache, get_settings
from app.core.neo4j_client import close_driver, get_driver, managed_neo4j_session
from app.db.queries import hospital_queries, incident_queries, rewards_queries, route_queries
from app.db.queries import support_queries as support_queries_mod
from app.utils.helpers import load_json_array

logger = logging.getLogger(__name__)

BACKEND_ROOT = Path(__file__).resolve().parents[2]
SEED_DIR = BACKEND_ROOT / "data" / "seed"

ALLOWED_LABELS = frozenset(
    {
        "User",
        "Incident",
        "Volunteer",
        "Responder",
        "Hospital",
        "Shelter",
        "SupportContact",
        "Zone",
        "Reward",
        "Organization",
    }
)

MERGE_USER_SEED = """
MERGE (u:User {id: $user_id})
SET u.full_name = $full_name,
    u.phone = $phone,
    u.preferred_language = $preferred_language,
    u.household_size = $household_size,
    u.family_size = $household_size,
    u.elderly_count = $elderly_count,
    u.mobility_concern = $mobility_concern,
    u.oxygen_dependency = $oxygen_dependency,
    u.emergency_contact_name = $emergency_contact_name,
    u.emergency_contact_phone = $emergency_contact_phone,
    u.emergency_contact_relationship = $emergency_contact_relationship
WITH u
MERGE (z:Zone {id: $zone_id})
ON CREATE SET z.name = $zone_name
MERGE (u)-[:LOCATED_IN]->(z)
"""

MERGE_VOLUNTEER_SEED = """
MERGE (v:Volunteer {id: $id})
SET v.display_name = $display_name,
    v.skills = $skills,
    v.skill_type = $skill_type,
    v.support_types = $support_types,
    v.languages = $languages,
    v.transport_access = $transport_access,
    v.availability = $availability,
    v.verified = coalesce($verified, true),
    v.credits = $credits,
    v.trust_score = $trust_score
WITH v
MERGE (z:Zone {id: $zone_id})
ON CREATE SET z.name = $zone_name
MERGE (v)-[:LOCATED_IN]->(z)
"""

MERGE_INCIDENT_SEED = """
MERGE (i:Incident {id: $id})
SET i.title = $title,
    i.incident_type = $incident_type,
    i.status = $status,
    i.severity = $severity,
    i.created_at = $created_at,
    i.zone_id = $zone_id,
    i.people_count = $people_count,
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
    i.route_status = 'pending',
    i.rejected_json = '[]',
    i.rejected_org_json = '[]',
    i.tier_reasons_json = '[]',
    i.decision_summary = $decision_summary,
    i.response_tier = $response_tier,
    i.escalation_required = $escalation_required,
    i.preferred_language = $preferred_language,
    i.ai_guidance = coalesce(i.ai_guidance, '')
"""

MERGE_ORGANIZATION_SEED = """
MERGE (o:Organization {id: $id})
SET o.name = $name,
    o.org_type = $org_type,
    o.phone = $phone,
    o.zone_id = $zone_id,
    o.active = true,
    o.beds_available = $beds_available,
    o.oxygen_units = $oxygen_units,
    o.ambulances_available = $ambulances_available,
    o.shelter_units = $shelter_units,
    o.food_capacity_units = $food_capacity_units,
    o.rescue_units = $rescue_units
WITH o
MERGE (z:Zone {id: $zone_id})
ON CREATE SET z.name = $zone_id
MERGE (o)-[:OPERATES_IN]->(z)
"""

MERGE_ZONE = """
MERGE (z:Zone {id: $id})
SET z.name = $name,
    z.notes = $notes
"""

MERGE_RESPONDER = """
MERGE (r:Responder {id: $id})
SET r.unit_name = $unit_name,
    r.role = $role,
    r.status = $status
"""

MERGE_SHELTER = """
MERGE (s:Shelter {id: $id})
SET s.name = $name,
    s.capacity = $capacity,
    s.occupancy = $occupancy,
    s.latitude = $latitude,
    s.longitude = $longitude
"""

DEMO_VOLUNTEER_HELP = """
MATCH (v:Volunteer {id: $vol_id})
MATCH (i:Incident {id: $incident_id})
MERGE (v)-[:CAN_HELP_WITH]->(i)
"""

DEMO_VERIFIED = """
MATCH (i:Incident {id: $incident_id})
MATCH (r:Responder {id: $responder_id})
MERGE (i)-[:VERIFIED_BY]->(r)
"""


def _seed_transaction(tx) -> None:
    for row in load_json_array(SEED_DIR / "zones.json"):
        tx.run(
            MERGE_ZONE,
            id=row["id"],
            name=row.get("name", ""),
            notes=row.get("notes", ""),
        )

    for row in load_json_array(SEED_DIR / "users.json"):
        tx.run(
            MERGE_USER_SEED,
            user_id=row["id"],
            full_name=row.get("full_name", ""),
            phone=row.get("phone", ""),
            preferred_language=row.get("preferred_language", "en"),
            household_size=int(row.get("household_size") or 1),
            elderly_count=int(row.get("elderly_count") or 0),
            mobility_concern=bool(row.get("mobility_concern", False)),
            oxygen_dependency=bool(row.get("oxygen_dependency", False)),
            emergency_contact_name=row.get("emergency_contact_name", ""),
            emergency_contact_phone=row.get("emergency_contact_phone", ""),
            emergency_contact_relationship=row.get("emergency_contact_relationship", ""),
            zone_id=row["zone_id"],
            zone_name=row["zone_id"],
        )

    for row in load_json_array(SEED_DIR / "organizations.json"):
        tx.run(
            MERGE_ORGANIZATION_SEED,
            id=row["id"],
            name=row.get("name", ""),
            org_type=row.get("org_type", "ngo"),
            phone=row.get("phone", ""),
            zone_id=row.get("zone_id", ""),
            beds_available=int(row.get("beds_available") or 0),
            oxygen_units=int(row.get("oxygen_units") or 0),
            ambulances_available=int(row.get("ambulances_available") or 0),
            shelter_units=int(row.get("shelter_units") or 0),
            food_capacity_units=int(row.get("food_capacity_units") or 0),
            rescue_units=int(row.get("rescue_units") or 0),
        )

    for row in load_json_array(SEED_DIR / "incidents.json"):
        tx.run(
            MERGE_INCIDENT_SEED,
            id=row["id"],
            title=row.get("title", ""),
            incident_type=row.get("incident_type", row.get("title", "incident")),
            status=row.get("status", "open"),
            severity=row.get("severity", "medium"),
            created_at=row.get("created_at"),
            zone_id=row.get("zone_id", ""),
            people_count=int(row.get("people_count") or 1),
            elderly=bool(row.get("elderly", False)),
            child_present=bool(row.get("child_present", False)),
            injury=bool(row.get("injury", False)),
            oxygen_required=bool(row.get("oxygen_required", False)),
            shelter_needed=bool(row.get("shelter_needed", False)),
            food_needed=bool(row.get("food_needed", False)),
            transport_needed=bool(row.get("transport_needed", False)),
            note=str(row.get("note", "")),
            priority_score=float(row.get("priority_score") or 0),
            priority_label=str(row.get("priority_label", "MEDIUM")),
            decision_summary=str(row.get("decision_summary", "Demo seed incident.")),
            response_tier=str(row.get("response_tier", "volunteer_only")),
            escalation_required=bool(row.get("escalation_required", False)),
            preferred_language=str(row.get("preferred_language", "en")),
        )
        zid = row.get("zone_id")
        if zid:
            tx.run(
                incident_queries.LINK_INCIDENT_TO_ZONE,
                incident_id=row["id"],
                zone_id=zid,
                zone_name=zid,
            )
        reporter = row.get("reporter_user_id")
        if reporter:
            tx.run(
                """
                MATCH (u:User {id: $uid})
                MATCH (i:Incident {id: $iid})
                MERGE (u)-[:REPORTED]->(i)
                """,
                uid=str(reporter),
                iid=row["id"],
            )

    for row in load_json_array(SEED_DIR / "volunteers.json"):
        tx.run(
            MERGE_VOLUNTEER_SEED,
            id=row["id"],
            display_name=row.get("display_name", ""),
            skills=row.get("skills") or [],
            skill_type=row.get("skill_type", "general"),
            support_types=row.get("support_types") or ["general_support"],
            languages=row.get("languages") or ["en"],
            transport_access=row.get("transport_access", "none"),
            availability=row.get("availability", "available"),
            verified=bool(row.get("verified", True)),
            credits=int(row.get("credits") or 0),
            trust_score=float(row.get("trust_score") or 0.5),
            zone_id=row["zone_id"],
            zone_name=row.get("zone_name") or row["zone_id"],
        )

    for row in load_json_array(SEED_DIR / "hospitals.json"):
        tx.run(
            hospital_queries.MERGE_HOSPITAL,
            id=row["id"],
            name=row.get("name", ""),
            beds_available=int(row.get("beds_available") or 0),
            latitude=row.get("latitude"),
            longitude=row.get("longitude"),
        )

    for row in load_json_array(SEED_DIR / "shelters.json"):
        tx.run(
            MERGE_SHELTER,
            id=row["id"],
            name=row.get("name", ""),
            capacity=int(row.get("capacity") or 0),
            occupancy=int(row.get("occupancy") or 0),
            latitude=row.get("latitude"),
            longitude=row.get("longitude"),
        )

    for row in load_json_array(SEED_DIR / "responders.json"):
        tx.run(
            MERGE_RESPONDER,
            id=row["id"],
            unit_name=row.get("unit_name", ""),
            role=row.get("role", ""),
            status=row.get("status", ""),
        )

    for row in load_json_array(SEED_DIR / "support_contacts.json"):
        tx.run(
            support_queries_mod.MERGE_SUPPORT_CONTACT,
            id=row["id"],
            label=row.get("label", ""),
            phone=row.get("phone", ""),
            type=row.get("type", "other"),
        )

    for row in load_json_array(SEED_DIR / "rewards.json"):
        tx.run(
            rewards_queries.MERGE_REWARD,
            id=row["id"],
            title=row.get("title", ""),
            description=row.get("description", ""),
            badge_type=row.get("badge_type", "bronze"),
            credits_value=int(row.get("credits_value") or 0),
        )

    for row in load_json_array(SEED_DIR / "routes.json"):
        fl = row.get("from_label") or "Incident"
        tl = row.get("to_label") or "Hospital"
        if fl not in ALLOWED_LABELS or tl not in ALLOWED_LABELS:
            logger.warning("Skipping route with invalid labels: %s -> %s", fl, tl)
            continue
        q = route_queries.merge_route_to(fl, tl)
        tx.run(
            q,
            from_id=row["from_id"],
            to_id=row["to_id"],
            distance_km=float(row.get("distance_km") or 0),
            eta_minutes=int(row.get("eta_minutes") or 0),
            edge_id=row.get("id", ""),
        )

    vols = load_json_array(SEED_DIR / "volunteers.json")
    incs = load_json_array(SEED_DIR / "incidents.json")
    rsps = load_json_array(SEED_DIR / "responders.json")
    orgs = load_json_array(SEED_DIR / "organizations.json")
    if vols and incs:
        tx.run(DEMO_VOLUNTEER_HELP, vol_id=vols[0]["id"], incident_id=incs[0]["id"])
    if incs and rsps:
        tx.run(DEMO_VERIFIED, incident_id=incs[0]["id"], responder_id=rsps[0]["id"])
    if incs and orgs:
        tx.run(
            """
            MATCH (i:Incident {id: $iid})
            MATCH (o:Organization {id: $oid})
            SET i.assigned_organization_id = o.id,
                i.assigned_organization_name = o.name,
                i.assigned_organization_type = o.org_type,
                i.response_tier = 'volunteer_plus_organization',
                i.escalation_required = false
            """,
            iid=incs[0]["id"],
            oid=orgs[0]["id"],
        )


def run_seed() -> None:
    """MERGE all seed JSON into Neo4j."""
    load_dotenv(BACKEND_ROOT / ".env")
    clear_settings_cache()

    driver = get_driver()
    settings = get_settings()

    with managed_neo4j_session(driver, settings) as session:
        session.execute_write(_seed_transaction)

    logger.info("Seed completed successfully (database=%r).", settings.neo4j_database_display())


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    try:
        run_seed()
    finally:
        close_driver()


if __name__ == "__main__":
    main()
