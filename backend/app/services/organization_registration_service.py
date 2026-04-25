"""Organization registration and profile reads backed by PostgreSQL (Neo4j projection)."""

from __future__ import annotations

import logging
import uuid
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.neo4j_client import get_driver, managed_neo4j_session
from app.core.security import create_access_token, hash_password, verify_password
from app.db.queries import auth_queries
from app.db.sql.constants.auth_zones import CANONICAL_ZONE_IDS, normalize_zone_id, normalize_zone_ids, zone_display_name
from app.db.sql.models.organization import Organization
from app.db.sql.models.zone import Zone
from app.models.auth_models import AccessTokenResponse, AuthMeResponse
from app.models.auth_requests import LoginOrganizationRequest, RegisterOrganizationAuthRequest
from app.services.neo4j_projection_service import (
    OrganizationGraphProjectionInput,
    ProjectionResult,
    project_organization_account_from_pg,
)

_log = logging.getLogger("pulsegrid.org_pg")


def _neo_read_one(query: str, params: dict[str, Any]) -> dict[str, Any] | None:
    driver = get_driver()
    settings = get_settings()

    def work(tx: Any) -> list[dict[str, Any]]:
        result = tx.run(query, **params)
        return [dict(r) for r in result]

    with managed_neo4j_session(driver, settings) as session:
        rows = session.execute_read(work)
    return rows[0] if rows else None


def project_organization_orm_to_neo4j(db: Session, org: Organization) -> ProjectionResult:
    """Re-project a committed ``Organization`` row to Neo4j (capacity, identity, zones). Call after PG updates."""
    primary = (org.zone_id or "").strip()
    if not primary:
        _log.warning("organization_projection_skipped_missing_zone", extra={"organization_id": str(org.id)})
        return ProjectionResult(ok=False, skipped=True, detail="missing_zone_id")
    zone = db.get(Zone, primary)
    settings = get_settings()
    cov_raw = org.coverage_zone_ids
    if isinstance(cov_raw, list):
        coverage = [str(x) for x in cov_raw if str(x).strip()]
    else:
        coverage = []
    return project_organization_account_from_pg(
        settings=settings,
        payload=OrganizationGraphProjectionInput(
            organization_id=str(org.id),
            name=org.name,
            org_type=org.org_type,
            contact_phone=org.contact_phone or "",
            contact_name=org.contact_name,
            contact_email=org.contact_email,
            primary_zone_id=primary,
            primary_zone_name=(zone.name if zone else zone_display_name(primary)),
            coverage_zone_ids=coverage,
            beds_available=int(org.beds_available),
            oxygen_units=int(org.oxygen_units),
            ambulances_available=int(org.ambulances_available),
            shelter_units=int(org.shelter_units),
            food_capacity_units=int(org.food_capacity_units),
            rescue_units=int(org.rescue_units),
            active=bool(org.is_active),
        ),
    )


def _issue_org_token(organization_id: uuid.UUID) -> AccessTokenResponse:
    tok = create_access_token(subject=str(organization_id), role="organization")
    return AccessTokenResponse(access_token=tok, role="organization", id=str(organization_id))


def _coalesce_nonneg(v: int | None) -> int:
    if v is None:
        return 0
    return max(0, int(v))


