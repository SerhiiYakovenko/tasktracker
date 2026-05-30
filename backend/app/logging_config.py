"""Centralised logging configuration.

Provides a single :func:`configure_logging` entry point used at application
startup. Logging is intentionally simple and structured-friendly: a consistent
single-line format with timestamps, levels and logger names that plays well
with container log collectors.
"""

from __future__ import annotations

import logging
from logging.config import dictConfig

_LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
_DATE_FORMAT = "%Y-%m-%dT%H:%M:%S%z"


def configure_logging(level: str = "INFO") -> None:
    """Configure the root logger for the application.

    Args:
        level: Minimum log level name (e.g. ``"INFO"``, ``"DEBUG"``).
            Invalid values fall back to ``INFO``.
    """
    resolved = getattr(logging, level.upper(), logging.INFO)

    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": _LOG_FORMAT,
                    "datefmt": _DATE_FORMAT,
                },
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "default",
                    "stream": "ext://sys.stdout",
                },
            },
            "root": {
                "level": resolved,
                "handlers": ["console"],
            },
            "loggers": {
                # Quieten access logs but keep error logs from uvicorn.
                "uvicorn.access": {"level": "WARNING", "propagate": False, "handlers": ["console"]},
                "uvicorn.error": {"level": resolved, "propagate": False, "handlers": ["console"]},
            },
        }
    )


def get_logger(name: str) -> logging.Logger:
    """Return a module-scoped logger."""
    return logging.getLogger(name)
