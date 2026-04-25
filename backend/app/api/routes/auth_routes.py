"""Registration, email/password login, and admin login."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps.auth_deps import auth_principal
from app.api.deps.db_deps import get_db_optional
from app.models.auth_models import AccessTokenResponse, AuthMeResponse
from app.models.auth_requests import (
    AdminLoginRequest,
    AdminLoginResponse,
    LoginOrganizationRequest,
    LoginVictimRequest,
    LoginVolunteerRequest,
    RegisterOrganizationAuthRequest,
    RegisterVictimAuthRequest,
    RegisterVolunteerAuthRequest,
)
from app.services import auth_neo4j_service
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register-victim", response_model=AccessTokenResponse)
def post_register_victim(
    body: RegisterVictimAuthRequest,
    db: Session | None = Depends(get_db_optional),
) -> AccessTokenResponse:
    if db is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="PostgreSQL is required for victim registration. Set DATABASE_URL in backend/.env.",
        )
    try:
        return auth_service.register_victim(body, db)
    except HTTPException:
        raise
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/login-victim", response_model=AccessTokenResponse)
def post_login_victim(
    body: LoginVictimRequest,
    db: Session | None = Depends(get_db_optional),
) -> AccessTokenResponse:
    if db is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="PostgreSQL is required for victim login. Set DATABASE_URL in backend/.env.",
        )
    try:
        return auth_service.login_victim(body, db)
    except HTTPException:
        raise
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/register-volunteer", response_model=AccessTokenResponse)
def post_register_volunteer(
    body: RegisterVolunteerAuthRequest,
    db: Session | None = Depends(get_db_optional),
) -> AccessTokenResponse:
    if db is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="PostgreSQL is required for volunteer registration. Set DATABASE_URL in backend/.env.",
        )
    try:
        return auth_service.register_volunteer(body, db)
    except HTTPException:
        raise
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/login-volunteer", response_model=AccessTokenResponse)
def post_login_volunteer(
    body: LoginVolunteerRequest,
    db: Session | None = Depends(get_db_optional),
) -> AccessTokenResponse:
    if db is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="PostgreSQL is required for volunteer login. Set DATABASE_URL in backend/.env.",
        )
    try:
        return auth_service.login_volunteer(body, db)
    except HTTPException:
        raise
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/register-organization", response_model=AccessTokenResponse)
def post_register_organization(
    body: RegisterOrganizationAuthRequest,
    db: Session | None = Depends(get_db_optional),
) -> AccessTokenResponse:
    if db is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="PostgreSQL is required for organization registration. Set DATABASE_URL in backend/.env.",
        )
    try:
        return auth_service.register_organization(body, db)
    except HTTPException:
        raise
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/login-organization", response_model=AccessTokenResponse)
def post_login_organization(
    body: LoginOrganizationRequest,
    db: Session | None = Depends(get_db_optional),
) -> AccessTokenResponse:
    try:
        return auth_service.login_organization(body, db)
    except HTTPException:
        raise
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/me", response_model=AuthMeResponse)
def get_auth_me(
    principal: dict[str, str] = Depends(auth_principal),
    db: Session | None = Depends(get_db_optional),
) -> AuthMeResponse:
    try:
        return auth_service.get_me(principal, db)
    except HTTPException:
        raise
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/admin-login", response_model=AdminLoginResponse)
def post_admin_login(body: AdminLoginRequest) -> AdminLoginResponse:
    """TODO(Phase1): return 401 when ok is false and add JWT on success."""
    return auth_neo4j_service.admin_login(body)
