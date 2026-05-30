"""Task business logic.

Tasks are reachable only through projects the current user owns. Every task
operation therefore first resolves and authorises the owning project. The
listing endpoint supports filtering by project, status and assignee, plus
offset/limit pagination.
"""

from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from app.logging_config import get_logger
from app.models.project import Project
from app.models.task import Task, TaskStatus
from app.models.user import User
from app.schemas.task import TaskCreate, TaskUpdate
from app.services import project_service

logger = get_logger(__name__)


def _not_found() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Task not found.",
    )


def _owned_tasks_query(owner: User) -> Select[tuple[Task]]:
    """Base query selecting tasks within projects owned by ``owner``."""
    return (
        select(Task)
        .join(Project, Task.project_id == Project.id)
        .where(Project.owner_id == owner.id)
    )


def get_owned_task(db: Session, task_id: int, owner: User) -> Task:
    """Return a task that belongs to a project owned by ``owner``.

    Raises:
        HTTPException: 404 if missing or not owned by the caller.
    """
    stmt = _owned_tasks_query(owner).where(Task.id == task_id)
    task = db.execute(stmt).scalar_one_or_none()
    if task is None:
        raise _not_found()
    return task


def _validate_assignee(db: Session, assignee_id: int | None) -> None:
    """Ensure an assignee, if provided, refers to an existing active user."""
    if assignee_id is None:
        return
    user = db.get(User, assignee_id)
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Assignee does not exist or is inactive.",
        )


def list_tasks(
    db: Session,
    owner: User,
    *,
    project_id: int | None = None,
    status_filter: TaskStatus | None = None,
    assignee_id: int | None = None,
    page: int = 1,
    size: int = 20,
) -> tuple[list[Task], int]:
    """List tasks visible to ``owner`` with optional filters and pagination.

    Returns a tuple of ``(items, total)`` where ``total`` is the count before
    pagination is applied.
    """
    base = _owned_tasks_query(owner)
    if project_id is not None:
        base = base.where(Task.project_id == project_id)
    if status_filter is not None:
        base = base.where(Task.status == status_filter)
    if assignee_id is not None:
        base = base.where(Task.assignee_id == assignee_id)

    count_stmt = select(func.count()).select_from(base.subquery())
    total = db.execute(count_stmt).scalar_one()

    offset = (page - 1) * size
    page_stmt = (
        base.order_by(Task.created_at.desc()).offset(offset).limit(size)
    )
    items = list(db.execute(page_stmt).scalars().all())
    return items, total


def create_task(db: Session, payload: TaskCreate, owner: User) -> Task:
    """Create a task within a project the caller owns."""
    # Authorise the target project (raises 404 if not owned).
    project_service.get_owned_project(db, payload.project_id, owner)
    _validate_assignee(db, payload.assignee_id)

    task = Task(
        title=payload.title,
        description=payload.description,
        status=payload.status,
        priority=payload.priority,
        project_id=payload.project_id,
        assignee_id=payload.assignee_id,
        due_date=payload.due_date,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    logger.info("Created task id=%s project_id=%s", task.id, task.project_id)
    return task


def update_task(
    db: Session, task_id: int, payload: TaskUpdate, owner: User
) -> Task:
    """Apply a partial update to an owned task."""
    task = get_owned_task(db, task_id, owner)
    data = payload.model_dump(exclude_unset=True)
    if "assignee_id" in data:
        _validate_assignee(db, data["assignee_id"])
    for field, value in data.items():
        setattr(task, field, value)
    db.commit()
    db.refresh(task)
    logger.info("Updated task id=%s fields=%s", task.id, list(data))
    return task


def move_task(db: Session, task_id: int, new_status: TaskStatus, owner: User) -> Task:
    """Move a task to a new board column (status)."""
    task = get_owned_task(db, task_id, owner)
    task.status = new_status
    db.commit()
    db.refresh(task)
    logger.info("Moved task id=%s to status=%s", task.id, new_status.value)
    return task


def delete_task(db: Session, task_id: int, owner: User) -> None:
    """Delete an owned task."""
    task = get_owned_task(db, task_id, owner)
    db.delete(task)
    db.commit()
    logger.info("Deleted task id=%s owner_id=%s", task_id, owner.id)
