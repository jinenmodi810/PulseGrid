"""Volunteer registration and profile reads backed by PostgreSQL (Neo4j projection only)."""

from __future__ import annotations

import logging
import uuid
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.core.config import get_settings
from app.core.security import create_access_token, hash_password, verify_password
from app.db.sql.constants.auth_zones import CANONICAL_ZONE_IDS, normalize_zone_id, zone_display_name
from app.db.sql.enums import UserRole
from app.db.sql.models.responder_profile import ResponderProfile
from app.db.sql.models.user import User
from app.db.sql.models.zone import Zone
from app.models.auth_models import AccessTokenResponse, AuthMeResponse
from app.models.auth_requests import LoginVolunteerRequest, RegisterVolunteerAuthRequest
from app.services.neo4j_projection_service import VolunteerGraphProjectionInput, project_volunteer_account_from_pg

_log = logging.getLogger("pulsegrid.volunteer_pg")


def _issue_volunteer_token(volunteer_id: uuid.UUID) -> AccessTokenResponse:
    tok = create_access_token(subject=str(volunteer_id), role="volunteer")
    return AccessTokenResponse(access_token=tok, role="volunteer", id=str(volunteer_id))


def _str_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(x).strip() for x in value if str(x).strip()]
    return [str(value).strip()] if str(value).strip() else []


def register_volunteer(db: Session, body: RegisterVolunteerAuthRequest) -> AccessTokenResponse:
    email = str(body.email).strip().lower()
    zone_canonical = normalize_zone_id(body.zone_id)
    if zone_canonical is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Unknown zone_id: {body.zone_id!r}. Use the same ids as the Flutter app: "
                f"{', '.join(CANONICAL_ZONE_IDS)} (Riverside/Central/North/East chips send these hyphenated ids)."
            ),
        )
    zone = db.get(Zone, zone_canonical)
    if zone is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Zone is not seeded in PostgreSQL. Run Alembic migrations.",
        )

    existing = db.scalar(select(User.id).where(func.lower(User.email) == email))
    if existing is not None:
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
    skill_type = (body.skill_type or "").strip() or skills[0]

    uid = uuid.uuid4()
    user = User(
        id=uid,
        email=email,
        hashed_password=hash_password(body.password),
        phone=body.phone.strip(),
        display_name=body.full_name.strip(),
        role=UserRole.volunteer,
    )
    profile = ResponderProfile(
        user_id=uid,
        display_name=body.full_name.strip(),
        skills=skills,
        languages=langs,
        support_types=support_types,
        zone_id=zone_canonical,
        availability=(body.availability or "").strip() or None,
        transport_access=body.transport_access.strip(),
        verified=bool(body.verified),
        skill_type=skill_type,
        credits=0,
        trust_score=0.5,
    )
    db.add(user)
    db.add(profile)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="An account with this email already exists.") from exc

    db.refresh(user)
    db.refresh(profile)

    _log.info("postgresql_volunteer_registered", extra={"volunteer_id": str(uid), "email": email})

    settings = get_settings()
    projection = project_volunteer_account_from_pg(
        settings=settings,
        payload=VolunteerGraphProjectionInput(
            volunteer_id=str(uid),
            email=user.email,
            display_name=profile.display_name or body.full_name.strip(),
            phone=user.phone or "",
            skills=_str_list(profile.skills),
            support_types=_str_list(profile.support_types),
            languages=_str_list(profile.languages),
            transport_access=profile.transport_access or "",
            availability=profile.availability or "",
            verified=profile.verified,
            skill_type=profile.skill_type or "",
            zone_id=zone_canonical,
            zone_name=zone.name or zone_display_name(zone_canonical),
            credits=profile.credits,
            trust_score=profile.trust_score,
        ),
    )
    if not projection.ok:
        _log.error(
            "postgresql_volunteer_neo4j_projection_failed_post_commit",
            extra={"volunteer_id": str(uid), "detail": projection.detail},
        )

    return _issue_volunteer_token(uid)


def login_volunteer(db: Session, body: LoginVolunteerRequest) -> AccessTokenResponse:
    email = str(body.email).strip().lower()
    user = db.scalar(
        select(User).where(
            func.lower(User.email) == email,
            User.role == UserRole.volunteer,
            User.is_active.is_(True),
        )
    )
    if user is None or not verify_password(body.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect email or password.")
    _log.info("postgresql_volunteer_login_ok", extra={"volunteer_id": str(user.id)})
    return _issue_volunteer_token(user.id)


def build_auth_me_volunteer(db: Session, volunteer_id: str) -> AuthMeResponse | None:
    try:
        uid = uuid.UUID(str(volunteer_id).strip())
    except ValueError:
        return None
    user = db.scalar(
        select(User)
        .options(joinedload(User.responder_profile))
        .where(User.id == uid, User.role == UserRole.volunteer)
    )
    if user is None or user.responder_profile is None:
        return None
    rp = user.responder_profile
    return AuthMeResponse(
        role="volunteer",
        id=str(user.id),
        email=user.email,
        full_name=rp.display_name or user.display_name or "",
        phone=user.phone or "",
        zone_id=rp.zone_id or "",
        skills=_str_list(rp.skills),
        support_types=_str_list(rp.support_types),
        languages=_str_list(rp.languages),
        transport_access=rp.transport_access or "",
        availability=rp.availability or "",
        credits=int(rp.credits),
        trust_score=float(rp.trust_score),
    )
