"""Tests for task CRUD, board moves, filtering and pagination."""

from __future__ import annotations

from fastapi.testclient import TestClient

from tests.conftest import register_and_login


def _create_task(
    client: TestClient,
    auth_headers: dict[str, str],
    project_id: int,
    **overrides: object,
) -> dict:
    """Create a task and return its JSON body, asserting a 201."""
    payload: dict[str, object] = {
        "title": "A task",
        "project_id": project_id,
    }
    payload.update(overrides)
    resp = client.post("/api/v1/tasks", json=payload, headers=auth_headers)
    assert resp.status_code == 201, resp.text
    return resp.json()


def test_create_task_defaults(
    client: TestClient, auth_headers: dict[str, str], project_id: int
) -> None:
    body = _create_task(client, auth_headers, project_id, title="Write docs")
    assert body["title"] == "Write docs"
    assert body["project_id"] == project_id
    assert body["status"] == "todo"
    assert body["priority"] == "medium"
    assert body["assignee_id"] is None
    assert body["due_date"] is None
    assert "created_at" in body
    assert "updated_at" in body


def test_create_task_with_explicit_fields(
    client: TestClient, auth_headers: dict[str, str], project_id: int
) -> None:
    body = _create_task(
        client,
        auth_headers,
        project_id,
        title="Ship it",
        description="Cut the release",
        status="in_progress",
        priority="high",
        due_date="2030-01-01T12:00:00Z",
    )
    assert body["status"] == "in_progress"
    assert body["priority"] == "high"
    assert body["description"] == "Cut the release"
    assert body["due_date"] is not None


def test_create_task_requires_auth(
    client: TestClient, project_id: int
) -> None:
    resp = client.post(
        "/api/v1/tasks", json={"title": "x", "project_id": project_id}
    )
    assert resp.status_code == 401, resp.text


def test_create_task_in_unowned_project_404(
    client: TestClient, auth_headers: dict[str, str], project_id: int
) -> None:
    intruder = register_and_login(client, email="eve@example.com", full_name="Eve")
    resp = client.post(
        "/api/v1/tasks",
        json={"title": "Sneaky", "project_id": project_id},
        headers=intruder,
    )
    assert resp.status_code == 404, resp.text


def test_create_task_with_invalid_assignee_422(
    client: TestClient, auth_headers: dict[str, str], project_id: int
) -> None:
    resp = client.post(
        "/api/v1/tasks",
        json={"title": "Assign nobody", "project_id": project_id, "assignee_id": 999999},
        headers=auth_headers,
    )
    assert resp.status_code == 422, resp.text


def test_create_task_invalid_status_422(
    client: TestClient, auth_headers: dict[str, str], project_id: int
) -> None:
    resp = client.post(
        "/api/v1/tasks",
        json={"title": "Bad status", "project_id": project_id, "status": "archived"},
        headers=auth_headers,
    )
    assert resp.status_code == 422, resp.text


def test_get_task(
    client: TestClient, auth_headers: dict[str, str], project_id: int
) -> None:
    created = _create_task(client, auth_headers, project_id)
    resp = client.get(f"/api/v1/tasks/{created['id']}", headers=auth_headers)
    assert resp.status_code == 200, resp.text
    assert resp.json()["id"] == created["id"]


