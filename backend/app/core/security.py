"""Password hashing and JWT helpers (MVP / demo-grade)."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

import bcrypt
import jwt

from app.core.config import get_settings

# bcrypt applies the first 72 UTF-8 bytes only; the library rejects longer inputs.
_MAX_PASSWORD_BYTES = 72


def _bcrypt_safe_secret(plain: str) -> str:
    """Match bcrypt's 72-byte input cap (UTF-8), without splitting codepoints."""
    p = plain or ""
    raw = p.encode("utf-8")
    if len(raw) <= _MAX_PASSWORD_BYTES:
        return p
    cut = raw[:_MAX_PASSWORD_BYTES]
    while cut:
        try:
            return cut.decode("utf-8")
        except UnicodeDecodeError:
            cut = cut[:-1]
    return ""


def hash_password(plain: str) -> str:
    secret = _bcrypt_safe_secret(plain).encode("utf-8")
    return bcrypt.hashpw(secret, bcrypt.gensalt()).decode("ascii")


def verify_password(plain: str, hashed: str) -> bool:
    if not hashed:
        return False
    secret = _bcrypt_safe_secret(plain).encode("utf-8")
    try:
        return bcrypt.checkpw(secret, hashed.encode("ascii"))
    except (ValueError, TypeError):
        return False


def create_access_token(*, subject: str, role: str) -> str:
    settings = get_settings()
    secret = (settings.JWT_SECRET or "").strip()
    if not secret:
        raise RuntimeError("JWT_SECRET is not set in the environment.")
    now = datetime.now(tz=UTC)
    exp_min = max(5, int(settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES or 10080))
    payload: dict[str, Any] = {
        "sub": subject,
        "role": role,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=exp_min)).timestamp()),
        "typ": "access",
    }
    return jwt.encode(payload, secret, algorithm="HS256")


def decode_access_token(token: str) -> dict[str, Any]:
    settings = get_settings()
    secret = (settings.JWT_SECRET or "").strip()
    if not secret:
        raise jwt.InvalidTokenError("JWT_SECRET is not set")
    return jwt.decode(token, secret, algorithms=["HS256"])
