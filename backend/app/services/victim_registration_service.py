"""Victim registration and profile reads backed by PostgreSQL (Neo4j projection only)."""

from __future__ import annotations

import logging
import uuid

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.core.config import get_settings
from app.core.security import create_access_token, hash_password, verify_password
from app.db.sql.constants.auth_zones import CANONICAL_ZONE_IDS, normalize_zone_id, zone_display_name
from app.db.sql.enums import UserRole
from app.db.sql.models.user import User
from app.db.sql.models.victim_profile import VictimProfile
from app.db.sql.models.zone import Zone
from app.models.auth_models import AccessTokenResponse, AuthMeResponse
from app.models.auth_requests import LoginVictimRequest, RegisterVictimAuthRequest
from app.models.user_profile import UserProfileResponse
from app.services.neo4j_projection_service import VictimGraphProjectionInput, project_victim_account_from_pg

_log = logging.getLogger("pulsegrid.victim_pg")


def _issue_victim_token(user_id: uuid.UUID) -> AccessTokenResponse:
    tok = create_access_token(subject=str(user_id), role="victim")
    return AccessTokenResponse(access_token=tok, role="victim", id=str(user_id))


def register_victim(db: Session, body: RegisterVictimAuthRequest) -> AccessTokenResponse:
    email = str(body.email).strip().lower()
    zone_canonical = normalize_zone_id(body.home_zone_id)
    if zone_canonical is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Unknown home_zone_id: {body.home_zone_id!r}. Use the same ids as the Flutter app: "
                f"{', '.join(CANONICAL_ZONE_IDS)} (chip labels Riverside/Central/North/East map to these)."
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

    hs = body.household_size if body.household_size is not None else 1
    uid = uuid.uuid4()
    user = User(
        id=uid,
        email=email,
        hashed_password=hash_password(body.password),
        phone=body.phone.strip(),
        display_name=None,
        role=UserRole.victim,
    )
    profile = VictimProfile(
        account_id=uid,
        full_name=body.full_name.strip(),
        preferred_language=(body.preferred_language or "en").strip() or "en",
        home_zone_id=zone_canonical,
        household_size=hs,
        elderly_count=int(body.elderly_count),
        mobility_concern=bool(body.mobility_concern),
        oxygen_dependency=bool(body.oxygen_dependency),
        emergency_contact_name=body.emergency_contact_name.strip(),
        emergency_contact_phone=body.emergency_contact_phone.strip(),
        emergency_contact_relationship=(body.emergency_contact_relationship or "").strip(),
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

    _log.info("postgresql_victim_registered", extra={"user_id": str(uid), "email": email})

    settings = get_settings()
    projection = project_victim_account_from_pg(
        settings=settings,
        payload=VictimGraphProjectionInput(
            user_id=str(uid),
            email=user.email,
            full_name=profile.full_name,
            phone=user.phone or "",
            preferred_language=profile.preferred_language,
            household_size=int(profile.household_size or 1),
            elderly_count=int(profile.elderly_count),
            mobility_concern=profile.mobility_concern,
            oxygen_dependency=profile.oxygen_dependency,
            emergency_contact_name=profile.emergency_contact_name,
            emergency_contact_phone=profile.emergency_contact_phone,
            emergency_contact_relationship=profile.emergency_contact_relationship,
            zone_id=zone_canonical,
            zone_name=zone.name or zone_display_name(zone_canonical),
        ),
    )
    if not projection.ok:
        _log.error(
            "postgresql_victim_neo4j_projection_failed_post_commit",
            extra={"user_id": str(uid), "detail": projection.detail},
        )

    return _issue_victim_token(uid)


def login_victim(db: Session, body: LoginVictimRequest) -> AccessTokenResponse:
    email = str(body.email).strip().lower()
    user = db.scalar(
        select(User).where(func.lower(User.email) == email, User.role == UserRole.victim, User.is_active.is_(True))
    )
    if user is None or not verify_password(body.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect email or password.")
    _log.info("postgresql_victim_login_ok", extra={"user_id": str(user.id)})
    return _issue_victim_token(user.id)


def build_auth_me_victim(db: Session, user_id: str) -> AuthMeResponse | None:
    try:
        uid = uuid.UUID(str(user_id).strip())
    except ValueError:
        return None
    user = db.scalar(
        select(User)
        .options(joinedload(User.victim_profile).joinedload(VictimProfile.zone))
        .where(User.id == uid, User.role == UserRole.victim)
    )
    if user is None or user.victim_profile is None:
        return None
    vp = user.victim_profile
    return AuthMeResponse(
        role="victim",
        id=str(user.id),
        email=user.email,
        full_name=vp.full_name,
        phone=user.phone or "",
        preferred_language=vp.preferred_language,
        zone_id=vp.home_zone_id,
        household_size=int(vp.household_size or 1),
        elderly_count=int(vp.elderly_count),
        mobility_concern=bool(vp.mobility_concern),
        oxygen_dependency=bool(vp.oxygen_dependency),
        emergency_contact_name=vp.emergency_contact_name,
        emergency_contact_phone=vp.emergency_contact_phone,
        emergency_contact_relationship=vp.emergency_contact_relationship,
    )


def get_user_profile_response(db: Session, user_id: str) -> UserProfileResponse | None:
    try:
        uid = uuid.UUID(str(user_id).strip())
    except ValueError:
        return None
    user = db.scalar(
        select(User)
        .options(joinedload(User.victim_profile).joinedload(VictimProfile.zone))
        .where(User.id == uid, User.role == UserRole.victim)
    )
    if user is None or user.victim_profile is None:
        return None
    vp = user.victim_profile
    return UserProfileResponse(
        user_id=str(user.id),
        email=user.email,
        full_name=vp.full_name,
        phone=user.phone or "",
        preferred_language=vp.preferred_language,
        zone_id=vp.home_zone_id,
        household_size=int(vp.household_size or 1),
        elderly_count=int(vp.elderly_count),
        mobility_concern=bool(vp.mobility_concern),
        oxygen_dependency=bool(vp.oxygen_dependency),
        emergency_contact_name=vp.emergency_contact_name,
        emergency_contact_phone=vp.emergency_contact_phone,
        emergency_contact_relationship=vp.emergency_contact_relationship,
    )


