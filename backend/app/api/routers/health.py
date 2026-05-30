"""Health-check endpoint for liveness/readiness probes."""

from __future__ import annotations

from fastapi import APIRouter

from app import __version__

router = APIRouter(tags=["health"])


@router.get("/health", summary="Liveness check")
def health() -> dict[str, str]:
    """Return a simple status payload used by load balancers and probes."""
    return {"status": "ok", "version": __version__}
