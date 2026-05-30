"""Tests for registration, login and the authenticated /users/me endpoint."""

from __future__ import annotations

from fastapi.testclient import TestClient

from tests.conftest import DEFAULT_USER


def test_register_returns_public_user(client: TestClient) -> None:
    resp = client.post(
        "/api/v1/auth/register",
        json={
            "email": "newuser@example.com",
            "password": "password1234",
            "full_name": "New User",
        },
    )
    assert resp.status_code == 201, resp.text

    body = resp.json()
    assert body["email"] == "newuser@example.com"
    assert body["full_name"] == "New User"
    assert body["is_active"] is True
    assert isinstance(body["id"], int)
    assert "created_at" in body
    # The password hash must never be exposed.
    assert "hashed_password" not in body
    assert "password" not in body


def test_register_normalises_email_to_lowercase(client: TestClient) -> None:
    resp = client.post(
        "/api/v1/auth/register",
        json={
            "email": "MixedCase@Example.com",
            "password": "password1234",
            "full_name": "Mixed Case",
        },
    )
    assert resp.status_code == 201, resp.text
    assert resp.json()["email"] == "mixedcase@example.com"


def test_register_duplicate_email_conflicts(client: TestClient) -> None:
    payload = {
        "email": "dupe@example.com",
        "password": "password1234",
        "full_name": "Dupe",
    }
    first = client.post("/api/v1/auth/register", json=payload)
    assert first.status_code == 201, first.text

    second = client.post("/api/v1/auth/register", json=payload)
    assert second.status_code == 409, second.text


def test_register_rejects_short_password(client: TestClient) -> None:
    resp = client.post(
        "/api/v1/auth/register",
        json={"email": "short@example.com", "password": "short", "full_name": "S"},
    )
    assert resp.status_code == 422, resp.text


def test_login_returns_bearer_token(client: TestClient) -> None:
    client.post(
        "/api/v1/auth/register",
        json={
            "email": DEFAULT_USER["email"],
            "password": DEFAULT_USER["password"],
            "full_name": DEFAULT_USER["full_name"],
        },
    )

    resp = client.post(
        "/api/v1/auth/login",
        json={"email": DEFAULT_USER["email"], "password": DEFAULT_USER["password"]},
    )
    assert resp.status_code == 200, resp.text

    body = resp.json()
    assert body["token_type"] == "bearer"
    assert isinstance(body["access_token"], str)
    assert body["access_token"]


def test_login_wrong_password_unauthorized(client: TestClient) -> None:
    client.post(
        "/api/v1/auth/register",
        json={
            "email": DEFAULT_USER["email"],
            "password": DEFAULT_USER["password"],
            "full_name": DEFAULT_USER["full_name"],
        },
    )

    resp = client.post(
        "/api/v1/auth/login",
        json={"email": DEFAULT_USER["email"], "password": "wrong-password"},
    )
    assert resp.status_code == 401, resp.text


def test_login_unknown_email_unauthorized(client: TestClient) -> None:
    resp = client.post(
        "/api/v1/auth/login",
        json={"email": "ghost@example.com", "password": "password1234"},
    )
    assert resp.status_code == 401, resp.text


def test_users_me_returns_current_user(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    resp = client.get("/api/v1/users/me", headers=auth_headers)
    assert resp.status_code == 200, resp.text

    body = resp.json()
    assert body["email"] == DEFAULT_USER["email"]
    assert body["full_name"] == DEFAULT_USER["full_name"]
    assert "hashed_password" not in body


def test_users_me_without_token_unauthorized(client: TestClient) -> None:
    resp = client.get("/api/v1/users/me")
    assert resp.status_code == 401, resp.text


def test_users_me_with_invalid_token_unauthorized(client: TestClient) -> None:
    resp = client.get(
        "/api/v1/users/me",
        headers={"Authorization": "Bearer not-a-real-token"},
    )
    assert resp.status_code == 401, resp.text


def test_health_check(client: TestClient) -> None:
    resp = client.get("/health")
    assert resp.status_code == 200, resp.text
    assert resp.json()["status"] == "ok"