def test_get_missing_task_404(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    resp = client.get("/api/v1/tasks/999999", headers=auth_headers)
    assert resp.status_code == 404, resp.text


def test_update_task(
    client: TestClient, auth_headers: dict[str, str], project_id: int
) -> None:
    created = _create_task(client, auth_headers, project_id, title="Before")
    resp = client.patch(
        f"/api/v1/tasks/{created['id']}",
        json={"title": "After", "priority": "low"},
        headers=auth_headers,
    )
    assert resp.status_code == 200, resp.text

    body = resp.json()
    assert body["title"] == "After"
    assert body["priority"] == "low"
    # Unset fields stay as they were.
    assert body["status"] == "todo"


def test_move_task_changes_status(
    client: TestClient, auth_headers: dict[str, str], project_id: int
) -> None:
    created = _create_task(client, auth_headers, project_id)
    assert created["status"] == "todo"

    resp = client.post(
        f"/api/v1/tasks/{created['id']}/move",
        json={"status": "done"},
        headers=auth_headers,
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["status"] == "done"


def test_move_task_invalid_status_422(
    client: TestClient, auth_headers: dict[str, str], project_id: int
) -> None:
    created = _create_task(client, auth_headers, project_id)
    resp = client.post(
        f"/api/v1/tasks/{created['id']}/move",
        json={"status": "nope"},
        headers=auth_headers,
    )
    assert resp.status_code == 422, resp.text


def test_delete_task(
    client: TestClient, auth_headers: dict[str, str], project_id: int
) -> None:
    created = _create_task(client, auth_headers, project_id)
    delete_resp = client.delete(
        f"/api/v1/tasks/{created['id']}", headers=auth_headers
    )
    assert delete_resp.status_code == 204, delete_resp.text

    follow_up = client.get(f"/api/v1/tasks/{created['id']}", headers=auth_headers)
    assert follow_up.status_code == 404, follow_up.text


def test_list_tasks_envelope(
    client: TestClient, auth_headers: dict[str, str], project_id: int
) -> None:
    _create_task(client, auth_headers, project_id, title="One")
    _create_task(client, auth_headers, project_id, title="Two")

    resp = client.get("/api/v1/tasks", headers=auth_headers)
    assert resp.status_code == 200, resp.text

    body = resp.json()
    assert set(body) == {"items", "total", "page", "size"}
    assert body["total"] == 2
    assert body["page"] == 1
    assert body["size"] == 20
    assert len(body["items"]) == 2


def test_list_tasks_filter_by_status(
    client: TestClient, auth_headers: dict[str, str], project_id: int
) -> None:
    _create_task(client, auth_headers, project_id, title="todo-1", status="todo")
    _create_task(client, auth_headers, project_id, title="todo-2", status="todo")
    _create_task(client, auth_headers, project_id, title="done-1", status="done")

    resp = client.get(
        "/api/v1/tasks", params={"status": "done"}, headers=auth_headers
    )
    assert resp.status_code == 200, resp.text

    body = resp.json()
    assert body["total"] == 1
    assert body["items"][0]["title"] == "done-1"
    assert all(item["status"] == "done" for item in body["items"])


def test_list_tasks_filter_by_project(
    client: TestClient, auth_headers: dict[str, str], project_id: int
) -> None:
    other_project = client.post(
        "/api/v1/projects", json={"name": "Other"}, headers=auth_headers
    ).json()["id"]

    _create_task(client, auth_headers, project_id, title="In A")
    _create_task(client, auth_headers, other_project, title="In B")

    resp = client.get(
        "/api/v1/tasks", params={"project_id": project_id}, headers=auth_headers
    )
    assert resp.status_code == 200, resp.text

    body = resp.json()
    assert body["total"] == 1
    assert body["items"][0]["title"] == "In A"
    assert all(item["project_id"] == project_id for item in body["items"])


def test_list_tasks_filter_by_assignee(
    client: TestClient,
    auth_headers: dict[str, str],
    project_id: int,
) -> None:
    me = client.get("/api/v1/users/me", headers=auth_headers).json()["id"]

    _create_task(client, auth_headers, project_id, title="Assigned", assignee_id=me)
    _create_task(client, auth_headers, project_id, title="Unassigned")

    resp = client.get(
        "/api/v1/tasks", params={"assignee_id": me}, headers=auth_headers
    )
    assert resp.status_code == 200, resp.text

    body = resp.json()
    assert body["total"] == 1
    assert body["items"][0]["assignee_id"] == me


def test_list_tasks_pagination(
    client: TestClient, auth_headers: dict[str, str], project_id: int
) -> None:
    for index in range(5):
        _create_task(client, auth_headers, project_id, title=f"Task {index}")

    first_page = client.get(
        "/api/v1/tasks", params={"page": 1, "size": 2}, headers=auth_headers
    ).json()
    assert first_page["total"] == 5
    assert first_page["page"] == 1
    assert first_page["size"] == 2
    assert len(first_page["items"]) == 2

    third_page = client.get(
        "/api/v1/tasks", params={"page": 3, "size": 2}, headers=auth_headers
    ).json()
    assert third_page["total"] == 5
    assert len(third_page["items"]) == 1  # 5 items, last page has the remainder

    # No item appears on more than one page.
    first_ids = {item["id"] for item in first_page["items"]}
    third_ids = {item["id"] for item in third_page["items"]}
    assert first_ids.isdisjoint(third_ids)


def test_list_tasks_excludes_other_users_tasks(
    client: TestClient, auth_headers: dict[str, str], project_id: int
) -> None:
    _create_task(client, auth_headers, project_id, title="Mine")

    other = register_and_login(client, email="otto@example.com", full_name="Otto")
    other_project = client.post(
        "/api/v1/projects", json={"name": "Otto's"}, headers=other
    ).json()["id"]
    client.post(
        "/api/v1/tasks",
        json={"title": "Otto's task", "project_id": other_project},
        headers=other,
    )

    resp = client.get("/api/v1/tasks", headers=auth_headers)
    body = resp.json()
    assert body["total"] == 1
    assert body["items"][0]["title"] == "Mine"


def test_cannot_access_other_users_task(
    client: TestClient, auth_headers: dict[str, str], project_id: int
) -> None:
    created = _create_task(client, auth_headers, project_id)

    intruder = register_and_login(
        client, email="trudy@example.com", full_name="Trudy"
    )
    task_url = f"/api/v1/tasks/{created['id']}"

    assert client.get(task_url, headers=intruder).status_code == 404
    assert (
        client.patch(task_url, json={"title": "Hijack"}, headers=intruder).status_code
        == 404
    )
    assert (
        client.post(
            f"{task_url}/move", json={"status": "done"}, headers=intruder
        ).status_code
        == 404
    )
    assert client.delete(task_url, headers=intruder).status_code == 404
