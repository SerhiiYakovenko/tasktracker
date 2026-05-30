"""User endpoints."""

from __future__ import annotations

from fastapi import APIRouter

from app.api.deps import CurrentUser
from app.schemas.user import UserOut

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserOut, summary="Get the current user")
def read_current_user(current_user: CurrentUser) -> UserOut:
    """Return the profile of the authenticated user."""
    return UserOut.model_validate(current_user)
