"""SQLAlchemy ORM models.

Importing this package registers every model on ``Base.metadata`` so that
:func:`app.database.create_all` can create the full schema.
"""

from app.models.project import Project
from app.models.task import Task, TaskPriority, TaskStatus
from app.models.user import User

__all__ = ["User", "Project", "Task", "TaskStatus", "TaskPriority"]
