"""Security primitives: password hashing and JWT encode/decode.

This module is deliberately free of FastAPI and database concerns so it can be
unit-tested in isolation and reused outside the request lifecycle. Higher-level
authentication wiring lives in :mod:`app.api.deps`.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import get_settings

settings = get_settings()

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Return a salted bcrypt hash for ``password``."""
    return _pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against a stored bcrypt hash.

    Returns ``False`` rather than raising if the stored hash is malformed, so
    callers can treat every failure as an authentication failure.
    """
    try:
        return _pwd_context.verify(plain_password, hashed_password)
    except ValueError:
        return False


def create_access_token(
    subject: str | int,
    expires_delta: timedelta | None = None,
) -> str:
    """Create a signed JWT access token.

    Args:
        subject: The token subject — the authenticated user's id.
        expires_delta: Optional lifetime override. Defaults to the configured
            ``ACCESS_TOKEN_EXPIRE_MINUTES``.

    Returns:
        The encoded JWT as a string.
    """
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
    )
    payload: dict[str, Any] = {"sub": str(subject), "exp": expire}
    return jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> str | None:
    """Decode and validate a JWT, returning the subject (``sub``) claim.

    Returns ``None`` if the token is invalid, expired, or missing a subject.
    """
    try:
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.jwt_algorithm]
        )
    except JWTError:
        return None
    subject = payload.get("sub")
    return subject if isinstance(subject, str) else None
