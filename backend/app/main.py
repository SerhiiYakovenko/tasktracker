"""FastAPI application factory and ASGI entrypoint.

Run in development::

    uvicorn app.main:app --reload

Run in production::

    uvicorn app.main:app --host 0.0.0.0 --port 8000
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import __version__
from app.api.routers import api_router
from app.api.routers import health
from app.config import get_settings
from app.database import create_all
from app.logging_config import configure_logging, get_logger

settings = get_settings()
configure_logging(settings.log_level)
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    """Initialise resources on startup and tear them down on shutdown.

    For the demo we create the schema via ``Base.metadata.create_all`` instead
    of running Alembic migrations.
    """
    logger.info(
        "Starting %s (env=%s, db=%s)",
        settings.app_name,
        settings.environment,
        "sqlite" if settings.is_sqlite else "external",
    )
    create_all()
    yield
    logger.info("Shutting down %s", settings.app_name)


def create_app() -> FastAPI:
    """Build and configure the FastAPI application."""
    app = FastAPI(
        title=settings.app_name,
        version=__version__,
        description="A lean team task and project management API.",
        lifespan=lifespan,
    )

    if settings.cors_origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.cors_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # Health check at the root (not version-prefixed).
    app.include_router(health.router)
    # Versioned API.
    app.include_router(api_router, prefix=settings.api_v1_prefix)

    return app


app = create_app()
