"""Pydantic models for the project domain.

These models validate and structure project data exchanged by the API
and stored in Cassandra.
"""

from pydantic import BaseModel
from typing import Optional, List

class Project(BaseModel):
    """Full representation of a project stored in the database."""

    p_id: Optional[str] = None
    p_name: str
    p_head: str


class ProjectCreate(BaseModel):
    """Payload model for creating a new project."""

    p_name: str
    p_head: str


class ProjectUpdate(BaseModel):
    """Payload model for updating a project. All fields optional."""

    p_name: Optional[str] = None
    p_head: Optional[str] = None


class ProjectResponse(BaseModel):
    """Response model for project data."""

    p_id: Optional[str] = None
    p_name: str
    p_head: str


class ProjectListResponse(BaseModel):
    """Paginated list response for projects."""

    items: List[ProjectResponse]
    total: int
    page: int
    size: int
