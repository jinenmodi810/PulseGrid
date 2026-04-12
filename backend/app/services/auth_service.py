"""Email/password registration, login, and /auth/me assembly (Neo4j + JWT)."""

from __future__ import annotations

import logging
import uuid
from typing import Any

from fastapi import HTTPException

_log = logging.getLogger("pulsegrid.auth")

from app.core.config import get_settings
from app.core.neo4j_client import get_driver, managed_neo4j_session
from app.core.security import create_access_token, hash_password, verify_password
from app.db.queries import auth_queries
from app.models.auth_models import AccessTokenResponse, AuthMeResponse
from app.models.auth_requests import (
    LoginOrganizationRequest,
    LoginVictimRequest,
    LoginVolunteerRequest,
    RegisterOrganizationAuthRequest,
    RegisterVictimAuthRequest,
    RegisterVolunteerAuthRequest,
)


def _execute_read(query: str, params: dict[str, Any]) -> list[dict[str, Any]]:
    driver = get_driver()
    settings = get_settings()

    def work(tx: Any) -> list[dict[str, Any]]:
        result = tx.run(query, **params)
        return [dict(r) for r in result]

    with managed_neo4j_session(driver, settings) as session:
        return session.execute_read(work)


def _execute_read_one(query: str, params: dict[str, Any]) -> dict[str, Any] | None:
    rows = _execute_read(query, params)
    return rows[0] if rows else None


def _execute_write(query: str, params: dict[str, Any]) -> dict[str, Any]:
    driver = get_driver()
    settings = get_settings()

    def work(tx: Any) -> dict[str, Any]:
        rec = tx.run(query, **params).single()
        return dict(rec) if rec else {}

    with managed_neo4j_session(driver, settings) as session:
        return session.execute_write(work)


def _issue(role: str, entity_id: str) -> AccessTokenResponse:
    tok = create_access_token(subject=entity_id, role=role)
    return AccessTokenResponse(access_token=tok, role=role, id=entity_id)  # type: ignore[arg-type]


def register_victim(body: RegisterVictimAuthRequest) -> AccessTokenResponse:
    email = str(body.email).strip()
    existing = _execute_read_one(auth_queries.FIND_USER_BY_EMAIL, {"email": email})
    if existing and existing.get("id"):
        raise HTTPException(status_code=409, detail="An account with this email already exists.")
    user_id = str(uuid.uuid4())
    hs = body.household_size if body.household_size is not None else 1
    params = {
        "user_id": user_id,
        "email": email,
        "password_hash": hash_password(body.password),
        "full_name": body.full_name.strip(),
        "phone": body.phone.strip(),
        "preferred_language": (body.preferred_language or "en").strip() or "en",
        "household_size": hs,
        "elderly_count": int(body.elderly_count),
        "mobility_concern": bool(body.mobility_concern),
        "oxygen_dependency": bool(body.oxygen_dependency),
        "emergency_contact_name": body.emergency_contact_name.strip(),
        "emergency_contact_phone": body.emergency_contact_phone.strip(),
        "emergency_contact_relationship": (body.emergency_contact_relationship or "").strip(),
        "zone_id": body.home_zone_id.strip(),
        "zone_name": body.home_zone_id.strip(),
    }
    row = _execute_write(auth_queries.CREATE_USER_WITH_PASSWORD, params)
    uid = str(row.get("user_id") or user_id)
    _log.info("neo4j write ok: register_victim id=%s", uid)
    return _issue("victim", uid)


def login_victim(body: LoginVictimRequest) -> AccessTokenResponse:
    email = str(body.email).strip()
    row = _execute_read_one(auth_queries.FIND_USER_BY_EMAIL, {"email": email})
    if not row or not row.get("id"):
        raise HTTPException(status_code=401, detail="Incorrect email or password.")
    ph = str(row.get("password_hash") or "")
    if not ph or not verify_password(body.password, ph):
        raise HTTPException(status_code=401, detail="Incorrect email or password.")
    uid = str(row["id"])
    _log.info("neo4j read ok: login_victim id=%s", uid)
    return _issue("victim", uid)


def register_volunteer(body: RegisterVolunteerAuthRequest) -> AccessTokenResponse:
    email = str(body.email).strip()
    existing = _execute_read_one(auth_queries.FIND_VOLUNTEER_BY_EMAIL, {"email": email})
    if existing and existing.get("id"):
        raise HTTPException(status_code=409, detail="An account with this email already exists.")
    skills = [s.strip() for s in body.skills if s and str(s).strip()]
    if not skills:
        skills = ["general"]
    support_types = [s.strip().lower() for s in body.support_types if s and str(s).strip()]
    if not support_types:
        support_types = ["general_support"]
    langs = [str(x).strip() for x in body.languages if str(x).strip()]
    if not langs:
        langs = ["en"]
    skill_type = skills[0]
    volunteer_id = str(uuid.uuid4())
    params = {
        "volunteer_id": volunteer_id,
        "email": email,
        "password_hash": hash_password(body.password),
        "full_name": body.full_name.strip(),
        "phone": body.phone.strip(),
        "skill_type": skill_type,
        "skills": skills,
        "support_types": support_types,
        "languages": langs,
        "transport_access": body.transport_access.strip(),
        "availability": (body.availability or "").strip(),
        "verified": bool(body.verified),
        "zone_id": body.zone_id.strip(),
        "zone_name": body.zone_id.strip(),
    }
    row = _execute_write(auth_queries.CREATE_VOLUNTEER_WITH_PASSWORD, params)
    vid = str(row.get("volunteer_id") or volunteer_id)
    _log.info("neo4j write ok: register_volunteer id=%s", vid)
    return _issue("volunteer", vid)


