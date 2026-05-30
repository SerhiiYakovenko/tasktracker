"""Task CRUD, filtering, pagination and board-move endpoints."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Query, Response, status

from app.api.deps import CurrentUser, DBSession
from app.models.task import TaskStatus
from app.schemas.task import (
    TaskCreate,
    TaskList,
    TaskMove,
    TaskOut,
    TaskUpdate,
)
from app.services import task_service

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("", response_model=TaskList, summary="List tasks with filters")
def list_tasks(
    db: DBSession,
    current_user: CurrentUser,
    project_id: Annotated[int | None, Query()] = None,
    status_filter: Annotated[TaskStatus | None, Query(alias="status")] = None,
    assignee_id: Annotated[int | None, Query()] = None,
    page: Annotated[int, Query(ge=1)] = 1,
    size: Annotated[int, Query(ge=1, le=100)] = 20,
) -> TaskList:
    """Return a paginated list of tasks the current user can see.

    Filters (``project_id``, ``status``, ``assignee_id``) are optional and
    combine with AND semantics.
    """
    items, total = task_service.list_tasks(
        db,
        current_user,
        project_id=project_id,
        status_filter=status_filter,
        assignee_id=assignee_id,
        page=page,
        size=size,
    )
    return TaskList(
        items=[TaskOut.model_validate(t) for t in items],
        total=total,
        page=page,
        size=size,
    )


@router.post(
    "",
    response_model=TaskOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create a task",
)
def create_task(
    payload: TaskCreate, db: DBSession, current_user: CurrentUser
) -> TaskOut:
    """Create a task within a project owned by the current user."""
    task = task_service.create_task(db, payload, current_user)
    return TaskOut.model_validate(task)


@router.get("/{task_id}", response_model=TaskOut, summary="Get a task")
def get_task(task_id: int, db: DBSession, current_user: CurrentUser) -> TaskOut:
    """Return a single task the current user can see."""
    task = task_service.get_owned_task(db, task_id, current_user)
    return TaskOut.model_validate(task)


@router.patch("/{task_id}", response_model=TaskOut, summary="Update a task")
def update_task(
    task_id: int,
    payload: TaskUpdate,
    db: DBSession,
    current_user: CurrentUser,
) -> TaskOut:
    """Apply a partial update to a task the current user can see."""
    task = task_service.update_task(db, task_id, payload, current_user)
    return TaskOut.model_validate(task)


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    summary="Delete a task",
)
def delete_task(
    task_id: int, db: DBSession, current_user: CurrentUser
) -> Response:
    """Delete a task the current user can see."""
    task_service.delete_task(db, task_id, current_user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{task_id}/move", response_model=TaskOut, summary="Move a task")
def move_task(
    task_id: int,
    payload: TaskMove,
    db: DBSession,
    current_user: CurrentUser,
) -> TaskOut:
    """Move a task to a different board column (status)."""
    task = task_service.move_task(db, task_id, payload.status, current_user)
    return TaskOut.model_validate(task)
