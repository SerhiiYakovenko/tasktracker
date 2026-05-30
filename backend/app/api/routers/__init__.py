"""Versioned API routers.

:data:`api_router` aggregates every feature router under the ``/api/v1`` prefix
and is included by :mod:`app.main`. The health router is mounted separately at
the root so monitoring does not depend on the API version.
"""

from fastapi import APIRouter

from app.api.routers import auth, projects, tasks, users

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(projects.router)
api_router.include_router(tasks.router)

__all__ = ["api_router"]
