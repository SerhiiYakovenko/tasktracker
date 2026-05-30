"""Idempotent seed script for local development and demos.

Creates the schema if needed, a demo user, a sample project and a handful of
tasks across the board. Safe to run repeatedly: existing data is reused rather
than duplicated.

Usage::

    python -m app.seed
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import SessionLocal, create_all
from app.logging_config import configure_logging, get_logger
from app.models.project import Project
from app.models.task import Task, TaskPriority, TaskStatus
from app.models.user import User
from app.schemas.user import UserCreate
from app.services import project_service, user_service
from app.schemas.project import ProjectCreate

settings = get_settings()
logger = get_logger(__name__)


def _get_or_create_demo_user(db: Session) -> User:
    """Return the existing demo user or create one from settings."""
    existing = user_service.get_by_email(db, settings.seed_user_email)
    if existing is not None:
        logger.info("Demo user already exists (id=%s)", existing.id)
        return existing

    user = user_service.create_user(
        db,
        UserCreate(
            email=settings.seed_user_email,
            password=settings.seed_user_password,
            full_name=settings.seed_user_name,
        ),
    )
    logger.info("Created demo user id=%s", user.id)
    return user


def _get_or_create_project(db: Session, owner: User) -> Project:
    """Return the demo project or create it if absent."""
    for project in project_service.list_projects(db, owner):
        if project.name == "Website Relaunch":
            logger.info("Demo project already exists (id=%s)", project.id)
            return project

    project = project_service.create_project(
        db,
        ProjectCreate(
            name="Website Relaunch",
            description="Rebuild the marketing site and migrate the blog.",
        ),
        owner,
    )
    logger.info("Created demo project id=%s", project.id)
    return project


def _seed_tasks(db: Session, project: Project, assignee: User) -> None:
    """Create a small set of sample tasks if the project has none."""
    if project.tasks:
        logger.info("Project id=%s already has tasks; skipping", project.id)
        return

    now = datetime.now(timezone.utc)
    samples = [
        Task(
            title="Audit current site content",
            description="Catalogue pages worth migrating.",
            status=TaskStatus.DONE,
            priority=TaskPriority.MEDIUM,
            project_id=project.id,
            assignee_id=assignee.id,
            due_date=now - timedelta(days=2),
        ),
        Task(
            title="Design new landing page",
            description="High-fidelity mockups for the hero and features.",
            status=TaskStatus.IN_PROGRESS,
            priority=TaskPriority.HIGH,
            project_id=project.id,
            assignee_id=assignee.id,
            due_date=now + timedelta(days=3),
        ),
        Task(
            title="Set up CI pipeline",
            description="Lint, test and build on every push.",
            status=TaskStatus.TODO,
            priority=TaskPriority.HIGH,
            project_id=project.id,
            assignee_id=None,
            due_date=now + timedelta(days=7),
        ),
        Task(
            title="Write migration runbook",
            description="Document the cutover steps and rollback plan.",
            status=TaskStatus.TODO,
            priority=TaskPriority.LOW,
            project_id=project.id,
            assignee_id=assignee.id,
            due_date=None,
        ),
    ]
    db.add_all(samples)
    db.commit()
    logger.info("Seeded %d tasks for project id=%s", len(samples), project.id)


def seed() -> None:
    """Run the full seeding routine."""
    create_all()
    with SessionLocal() as db:
        user = _get_or_create_demo_user(db)
        project = _get_or_create_project(db, user)
        _seed_tasks(db, project, user)
    logger.info("Seeding complete.")


if __name__ == "__main__":
    configure_logging(settings.log_level)
    seed()
