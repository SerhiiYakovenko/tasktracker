"""User and authentication business logic."""

from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password
from app.logging_config import get_logger
from app.models.user import User
from app.schemas.user import UserCreate

logger = get_logger(__name__)


def get_by_id(db: Session, user_id: int) -> User | None:
    """Return the user with ``user_id`` or ``None``."""
    return db.get(User, user_id)


def get_by_email(db: Session, email: str) -> User | None:
    """Return the user with the given email (case-insensitive) or ``None``."""
    stmt = select(User).where(User.email == email.lower())
    return db.execute(stmt).scalar_one_or_none()


def create_user(db: Session, payload: UserCreate) -> User:
    """Register a new user.

    Raises:
        HTTPException: 409 if the email is already registered.
    """
    email = payload.email.lower()
    if get_by_email(db, email) is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email already exists.",
        )

    user = User(
        email=email,
        full_name=payload.full_name,
        hashed_password=hash_password(payload.password),
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    logger.info("Registered new user id=%s email=%s", user.id, user.email)
    return user


def authenticate(db: Session, email: str, password: str) -> User:
    """Validate credentials and return the user.

    Raises:
        HTTPException: 401 if the credentials are invalid or the user is
            inactive. The message is intentionally generic to avoid leaking
            whether an email exists.
    """
    invalid = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect email or password.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    user = get_by_email(db, email)
    if user is None or not verify_password(password, user.hashed_password):
        logger.info("Failed login attempt for email=%s", email.lower())
        raise invalid
    if not user.is_active:
        raise invalid
    return user
