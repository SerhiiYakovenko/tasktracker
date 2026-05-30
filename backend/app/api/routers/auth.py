"""Authentication endpoints: register and login."""

from __future__ import annotations

from fastapi import APIRouter, status

from app.api.deps import DBSession
from app.core.security import create_access_token
from app.schemas.token import Token
from app.schemas.user import UserCreate, UserLogin, UserOut
from app.services import user_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
)
def register(payload: UserCreate, db: DBSession) -> UserOut:
    """Create a new account and return its public representation."""
    user = user_service.create_user(db, payload)
    return UserOut.model_validate(user)


@router.post("/login", response_model=Token, summary="Log in and obtain a token")
def login(credentials: UserLogin, db: DBSession) -> Token:
    """Authenticate with email/password and return a JWT access token."""
    user = user_service.authenticate(db, credentials.email, credentials.password)
    access_token = create_access_token(subject=user.id)
    return Token(access_token=access_token, token_type="bearer")
