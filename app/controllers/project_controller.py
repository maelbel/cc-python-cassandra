"""API routes for project management and related student queries.

All endpoints require authentication. This module exposes CRUD
endpoints for projects and an endpoint to list students assigned to a
project.
"""

from fastapi import APIRouter, Depends, Query
from ..services.project_service import ProjectService
from ..dependencies import get_db
from ..entities.project import ProjectCreate, ProjectUpdate, ProjectResponse, ProjectListResponse
from ..controllers.auth_controller import get_current_user
from typing import Optional
from ..services.student_service import StudentService
from ..entities.student import StudentListResponse

router = APIRouter(dependencies=[Depends(get_current_user)])


def get_project_service(db=Depends(get_db)) -> ProjectService:
    """Return a `ProjectService` instance for dependency injection."""
    return ProjectService(db)


def get_student_service(db=Depends(get_db)) -> StudentService:
    """Return a `StudentService` instance for dependency injection."""
    return StudentService(db)


@router.get("/", response_model=ProjectListResponse)
def list_projects(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    q: Optional[str] = Query(None, description="Optional search query (p_id or p_name)"),
    service: ProjectService = Depends(get_project_service),
):
    """Return a paginated list of projects. Supports `q` search by id or name."""
    items, total = service.list_projects(page=page, size=size, q=q)
    return ProjectListResponse(
        items=items,
        total=total,
        page=page,
        size=size,
    )


@router.post("/", response_model=ProjectResponse)
def create_project(project: ProjectCreate, service: ProjectService = Depends(get_project_service)):
    """Create a new project and return it."""
    return service.create_project(project)


@router.put("/{p_id}", response_model=ProjectResponse)
def update_project(p_id: str, project: ProjectUpdate, service: ProjectService = Depends(get_project_service)):
    """Update a project identified by `p_id` and return the updated resource."""
    updated = service.update_project(p_id, project)
    return updated


@router.delete("/{p_id}")
def delete_project(p_id: str, service: ProjectService = Depends(get_project_service)):
    """Delete the project with id `p_id` and return a confirmation message."""
    service.delete_project(p_id)
    return {"message": "Project deleted"}


@router.get("/{p_id}/students", response_model=StudentListResponse)
def list_project_students(
    p_id: str,
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    q: Optional[str] = Query(None, description="Optional search query (s_id or s_name)"),
    service: StudentService = Depends(get_student_service)
):
    """List students assigned to the given project id with pagination."""
    items, total = service.list_students(page=page, size=size, q=q, project_id=p_id)
    return StudentListResponse(
        items=items,
        total=total,
        page=page,
        size=size,
    )
