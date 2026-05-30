"""Project business logic.

Projects are scoped to their owner: a user may only read or mutate projects
they own. Ownership checks live here so every router path is protected
consistently.
"""

from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.logging_config import get_logger
from app.models.project import Project
from app.models.user import User
from app.schemas.project import ProjectCreate, ProjectUpdate

logger = get_logger(__name__)


def _not_found() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Project not found.",
    )


def list_projects(db: Session, owner: User) -> list[Project]:
    """Return all projects owned by ``owner``, newest first."""
    stmt = (
        select(Project)
        .where(Project.owner_id == owner.id)
        .order_by(Project.created_at.desc())
    )
    return list(db.execute(stmt).scalars().all())


def get_owned_project(db: Session, project_id: int, owner: User) -> Project:
    """Return a project owned by ``owner``.

    Raises:
        HTTPException: 404 if the project does not exist or is owned by
            someone else (we do not distinguish, to avoid leaking existence).
    """
    project = db.get(Project, project_id)
    if project is None or project.owner_id != owner.id:
        raise _not_found()
    return project


def create_project(db: Session, payload: ProjectCreate, owner: User) -> Project:
    """Create a project owned by ``owner``."""
    project = Project(
        name=payload.name,
        description=payload.description,
        owner_id=owner.id,
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    logger.info("Created project id=%s owner_id=%s", project.id, owner.id)
    return project


def update_project(
    db: Session, project_id: int, payload: ProjectUpdate, owner: User
) -> Project:
    """Apply a partial update to an owned project."""
    project = get_owned_project(db, project_id, owner)
    data = payload.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(project, field, value)
    db.commit()
    db.refresh(project)
    logger.info("Updated project id=%s fields=%s", project.id, list(data))
    return project


def delete_project(db: Session, project_id: int, owner: User) -> None:
    """Delete an owned project and its tasks (cascade)."""
    project = get_owned_project(db, project_id, owner)
    db.delete(project)
    db.commit()
    logger.info("Deleted project id=%s owner_id=%s", project_id, owner.id)
