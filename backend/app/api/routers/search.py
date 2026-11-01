"""Task search endpoint."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Query

from app.api.deps import CurrentUser, DBSession
from app.schemas.search import SearchResponse, SearchResult
from app.schemas.task import TaskOut
from app.services import search_service

router = APIRouter(prefix="/search", tags=["search"])


@router.get("", response_model=SearchResponse, summary="Search tasks")
def search_tasks(
    db: DBSession,
    current_user: CurrentUser,
    q: Annotated[str, Query(min_length=1, description="Free-text query")],
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
) -> SearchResponse:
    """Search the current user's tasks by title and description."""
    hits = search_service.search_tasks(db, current_user, query=q, limit=limit)
    results = [
        SearchResult(
            task=TaskOut.model_validate(hit["task"]),
            score=hit["score"],
            snippet=hit["snippet"],
        )
        for hit in hits
    ]
    return SearchResponse(query=q, results=results, total=len(results))
