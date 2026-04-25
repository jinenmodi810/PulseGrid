"""Post-commit Neo4j projections mirroring PostgreSQL entities.

Secrets (passwords, hashes, tokens) must never be written to the graph from this module.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from neo4j.exceptions import Neo4jError

from app.core.config import Settings, get_settings
from app.core.neo4j_client import get_driver, managed_neo4j_session
from app.db.sql.enums import UserRole

_log = logging.getLogger("pulsegrid.neo4j_projection")


@dataclass(frozen=True)
class ProjectionResult:
    ok: bool
    skipped: bool
    detail: str | None = None


@dataclass(frozen=True)
class VictimGraphProjectionInput:
    """Safe, post-commit payload for syncing a victim account into Neo4j (no secrets)."""

    user_id: str
    email: str
    full_name: str
    phone: str
    preferred_language: str
    household_size: int
    elderly_count: int
    mobility_concern: bool
    oxygen_dependency: bool
    emergency_contact_name: str
    emergency_contact_phone: str
    emergency_contact_relationship: str
    zone_id: str
    zone_name: str


def project_victim_account_from_pg(*, settings: Settings, payload: VictimGraphProjectionInput) -> ProjectionResult:
    """Upsert ``:User`` + ``:Zone`` + ``LOCATED_IN`` after PostgreSQL commit. Never writes password/hash."""
    driver = get_driver()
    params: dict[str, Any] = {
        "user_id": payload.user_id,
        "email": payload.email.strip(),
        "full_name": payload.full_name.strip(),
        "phone": (payload.phone or "").strip(),
        "preferred_language": payload.preferred_language.strip() or "en",
        "household_size": int(payload.household_size),
        "elderly_count": int(payload.elderly_count),
        "mobility_concern": bool(payload.mobility_concern),
        "oxygen_dependency": bool(payload.oxygen_dependency),
        "emergency_contact_name": payload.emergency_contact_name.strip(),
        "emergency_contact_phone": payload.emergency_contact_phone.strip(),
        "emergency_contact_relationship": (payload.emergency_contact_relationship or "").strip(),
        "zone_id": payload.zone_id.strip(),
        "zone_name": payload.zone_name.strip(),
    }
    cypher = """
    MERGE (u:User {id: $user_id})
    SET u.email = $email,
        u.full_name = $full_name,
        u.phone = $phone,
        u.preferred_language = $preferred_language,
        u.household_size = $household_size,
        u.family_size = $household_size,
        u.elderly_count = $elderly_count,
        u.mobility_concern = $mobility_concern,
        u.oxygen_dependency = $oxygen_dependency,
        u.emergency_contact_name = $emergency_contact_name,
        u.emergency_contact_phone = $emergency_contact_phone,
        u.emergency_contact_relationship = $emergency_contact_relationship,
        u.pg_source_of_truth = true,
        u.updated_at = datetime()
    REMOVE u.password_hash
    WITH u
    MERGE (z:Zone {id: $zone_id})
    ON CREATE SET z.name = $zone_name
    MERGE (u)-[:LOCATED_IN]->(z)
    RETURN u.id AS ok_id
    """
    try:
        with managed_neo4j_session(driver, settings) as session:
            session.run(cypher, **params)
        _log.info("neo4j_victim_projection_ok", extra={"user_id": payload.user_id})
        return ProjectionResult(ok=True, skipped=False, detail=None)
    except Neo4jError as exc:
        _log.error(
            "neo4j_victim_projection_failed",
            extra={"user_id": payload.user_id, "neo4j_code": getattr(exc, "code", None)},
        )
        return ProjectionResult(ok=False, skipped=False, detail=str(exc))
    except Exception as exc:  # noqa: BLE001
        _log.exception("neo4j_victim_projection_failed", extra={"user_id": payload.user_id})
        return ProjectionResult(ok=False, skipped=False, detail=str(exc))


@dataclass(frozen=True)
class VolunteerGraphProjectionInput:
    """Safe payload for syncing a volunteer ``users`` + ``responder_profiles`` row into Neo4j."""

    volunteer_id: str
    email: str
    display_name: str
    phone: str
    skills: list[str]
    support_types: list[str]
    languages: list[str]
    transport_access: str
    availability: str
    verified: bool
    skill_type: str
    zone_id: str
    zone_name: str
    credits: int
    trust_score: float


def project_volunteer_account_from_pg(*, settings: Settings, payload: VolunteerGraphProjectionInput) -> ProjectionResult:
    """Upsert ``:Volunteer`` + ``:Zone`` + ``LOCATED_IN`` after PostgreSQL commit. Never writes password/hash."""
    driver = get_driver()
    params: dict[str, Any] = {
        "id": payload.volunteer_id,
        "email": payload.email.strip(),
        "display_name": payload.display_name.strip(),
        "phone": (payload.phone or "").strip(),
        "skills": list(payload.skills),
        "support_types": list(payload.support_types),
        "languages": list(payload.languages),
        "transport_access": payload.transport_access.strip(),
        "availability": (payload.availability or "").strip(),
        "verified": bool(payload.verified),
        "skill_type": (payload.skill_type or "").strip(),
        "credits": int(payload.credits),
        "trust_score": float(payload.trust_score),
        "zone_id": payload.zone_id.strip(),
        "zone_name": payload.zone_name.strip(),
    }
    cypher = """
    MERGE (v:Volunteer {id: $id})
    SET v.email = $email,
        v.display_name = $display_name,
        v.phone = $phone,
        v.skills = $skills,
        v.support_types = $support_types,
        v.languages = $languages,
        v.transport_access = $transport_access,
        v.availability = $availability,
        v.verified = $verified,
        v.skill_type = $skill_type,
        v.credits = $credits,
        v.trust_score = $trust_score,
        v.pg_source_of_truth = true,
        v.updated_at = datetime()
    REMOVE v.password_hash
    WITH v
    MERGE (z:Zone {id: $zone_id})
    ON CREATE SET z.name = $zone_name
    MERGE (v)-[:LOCATED_IN]->(z)
    RETURN v.id AS ok_id
    """
    try:
        with managed_neo4j_session(driver, settings) as session:
            session.run(cypher, **params)
        _log.info("neo4j_volunteer_projection_ok", extra={"volunteer_id": payload.volunteer_id})
        return ProjectionResult(ok=True, skipped=False, detail=None)
    except Neo4jError as exc:
        _log.error(
            "neo4j_volunteer_projection_failed",
            extra={"volunteer_id": payload.volunteer_id, "neo4j_code": getattr(exc, "code", None)},
        )
        return ProjectionResult(ok=False, skipped=False, detail=str(exc))
    except Exception as exc:  # noqa: BLE001
        _log.exception("neo4j_volunteer_projection_failed", extra={"volunteer_id": payload.volunteer_id})
        return ProjectionResult(ok=False, skipped=False, detail=str(exc))


@dataclass(frozen=True)
class OrganizationGraphProjectionInput:
    """Safe payload for syncing a committed ``organizations`` row into Neo4j (no password/hash)."""

    organization_id: str
    name: str
    org_type: str
    contact_phone: str
    contact_name: str
    contact_email: str
    primary_zone_id: str
    primary_zone_name: str
    coverage_zone_ids: list[str]
    beds_available: int
    oxygen_units: int
    ambulances_available: int
    shelter_units: int
    food_capacity_units: int
    rescue_units: int
    active: bool


def project_organization_account_from_pg(
    *, settings: Settings, payload: OrganizationGraphProjectionInput
) -> ProjectionResult:
    """Upsert ``:Organization`` + zones + ``OPERATES_IN`` / ``COVERS``. Never writes password/hash."""
    driver = get_driver()
    params: dict[str, Any] = {
        "organization_id": payload.organization_id.strip(),
        "name": payload.name.strip(),
        "org_type": (payload.org_type or "").strip().lower(),
        "contact_phone": (payload.contact_phone or "").strip(),
        "contact_name": payload.contact_name.strip(),
        "contact_email": payload.contact_email.strip().lower(),
        "primary_zone_id": payload.primary_zone_id.strip(),
        "primary_zone_name": payload.primary_zone_name.strip(),
        "coverage_zone_ids": list(payload.coverage_zone_ids),
        "beds_available": int(payload.beds_available),
        "oxygen_units": int(payload.oxygen_units),
        "ambulances_available": int(payload.ambulances_available),
        "shelter_units": int(payload.shelter_units),
        "food_capacity_units": int(payload.food_capacity_units),
        "rescue_units": int(payload.rescue_units),
        "active": bool(payload.active),
    }
    cypher = """
    MERGE (o:Organization {id: $organization_id})
    SET o.name = $name,
        o.org_type = $org_type,
        o.phone = $contact_phone,
        o.contact_name = $contact_name,
        o.contact_email = $contact_email,
        o.active = $active,
        o.beds_available = $beds_available,
        o.oxygen_units = $oxygen_units,
        o.ambulances_available = $ambulances_available,
        o.shelter_units = $shelter_units,
        o.food_capacity_units = $food_capacity_units,
        o.rescue_units = $rescue_units,
        o.zone_id = $primary_zone_id,
        o.pg_source_of_truth = true,
        o.updated_at = datetime()
    REMOVE o.password_hash
    WITH o
    OPTIONAL MATCH (o)-[rc:COVERS]->(:Zone)
    DELETE rc
    WITH o
    MERGE (z:Zone {id: $primary_zone_id})
    ON CREATE SET z.name = $primary_zone_name
    MERGE (o)-[:OPERATES_IN]->(z)
    WITH o
    UNWIND $coverage_zone_ids AS zid
    MERGE (cz:Zone {id: zid})
    ON CREATE SET cz.name = zid
    MERGE (o)-[:COVERS]->(cz)
    RETURN o.id AS ok_id
    """
    try:
        with managed_neo4j_session(driver, settings) as session:
            session.run(cypher, **params)
        _log.info("neo4j_organization_projection_ok", extra={"organization_id": payload.organization_id})
        return ProjectionResult(ok=True, skipped=False, detail=None)
    except Neo4jError as exc:
        _log.error(
            "neo4j_organization_projection_failed",
            extra={"organization_id": payload.organization_id, "neo4j_code": getattr(exc, "code", None)},
        )
        return ProjectionResult(ok=False, skipped=False, detail=str(exc))
    except Exception as exc:  # noqa: BLE001
        _log.exception("neo4j_organization_projection_failed", extra={"organization_id": payload.organization_id})
        return ProjectionResult(ok=False, skipped=False, detail=str(exc))


def project_user_from_pg(
    *,
    settings: Settings,
    user_id: str,
    email: str,
    full_name: str,
    phone: str | None,
    role: UserRole,
) -> ProjectionResult:
    """Upsert graph nodes that correspond to a committed ``users`` row.

    Flow: PostgreSQL transaction commits first; callers invoke this afterward.
    On failure, log at ERROR with structured context — safe to enqueue for retry externally.
    """
    if role is UserRole.organization:
        _log.info(
            "neo4j_projection_skipped",
            extra={"reason": "organization_contact_projection_not_yet_modeled", "user_id": user_id},
        )
        return ProjectionResult(ok=True, skipped=True, detail="organization_role_skipped")

    driver = get_driver()
    params: dict[str, Any] = {
        "id": user_id,
        "email": email.strip(),
        "full_name": full_name.strip(),
        "phone": (phone or "").strip() or None,
    }

    try:
        with managed_neo4j_session(driver, settings) as session:
            if role is UserRole.volunteer:
                cypher = """
                MERGE (v:Volunteer {id: $id})
                SET v.display_name = $full_name,
                    v.email = $email,
                    v.phone = coalesce($phone, v.phone),
                    v.pg_source_of_truth = true,
                    v.updated_at = datetime()
                RETURN v.id AS id
                """
                session.run(cypher, **params)
            else:
                # admin (or legacy bootstrap): minimal :User mirror — victims use ``project_victim_account_from_pg``.
                cypher = """
                MERGE (u:User {id: $id})
                SET u.email = $email,
                    u.full_name = $full_name,
                    u.phone = coalesce($phone, u.phone),
                    u.role = $role,
                    u.pg_source_of_truth = true,
                    u.updated_at = datetime()
                REMOVE u.password_hash
                RETURN u.id AS id
                """
                session.run(
                    cypher,
                    id=params["id"],
                    email=params["email"],
                    full_name=params["full_name"],
                    phone=params["phone"],
                    role=role.value,
                )
        _log.info("neo4j_user_projection_ok", extra={"user_id": user_id, "role": role.value})
        return ProjectionResult(ok=True, skipped=False, detail=None)
    except Neo4jError as exc:
        _log.error(
            "neo4j_user_projection_failed",
            extra={"user_id": user_id, "role": role.value, "neo4j_code": getattr(exc, "code", None)},
        )
        return ProjectionResult(ok=False, skipped=False, detail=str(exc))
    except Exception as exc:  # noqa: BLE001
        _log.exception("neo4j_user_projection_failed", extra={"user_id": user_id, "role": role.value})
        return ProjectionResult(ok=False, skipped=False, detail=str(exc))


def project_user_with_retry(
    *,
    settings: Settings | None = None,
    user_id: str,
    email: str,
    full_name: str,
    phone: str | None,
    role: UserRole,
    max_attempts: int = 1,
) -> ProjectionResult:
    """Thin wrapper reserved for future broker-backed retries (``max_attempts`` > 1)."""
    cfg = settings or get_settings()
    last: ProjectionResult | None = None
    for attempt in range(1, max(max_attempts, 1) + 1):
        last = project_user_from_pg(
            settings=cfg,
            user_id=user_id,
            email=email,
            full_name=full_name,
            phone=phone,
            role=role,
        )
        if last.ok:
            return last
        _log.warning(
            "neo4j_projection_retry_scheduled",
            extra={"user_id": user_id, "attempt": attempt, "max_attempts": max_attempts},
        )
    assert last is not None
    return last
