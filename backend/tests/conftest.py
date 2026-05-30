"""Shared pytest fixtures.

The application is configured to use a throwaway, file-backed SQLite database
*before* any ``app.*`` module is imported, by setting ``DATABASE_URL`` (and a
test ``SECRET_KEY``) in the environment. Because the app builds its engine and
settings at import time, this guarantees the application under test and the
fixtures all talk to the same temporary database. The schema is recreated for
every test so cases stay isolated, and a ``TestClient`` drives the real ASGI
app end to end with ``get_db`` overridden to use the test session factory.
"""

from __future__ import annotations

import os
import tempfile
from collections.abc import Generator, Iterator
from pathlib import Path

import pytest

# A dedicated temp file for the whole test process. Set the environment before
# importing the app so its cached Settings / engine point at this database.
_TMP_DIR = Path(tempfile.mkdtemp(prefix="tasktracker-tests-"))
_DB_PATH = _TMP_DIR / "test_app.db"
os.environ["DATABASE_URL"] = f"sqlite:///{_DB_PATH}"
os.environ.setdefault("SECRET_KEY", "test-secret-key")
os.environ.setdefault("ENVIRONMENT", "development")

from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy.orm import Session  # noqa: E402

# Importing ``app.models`` registers every table on ``Base.metadata`` so the
# schema can be created. Imported before ``app.main`` to be explicit about the
# registration side-effect.
import app.models  # noqa: E402, F401  (registration side-effect)
from app.database import Base, SessionLocal, engine, get_db  # noqa: E402
from app.main import app as fastapi_app  # noqa: E402


@pytest.fixture(autouse=True)
def _schema() -> Iterator[None]:
    """Recreate a clean schema before each test and drop it afterwards."""
    Base.metadata.create_all(bind=engine)
    try:
        yield
    finally:
        Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def db_session() -> Iterator[Session]:
    """Yield a database session for tests that need direct DB access."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def client() -> Iterator[TestClient]:
    """A TestClient with ``get_db`` overridden to use the test database."""

    def _override_get_db() -> Generator[Session, None, None]:
        session = SessionLocal()
        try:
            yield session
        finally:
            session.close()

    fastapi_app.dependency_overrides[get_db] = _override_get_db
    try:
        with TestClient(fastapi_app) as test_client:
            yield test_client
    finally:
        fastapi_app.dependency_overrides.clear()


# --- Authentication helpers ------------------------------------------------

DEFAULT_USER = {
    "email": "alice@example.com",
    "password": "supersecret123",
    "full_name": "Alice Example",
}


def register_and_login(
    client: TestClient,
    *,
    email: str = DEFAULT_USER["email"],
    password: str = DEFAULT_USER["password"],
    full_name: str = DEFAULT_USER["full_name"],
) -> dict[str, str]:
    """Register a user (idempotently) and return a Bearer auth header.

    If the email is already registered the registration 409 is ignored and the
    existing credentials are used to log in.
    """
    register_resp = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password, "full_name": full_name},
    )
    assert register_resp.status_code in (201, 409), register_resp.text

    login_resp = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert login_resp.status_code == 200, login_resp.text
    token = login_resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def auth_headers(client: TestClient) -> dict[str, str]:
    """A registered-and-logged-in user, returned as a Bearer auth header."""
    return register_and_login(client)


@pytest.fixture()
def project_id(client: TestClient, auth_headers: dict[str, str]) -> int:
    """Create a project owned by the default user and return its id."""
    resp = client.post(
        "/api/v1/projects",
        json={"name": "Demo Project", "description": "Fixture project"},
        headers=auth_headers,
    )
    assert resp.status_code == 201, resp.text
    return int(resp.json()["id"])
