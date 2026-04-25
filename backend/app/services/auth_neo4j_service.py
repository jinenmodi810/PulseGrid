"""Persist registration flows to Neo4j (MERGE, unique ids)."""

from __future__ import annotations

import uuid
from typing import Any

from app.core.config import get_settings
from app.core.neo4j_client import get_driver, managed_neo4j_session
from app.db.queries import auth_queries
from app.models.auth_requests import (
    AdminLoginRequest,
    AdminLoginResponse,
    RegisterOrganizationRequest,
    RegisterOrganizationResponse,
    RegisterVolunteerRequest,
    RegisterVolunteerResponse,
)
from app.models.user_profile import UserProfileResponse


def _run_write(cypher: str, params: dict[str, Any]) -> dict[str, Any]:
    driver = get_driver()
    settings = get_settings()

    def work(tx: Any) -> dict[str, Any]:
        result = tx.run(cypher, **params)
        record = result.single()
        if record is None:
            return {}
        return dict(record)

    with managed_neo4j_session(driver, settings) as session:
        return session.execute_write(work)


def register_volunteer(body: RegisterVolunteerRequest) -> RegisterVolunteerResponse:
    volunteer_id = str(uuid.uuid4())
    skills = [s.strip() for s in body.skills if s and str(s).strip()]
    if not skills and (body.skill_type or "").strip():
        skills = [(body.skill_type or "").strip()]
    if not skills:
        skills = ["general"]
    support_types = [s.strip().lower() for s in body.support_types if s and str(s).strip()]
    if not support_types:
        support_types = ["general_support"]
    langs = [str(x).strip() for x in body.languages if str(x).strip()]
    if not langs:
        langs = ["en"]
    skill_type = skills[0]
    params = {
        "volunteer_id": volunteer_id,
        "full_name": body.full_name.strip(),
        "phone": body.phone.strip(),
        "skill_type": skill_type,
        "skills": skills,
        "support_types": support_types,
        "languages": langs,
        "transport_access": body.transport_access.strip(),
        "availability": (body.availability or "").strip(),
        "verified": body.verified,
        "zone_id": body.zone_id.strip(),
        "zone_name": body.zone_id.strip(),
    }
    row = _run_write(auth_queries.MERGE_VOLUNTEER_AND_ZONE, params)
    return RegisterVolunteerResponse(
        volunteer_id=row.get("volunteer_id", volunteer_id),
        zone_id=row.get("zone_id", body.zone_id),
    )


def register_organization(body: RegisterOrganizationRequest) -> RegisterOrganizationResponse:
    organization_id = str(uuid.uuid4())
    params = {
        "organization_id": organization_id,
        "name": body.name.strip(),
        "org_type": (body.org_type or "").strip().lower(),
        "phone": (body.phone or "").strip(),
        "zone_id": body.zone_id.strip(),
        "zone_name": body.zone_id.strip(),
        "beds_available": body.beds_available,
        "oxygen_units": body.oxygen_units,
        "ambulances_available": body.ambulances_available,
        "shelter_units": body.shelter_units,
        "food_capacity_units": body.food_capacity_units,
        "rescue_units": body.rescue_units,
    }
    row = _run_write(auth_queries.MERGE_ORGANIZATION_AND_ZONE, params)
    return RegisterOrganizationResponse(
        organization_id=row.get("organization_id", organization_id),
        zone_id=row.get("zone_id", body.zone_id),
    )


def get_user_profile(user_id: str) -> UserProfileResponse | None:
    """Load a registered User node for client profile / home screens."""

    def read(tx: Any) -> dict[str, Any] | None:
        rec = tx.run(auth_queries.GET_USER_BY_ID, user_id=user_id).single()
        return dict(rec) if rec else None

    driver = get_driver()
    settings = get_settings()
    with managed_neo4j_session(driver, settings) as session:
        row = session.execute_read(read)
    if not row or not row.get("user_id"):
        return None
    return UserProfileResponse(
        user_id=str(row["user_id"]),
        email=str(row.get("email") or ""),
        full_name=str(row.get("full_name") or ""),
        phone=str(row.get("phone") or ""),
        preferred_language=str(row.get("preferred_language") or "en"),
        zone_id=str(row.get("zone_id") or ""),
        household_size=int(row.get("household_size") or 1),
        elderly_count=int(row.get("elderly_count") or 0),
        mobility_concern=bool(row.get("mobility_concern")),
        oxygen_dependency=bool(row.get("oxygen_dependency")),
        emergency_contact_name=str(row.get("emergency_contact_name") or ""),
        emergency_contact_phone=str(row.get("emergency_contact_phone") or ""),
        emergency_contact_relationship=str(row.get("emergency_contact_relationship") or ""),
    )


def admin_login(body: AdminLoginRequest) -> AdminLoginResponse:
    # TODO(Phase1): replace with hashed passwords, MFA, and JWT issuance.
    settings = get_settings()
    if not settings.ADMIN_EMAIL or not settings.ADMIN_PASSWORD:
        return AdminLoginResponse(
            ok=False,
            detail="Admin login not configured: set ADMIN_EMAIL and ADMIN_PASSWORD in backend/.env, then restart the API.",
        )
    if body.email.strip().lower() != settings.ADMIN_EMAIL.strip().lower():
        return AdminLoginResponse(ok=False, detail="Invalid credentials.")
    if body.password != settings.ADMIN_PASSWORD:
        return AdminLoginResponse(ok=False, detail="Invalid credentials.")
    return AdminLoginResponse(ok=True, detail=None, session_marker=settings.ADMIN_SESSION_MARKER)


def dashboard_summary() -> dict[str, int]:
    from app.db.queries import dashboard_queries as dq

    driver = get_driver()
    settings = get_settings()

    queries = [
        ("active_incidents", dq.ACTIVE_INCIDENTS),
        ("available_volunteers", dq.AVAILABLE_VOLUNTEERS),
        ("hospitals_available", dq.HOSPITALS_AVAILABLE),
        ("shelters_available", dq.SHELTERS_AVAILABLE),
        ("pending_requests", dq.PENDING_REQUESTS),
        ("resolved_requests", dq.RESOLVED_REQUESTS),
    ]

    def read_all(tx: Any) -> dict[str, int]:
        out: dict[str, int] = {}
        for key, cypher in queries:
            rec = tx.run(cypher).single()
            out[key] = int(rec["c"]) if rec is not None else 0
        return out

    with managed_neo4j_session(driver, settings) as session:
        return session.execute_read(read_all)
