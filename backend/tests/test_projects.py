"""Tests for project CRUD and per-owner access scoping."""

from __future__ import annotations

from fastapi.testclient import TestClient

from tests.conftest import register_and_login


def test_create_project(client: TestClient, auth_headers: dict[str, str]) -> None:
    resp = client.post(
        "/api/v1/projects",
        json={"name": "Apollo", "description": "Launch the new dashboard"},
        headers=auth_headers,
    )
    assert resp.status_code == 201, resp.text

    body = resp.json()
    assert body["name"] == "Apollo"
    assert body["description"] == "Launch the new dashboard"
    assert isinstance(body["id"], int)
    assert isinstance(body["owner_id"], int)
    assert "created_at" in body


def test_create_project_allows_null_description(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    resp = client.post(
        "/api/v1/projects",
        json={"name": "No Description"},
        headers=auth_headers,
    )
    assert resp.status_code == 201, resp.text
    assert resp.json()["description"] is None


def test_create_project_requires_auth(client: TestClient) -> None:
    resp = client.post("/api/v1/projects", json={"name": "Unauthorised"})
    assert resp.status_code == 401, resp.text


def test_create_project_rejects_empty_name(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    resp = client.post(
        "/api/v1/projects",
        json={"name": ""},
        headers=auth_headers,
    )
    assert resp.status_code == 422, resp.text


def test_list_projects_only_returns_own(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    client.post("/api/v1/projects", json={"name": "Mine A"}, headers=auth_headers)
    client.post("/api/v1/projects", json={"name": "Mine B"}, headers=auth_headers)

    other = register_and_login(client, email="bob@example.com", full_name="Bob")
    client.post("/api/v1/projects", json={"name": "Bob's"}, headers=other)

    resp = client.get("/api/v1/projects", headers=auth_headers)
    assert resp.status_code == 200, resp.text

    names = {p["name"] for p in resp.json()}
    assert names == {"Mine A", "Mine B"}


def test_get_project(client: TestClient, auth_headers: dict[str, str]) -> None:
    created = client.post(
        "/api/v1/projects",
        json={"name": "Fetch Me"},
        headers=auth_headers,
    ).json()

    resp = client.get(f"/api/v1/projects/{created['id']}", headers=auth_headers)
    assert resp.status_code == 200, resp.text
    assert resp.json()["id"] == created["id"]


def test_get_missing_project_404(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    resp = client.get("/api/v1/projects/999999", headers=auth_headers)
    assert resp.status_code == 404, resp.text


def test_update_project(client: TestClient, auth_headers: dict[str, str]) -> None:
    created = client.post(
        "/api/v1/projects",
        json={"name": "Old Name", "description": "old"},
        headers=auth_headers,
    ).json()

    resp = client.patch(
        f"/api/v1/projects/{created['id']}",
        json={"name": "New Name"},
        headers=auth_headers,
    )
    assert resp.status_code == 200, resp.text

    body = resp.json()
    assert body["name"] == "New Name"
    # Unset fields are left untouched.
    assert body["description"] == "old"


def test_delete_project(client: TestClient, auth_headers: dict[str, str]) -> None:
    created = client.post(
        "/api/v1/projects",
        json={"name": "Delete Me"},
        headers=auth_headers,
    ).json()

    delete_resp = client.delete(
        f"/api/v1/projects/{created['id']}", headers=auth_headers
    )
    assert delete_resp.status_code == 204, delete_resp.text

    follow_up = client.get(
        f"/api/v1/projects/{created['id']}", headers=auth_headers
    )
    assert follow_up.status_code == 404, follow_up.text


def test_cannot_access_other_users_project(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    owned = client.post(
        "/api/v1/projects",
        json={"name": "Private"},
        headers=auth_headers,
    ).json()

    intruder = register_and_login(
        client, email="mallory@example.com", full_name="Mallory"
    )

    # The intruder sees a 404 (existence is not leaked) on every verb.
    assert (
        client.get(f"/api/v1/projects/{owned['id']}", headers=intruder).status_code
        == 404
    )
    assert (
        client.patch(
            f"/api/v1/projects/{owned['id']}",
            json={"name": "Hijacked"},
            headers=intruder,
        ).status_code
        == 404
    )
    assert (
        client.delete(
            f"/api/v1/projects/{owned['id']}", headers=intruder
        ).status_code
        == 404
    )

    # The real owner's project is untouched.
    assert (
        client.get(f"/api/v1/projects/{owned['id']}", headers=auth_headers).json()[
            "name"
        ]
        == "Private"
    )
