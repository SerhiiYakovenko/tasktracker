"""JWT token schemas."""

from __future__ import annotations

from pydantic import BaseModel


class Token(BaseModel):
    """Access token returned on successful login."""

    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """Decoded JWT payload (the ``sub`` claim holds the user id)."""

    sub: str | None = None
