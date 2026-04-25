"""Email/password registration, login, and /auth/me assembly (PostgreSQL + Neo4j + JWT)."""

from __future__ import annotations

import logging
from typing import Any

from fastapi import HTTPException
from sqlalchemy.orm import Session

_log = logging.getLogger("pulsegrid.auth")

from app.core.config import get_settings
from app.core.neo4j_client import get_driver, managed_neo4j_session
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
from app.services import (
    organization_registration_service,
    victim_registration_service,
    volunteer_registration_service,
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


def register_victim(body: RegisterVictimAuthRequest, db: Session) -> AccessTokenResponse:
    return victim_registration_service.register_victim(db, body)


def login_victim(body: LoginVictimRequest, db: Session) -> AccessTokenResponse:
    return victim_registration_service.login_victim(db, body)


def register_volunteer(body: RegisterVolunteerAuthRequest, db: Session) -> AccessTokenResponse:
    return volunteer_registration_service.register_volunteer(db, body)


def login_volunteer(body: LoginVolunteerRequest, db: Session) -> AccessTokenResponse:
    return volunteer_registration_service.login_volunteer(db, body)


def register_organization(body: RegisterOrganizationAuthRequest, db: Session) -> AccessTokenResponse:
    return organization_registration_service.register_organization(db, body)


def login_organization(body: LoginOrganizationRequest, db: Session | None) -> AccessTokenResponse:
    return organization_registration_service.login_organization(db, body)


def get_me(principal: dict[str, str], db: Session | None = None) -> AuthMeResponse:
    role = principal["role"]
    eid = principal["sub"]
    if role == "victim":
        if db is not None:
            pg_me = victim_registration_service.build_auth_me_victim(db, eid)
            if pg_me is not None:
                return pg_me
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
        if db is not None:
            pg_me = volunteer_registration_service.build_auth_me_volunteer(db, eid)
            if pg_me is not None:
                return pg_me
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
        if db is not None:
            pg_me = organization_registration_service.build_auth_me_organization(db, eid)
            if pg_me is not None:
                return pg_me
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
