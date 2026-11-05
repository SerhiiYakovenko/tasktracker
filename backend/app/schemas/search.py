"""Task search request and response schemas."""

from __future__ import annotations

from pydantic import BaseModel

from app.schemas.task import TaskOut


class SearchResult(BaseModel):
    """A single search hit: the matched task plus ranking metadata."""

    task: TaskOut
    score: int
    snippet: str


class SearchResponse(BaseModel):
    """Envelope for a task search response."""

    query: str
    results: list[SearchResult]
    total: int