def login_volunteer(body: LoginVolunteerRequest) -> AccessTokenResponse:
    email = str(body.email).strip()
    row = _execute_read_one(auth_queries.FIND_VOLUNTEER_BY_EMAIL, {"email": email})
    if not row or not row.get("id"):
        raise HTTPException(status_code=401, detail="Incorrect email or password.")
    ph = str(row.get("password_hash") or "")
    if not ph or not verify_password(body.password, ph):
        raise HTTPException(status_code=401, detail="Incorrect email or password.")
    vid = str(row["id"])
    _log.info("neo4j read ok: login_volunteer id=%s", vid)
    return _issue("volunteer", vid)


def register_organization(body: RegisterOrganizationAuthRequest) -> AccessTokenResponse:
    email = str(body.contact_email).strip()
    existing = _execute_read_one(auth_queries.FIND_ORGANIZATION_BY_CONTACT_EMAIL, {"email": email})
    if existing and existing.get("id"):
        raise HTTPException(status_code=409, detail="An account with this email already exists.")
    organization_id = str(uuid.uuid4())
    zone_ids = [z.strip() for z in body.coverage_zone_ids if z and str(z).strip()]
    primary = body.zone_id.strip()
    if primary not in zone_ids:
        zone_ids = [primary, *zone_ids]
    params = {
        "organization_id": organization_id,
        "name": body.organization_name.strip(),
        "org_type": (body.organization_type or "").strip().lower(),
        "contact_phone": body.contact_phone.strip(),
        "contact_name": body.contact_name.strip(),
        "contact_email": email,
        "password_hash": hash_password(body.password),
        "zone_id": primary,
        "zone_name": primary,
        "beds_available": body.beds_available,
        "oxygen_units": body.oxygen_units,
        "ambulances_available": body.ambulances_available,
        "shelter_units": body.shelter_units,
        "food_capacity_units": body.food_capacity_units,
        "rescue_units": body.rescue_units,
    }
    row = _execute_write(auth_queries.CREATE_ORGANIZATION_WITH_PASSWORD, params)
    oid = str(row.get("organization_id") or organization_id)
    _execute_write(auth_queries.MERGE_ORGANIZATION_COVERS_ZONES, {"organization_id": oid, "zone_ids": zone_ids})
    _log.info("neo4j write ok: register_organization id=%s", oid)
    return _issue("organization", oid)


def login_organization(body: LoginOrganizationRequest) -> AccessTokenResponse:
    email = str(body.email).strip()
    row = _execute_read_one(auth_queries.FIND_ORGANIZATION_BY_CONTACT_EMAIL, {"email": email})
    if not row or not row.get("id"):
        raise HTTPException(status_code=401, detail="Incorrect email or password.")
    ph = str(row.get("password_hash") or "")
    if not ph or not verify_password(body.password, ph):
        raise HTTPException(status_code=401, detail="Incorrect email or password.")
    oid = str(row["id"])
    _log.info("neo4j read ok: login_organization id=%s", oid)
    return _issue("organization", oid)


def get_me(principal: dict[str, str]) -> AuthMeResponse:
    role = principal["role"]
    eid = principal["sub"]
    if role == "victim":
        row = _execute_read_one(auth_queries.GET_USER_ME, {"user_id": eid})
        if not row or not row.get("id"):
            raise HTTPException(status_code=401, detail="Account not found.")
        return AuthMeResponse(
            role="victim",
            id=str(row["id"]),
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
    if role == "volunteer":
        row = _execute_read_one(auth_queries.GET_VOLUNTEER_ME, {"volunteer_id": eid})
        if not row or not row.get("id"):
            raise HTTPException(status_code=401, detail="Account not found.")
        skills = row.get("skills") or []
        st = row.get("support_types") or []
        langs = row.get("languages") or []
        return AuthMeResponse(
            role="volunteer",
            id=str(row["id"]),
            email=str(row.get("email") or ""),
            full_name=str(row.get("display_name") or ""),
            phone=str(row.get("phone") or ""),
            zone_id=str(row.get("zone_id") or ""),
            skills=[str(x) for x in skills] if isinstance(skills, list) else [],
            support_types=[str(x) for x in st] if isinstance(st, list) else [],
            languages=[str(x) for x in langs] if isinstance(langs, list) else [],
            transport_access=str(row.get("transport_access") or ""),
            availability=str(row.get("availability") or ""),
            credits=int(row.get("credits") or 0),
            trust_score=float(row.get("trust_score") or 0.5),
        )
    if role == "organization":
        row = _execute_read_one(auth_queries.GET_ORGANIZATION_ME, {"organization_id": eid})
        if not row or not row.get("id"):
            raise HTTPException(status_code=401, detail="Account not found.")
        return AuthMeResponse(
            role="organization",
            id=str(row["id"]),
            email=str(row.get("email") or ""),
            organization_name=str(row.get("organization_name") or ""),
            org_type=str(row.get("org_type") or ""),
            contact_name=str(row.get("contact_name") or ""),
            contact_phone=str(row.get("contact_phone") or ""),
            zone_id=str(row.get("zone_id") or ""),
            beds_available=int(row.get("beds_available") or 0),
            oxygen_units=int(row.get("oxygen_units") or 0),
            ambulances_available=int(row.get("ambulances_available") or 0),
            shelter_units=int(row.get("shelter_units") or 0),
            food_capacity_units=int(row.get("food_capacity_units") or 0),
            rescue_units=int(row.get("rescue_units") or 0),
            active=bool(row.get("active", True)),
        )
    raise HTTPException(status_code=401, detail="Unknown role.")