def register_organization(db: Session, body: RegisterOrganizationAuthRequest) -> AccessTokenResponse:
    primary = normalize_zone_id(body.zone_id)
    if primary is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Unknown zone_id: {body.zone_id!r}. Use the same ids as the Flutter app: "
                f"{', '.join(CANONICAL_ZONE_IDS)} (Riverside/Central/North/East chips send these hyphenated ids)."
            ),
        )
    coverage = normalize_zone_ids([str(z) for z in body.coverage_zone_ids])
    if primary not in coverage:
        coverage = [primary, *coverage]

    zone = db.get(Zone, primary)
    if zone is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Zone is not seeded in PostgreSQL. Run Alembic migrations.",
        )
    for zid in coverage:
        if db.get(Zone, zid) is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unknown coverage zone_id: {zid!r}.",
            )

    email = str(body.contact_email).strip().lower()
    existing_pg = db.scalar(select(Organization.id).where(func.lower(Organization.contact_email) == email))
    if existing_pg is not None:
        raise HTTPException(status_code=409, detail="An account with this email already exists.")

    neo = _neo_read_one(auth_queries.FIND_ORGANIZATION_BY_CONTACT_EMAIL, {"email": email})
    if neo and neo.get("id"):
        raise HTTPException(status_code=409, detail="An account with this email already exists.")

    oid = uuid.uuid4()
    org = Organization(
        id=oid,
        name=body.organization_name.strip(),
        contact_email=email,
        hashed_password=hash_password(body.password),
        contact_phone=body.contact_phone.strip(),
        contact_name=body.contact_name.strip(),
        org_type=(body.organization_type or "").strip().lower(),
        zone_id=primary,
        coverage_zone_ids=coverage,
        beds_available=_coalesce_nonneg(body.beds_available),
        oxygen_units=_coalesce_nonneg(body.oxygen_units),
        ambulances_available=_coalesce_nonneg(body.ambulances_available),
        shelter_units=_coalesce_nonneg(body.shelter_units),
        food_capacity_units=_coalesce_nonneg(body.food_capacity_units),
        rescue_units=_coalesce_nonneg(body.rescue_units),
        is_active=True,
    )
    db.add(org)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="An account with this email already exists.") from exc

    db.refresh(org)
    _log.info("postgresql_organization_registered", extra={"organization_id": str(oid), "email": email})

    projection = project_organization_orm_to_neo4j(db, org)
    if not projection.ok:
        _log.error(
            "postgresql_organization_neo4j_projection_failed_post_commit",
            extra={"organization_id": str(oid), "detail": projection.detail},
        )

    return _issue_org_token(oid)


def login_organization(db: Session | None, body: LoginOrganizationRequest) -> AccessTokenResponse:
    email = str(body.email).strip().lower()
    if db is not None:
        org = db.scalar(select(Organization).where(func.lower(Organization.contact_email) == email))
        if org is not None:
            hp = org.hashed_password
            if hp:
                if not verify_password(body.password, hp):
                    raise HTTPException(status_code=401, detail="Incorrect email or password.")
                if not org.is_active:
                    raise HTTPException(status_code=401, detail="Incorrect email or password.")
                _log.info("postgresql_organization_login_ok", extra={"organization_id": str(org.id)})
                return _issue_org_token(org.id)
            # Row exists without a password hash — fall through to Neo4j legacy login.

    neo = _neo_read_one(auth_queries.FIND_ORGANIZATION_BY_CONTACT_EMAIL, {"email": email})
    if not neo or not neo.get("id"):
        raise HTTPException(status_code=401, detail="Incorrect email or password.")
    ph = str(neo.get("password_hash") or "")
    if not ph or not verify_password(body.password, ph):
        raise HTTPException(status_code=401, detail="Incorrect email or password.")
    oid = str(neo["id"])
    _log.info("neo4j_organization_login_ok", extra={"organization_id": oid})
    return _issue_org_token(uuid.UUID(oid))


def build_auth_me_organization(db: Session, organization_id: str) -> AuthMeResponse | None:
    try:
        oid = uuid.UUID(str(organization_id).strip())
    except ValueError:
        return None
    org = db.get(Organization, oid)
    if org is None:
        return None
    return AuthMeResponse(
        role="organization",
        id=str(org.id),
        email=org.contact_email,
        organization_name=org.name,
        org_type=org.org_type,
        contact_name=org.contact_name,
        contact_phone=org.contact_phone or "",
        zone_id=org.zone_id or "",
        beds_available=int(org.beds_available),
        oxygen_units=int(org.oxygen_units),
        ambulances_available=int(org.ambulances_available),
        shelter_units=int(org.shelter_units),
        food_capacity_units=int(org.food_capacity_units),
        rescue_units=int(org.rescue_units),
        active=bool(org.is_active),
    )
