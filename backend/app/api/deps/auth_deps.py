"""Bearer JWT dependency for /auth/me and future protected routes."""

from __future__ import annotations

from typing import Annotated

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.security import decode_access_token

security = HTTPBearer(auto_error=False)


def require_bearer_token(
    creds: Annotated[HTTPAuthorizationCredentials | None, Depends(security)],
) -> str:
    if creds is None or (creds.scheme or "").lower() != "bearer":
        raise HTTPException(status_code=401, detail="Sign in required.")
    t = (creds.credentials or "").strip()
    if not t:
        raise HTTPException(status_code=401, detail="Sign in required.")
    return t


def auth_principal(token: Annotated[str, Depends(require_bearer_token)]) -> dict[str, str]:
    try:
        payload = decode_access_token(token)
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired session.") from None
    sub = payload.get("sub")
    role = payload.get("role")
    if not sub or not role:
        raise HTTPException(status_code=401, detail="Invalid session.")
    return {"sub": str(sub), "role": str(role)}


def require_role(principal: dict[str, str], *roles: str) -> None:
    """Raise 403 when principal role is not one of expected roles."""
    expected = {r.strip().lower() for r in roles if r and r.strip()}
    got = str(principal.get("role") or "").strip().lower()
    if expected and got not in expected:
        raise HTTPException(status_code=403, detail="Insufficient role permissions.")
