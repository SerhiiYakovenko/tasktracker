"""Task request and response schemas."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.task import TaskPriority, TaskStatus


class TaskCreate(BaseModel):
    """Payload for creating a task."""

    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=8000)
    project_id: int
    status: TaskStatus = TaskStatus.TODO
    priority: TaskPriority = TaskPriority.MEDIUM
    assignee_id: int | None = None
    due_date: datetime | None = None


class TaskUpdate(BaseModel):
    """Partial update for a task. Unset fields are left unchanged."""

    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=8000)
    status: TaskStatus | None = None
    priority: TaskPriority | None = None
    assignee_id: int | None = None
    due_date: datetime | None = None


class TaskMove(BaseModel):
    """Payload for moving a task to a new board column."""

    status: TaskStatus


class TaskOut(BaseModel):
    """Public representation of a task."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str | None
    status: TaskStatus
    priority: TaskPriority
    project_id: int
    assignee_id: int | None
    due_date: datetime | None
    created_at: datetime
    updated_at: datetime


class TaskList(BaseModel):
    """Paginated collection of tasks."""

    items: list[TaskOut]
    total: int
    page: int
    size: int
