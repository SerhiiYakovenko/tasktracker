"""Project CRUD endpoints. All operations are scoped to the current user."""

from __future__ import annotations

from fastapi import APIRouter, Response, status

from app.api.deps import CurrentUser, DBSession
from app.schemas.project import ProjectCreate, ProjectOut, ProjectUpdate
from app.services import project_service

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("", response_model=list[ProjectOut], summary="List your projects")
def list_projects(db: DBSession, current_user: CurrentUser) -> list[ProjectOut]:
    """Return all projects owned by the current user."""
    projects = project_service.list_projects(db, current_user)
    return [ProjectOut.model_validate(p) for p in projects]


@router.post(
    "",
    response_model=ProjectOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create a project",
)
def create_project(
    payload: ProjectCreate, db: DBSession, current_user: CurrentUser
) -> ProjectOut:
    """Create a project owned by the current user."""
    project = project_service.create_project(db, payload, current_user)
    return ProjectOut.model_validate(project)


@router.get("/{project_id}", response_model=ProjectOut, summary="Get a project")
def get_project(
    project_id: int, db: DBSession, current_user: CurrentUser
) -> ProjectOut:
    """Return a single project owned by the current user."""
    project = project_service.get_owned_project(db, project_id, current_user)
    return ProjectOut.model_validate(project)


@router.patch("/{project_id}", response_model=ProjectOut, summary="Update a project")
def update_project(
    project_id: int,
    payload: ProjectUpdate,
    db: DBSession,
    current_user: CurrentUser,
) -> ProjectOut:
    """Apply a partial update to a project owned by the current user."""
    project = project_service.update_project(db, project_id, payload, current_user)
    return ProjectOut.model_validate(project)


@router.delete(
    "/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    summary="Delete a project",
)
def delete_project(
    project_id: int, db: DBSession, current_user: CurrentUser
) -> Response:
    """Delete a project (and its tasks) owned by the current user."""
    project_service.delete_project(db, project_id, current_user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
