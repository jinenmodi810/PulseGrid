"""Affected-user profile reads (Neo4j-backed)."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.models.user_profile import UserProfileResponse
from app.services import auth_neo4j_service

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/{user_id}", response_model=UserProfileResponse)
def get_user(user_id: str) -> UserProfileResponse:
    try:
        profile = auth_neo4j_service.get_user_profile(user_id)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    if profile is None:
        raise HTTPException(status_code=404, detail="User not found")
    return profile
