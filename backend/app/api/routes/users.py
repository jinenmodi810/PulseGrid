"""Affected-user profile reads (Neo4j-backed)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps.auth_deps import auth_principal, require_role
from app.api.deps.db_deps import get_db_optional
from app.models.user_profile import UserProfileResponse
from app.services import auth_neo4j_service, victim_registration_service

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/{user_id}", response_model=UserProfileResponse)
def get_user(
    user_id: str,
    principal: dict[str, str] = Depends(auth_principal),
    db: Session | None = Depends(get_db_optional),
) -> UserProfileResponse:
    require_role(principal, "victim")
    if str(principal.get("sub") or "").strip() != str(user_id).strip():
        raise HTTPException(status_code=403, detail="User id does not match session.")
    try:
        profile = None
        if db is not None:
            profile = victim_registration_service.get_user_profile_response(db, user_id)
        if profile is None:
            profile = auth_neo4j_service.get_user_profile(user_id)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    if profile is None:
        raise HTTPException(status_code=404, detail="User not found")
    return profile
