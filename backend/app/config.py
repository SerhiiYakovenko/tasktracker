"""Application configuration.

Settings are loaded from environment variables (and an optional `.env` file)
via pydantic-settings. A single cached :class:`Settings` instance is exposed
through :func:`get_settings` and consumed everywhere through dependency
injection so the rest of the codebase never reads ``os.environ`` directly.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Strongly-typed application settings.

    Values are read from the process environment first, then from a local
    ``.env`` file. Unknown environment variables are ignored.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = "TaskTracker"
    environment: Literal["development", "staging", "production"] = "development"
    log_level: str = "INFO"
    api_v1_prefix: str = "/api/v1"

    # Database
    database_url: str = "sqlite:///./data/app.db"

    # Security
    secret_key: str = "change-me"
    access_token_expire_minutes: int = 60
    jwt_algorithm: str = "HS256"

    # CORS. Stored as a comma-separated string (env-friendly: BACKEND_CORS_ORIGINS="http://a,http://b")
    # and exposed as a parsed list via the `cors_origins` property. Keeping it a plain `str` avoids
    # pydantic-settings trying to JSON-decode a complex (list) env value.
    backend_cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    # Seed data
    seed_user_email: str = "demo@tasktracker.dev"
    seed_user_password: str = "change-me"
    seed_user_name: str = "Demo User"

    @property
    def cors_origins(self) -> list[str]:
        """Allowed CORS origins, parsed from the comma-separated setting."""
        return [
            origin.strip()
            for origin in self.backend_cors_origins.split(",")
            if origin.strip()
        ]

    @property
    def is_sqlite(self) -> bool:
        """Whether the configured database is SQLite."""
        return self.database_url.startswith("sqlite")


@lru_cache
def get_settings() -> Settings:
    """Return a process-wide cached :class:`Settings` instance."""
    return Settings()
