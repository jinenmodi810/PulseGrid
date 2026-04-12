"""Registration, email/password login, and admin login."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from app.api.deps.auth_deps import auth_principal
from app.models.auth_models import AccessTokenResponse, AuthMeResponse
from app.models.auth_requests import (
    AdminLoginRequest,
    AdminLoginResponse,
    LoginOrganizationRequest,
    LoginVictimRequest,
    LoginVolunteerRequest,
    RegisterOrganizationAuthRequest,
    RegisterUserRequest,
    RegisterUserResponse,
    RegisterVictimAuthRequest,
    RegisterVolunteerAuthRequest,
)
from app.services import auth_neo4j_service
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


# Legacy affected-user registration (no password). Prefer POST /auth/register-victim.
@router.post("/register-user", response_model=RegisterUserResponse)
def post_register_user(body: RegisterUserRequest) -> RegisterUserResponse:
    try:
        return auth_neo4j_service.register_user(body)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/register-victim", response_model=AccessTokenResponse)
def post_register_victim(body: RegisterVictimAuthRequest) -> AccessTokenResponse:
    try:
        return auth_service.register_victim(body)
    except HTTPException:
        raise
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/login-victim", response_model=AccessTokenResponse)
def post_login_victim(body: LoginVictimRequest) -> AccessTokenResponse:
    try:
        return auth_service.login_victim(body)
    except HTTPException:
        raise
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/register-volunteer", response_model=AccessTokenResponse)
def post_register_volunteer(body: RegisterVolunteerAuthRequest) -> AccessTokenResponse:
    try:
        return auth_service.register_volunteer(body)
    except HTTPException:
        raise
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/login-volunteer", response_model=AccessTokenResponse)
def post_login_volunteer(body: LoginVolunteerRequest) -> AccessTokenResponse:
    try:
        return auth_service.login_volunteer(body)
    except HTTPException:
        raise
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/register-organization", response_model=AccessTokenResponse)
def post_register_organization(body: RegisterOrganizationAuthRequest) -> AccessTokenResponse:
    try:
        return auth_service.register_organization(body)
    except HTTPException:
        raise
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/login-organization", response_model=AccessTokenResponse)
def post_login_organization(body: LoginOrganizationRequest) -> AccessTokenResponse:
    try:
        return auth_service.login_organization(body)
    except HTTPException:
        raise
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/me", response_model=AuthMeResponse)
def get_auth_me(principal: dict[str, str] = Depends(auth_principal)) -> AuthMeResponse:
    try:
        return auth_service.get_me(principal)
    except HTTPException:
        raise
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/admin-login", response_model=AdminLoginResponse)
def post_admin_login(body: AdminLoginRequest) -> AdminLoginResponse:
    """TODO(Phase1): return 401 when ok is false and add JWT on success."""
    return auth_neo4j_service.admin_login(body)
