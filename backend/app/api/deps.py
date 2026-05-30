"""Shared FastAPI dependencies.

Provides the database session and the authenticated-user dependencies that
routers consume via ``Depends``. The ``OAuth2PasswordBearer`` scheme is used
purely to extract and document the ``Authorization: Bearer <token>`` header;
the token itself is a JSON-login JWT.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.config import Settings, get_settings
from app.core.security import decode_access_token
from app.database import get_db
from app.models.user import User
from app.services import user_service

# tokenUrl points at the login endpoint for OpenAPI's "Authorize" button.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

SettingsDep = Annotated[Settings, Depends(get_settings)]
DBSession = Annotated[Session, Depends(get_db)]


def get_current_user(
    db: DBSession,
    token: Annotated[str, Depends(oauth2_scheme)],
) -> User:
    """Resolve the authenticated user from a Bearer token.

    Raises:
        HTTPException: 401 if the token is missing, invalid, expired, or refers
            to a user that no longer exists.
    """
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    subject = decode_access_token(token)
    if subject is None:
        raise credentials_error

    try:
        user_id = int(subject)
    except ValueError as exc:
        raise credentials_error from exc

    user = user_service.get_by_id(db, user_id)
    if user is None:
        raise credentials_error
    return user


def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """Ensure the authenticated user is active.

    Raises:
        HTTPException: 403 if the account has been deactivated.
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user.",
        )
    return current_user


CurrentUser = Annotated[User, Depends(get_current_active_user)]
