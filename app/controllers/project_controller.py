from fastapi import APIRouter, Depends, HTTPException, Query
from ..services.project_service import ProjectService
from ..entities.project import ProjectCreate, ProjectUpdate, ProjectResponse, Project, ProjectListResponse
from ..controllers.auth_controller import get_auth_service, get_current_user
from ..entities.user import User
from typing import List, Tuple, Optional
from ..services.student_service import StudentService
from ..entities.student import StudentListResponse, StudentResponse

router = APIRouter()

def get_project_service() -> ProjectService:
    from ..main import db
    return ProjectService(db)

def get_student_service() -> StudentService:
    from ..main import db
    return StudentService(db)

@router.get("/", response_model=ProjectListResponse)
def list_projects(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    q: Optional[str] = Query(None, description="Optional search query (p_id or p_name)"),
    service: ProjectService = Depends(get_project_service),
):
    """List projects with pagination and optional search"""
    items, total = service.list_projects(page=page, size=size, q=q)
    return ProjectListResponse(
        items=[ProjectResponse(**p.model_dump()) for p in items],
        total=total,
        page=page,
        size=size,
    )

@router.post("/", response_model=ProjectResponse)
def create_project(project: ProjectCreate, service: ProjectService = Depends(get_project_service), current_user: User = Depends(get_current_user)):
    """Create a new project (requires authentication)"""
    return service.create_project(project)

@router.put("/{p_id}", response_model=ProjectResponse)
def update_project(p_id: str, project: ProjectUpdate, service: ProjectService = Depends(get_project_service), current_user: User = Depends(get_current_user)):
    """Update a project (requires authentication)"""
    updated = service.update_project(p_id, project)
    if not updated:
        raise HTTPException(status_code=404, detail="Project not found or no changes provided")
    return updated

@router.delete("/{p_id}")
def delete_project(p_id: str, service: ProjectService = Depends(get_project_service), current_user: User = Depends(get_current_user)):
    """Delete a project (requires authentication)"""
    success = service.delete_project(p_id)
    if not success:
        raise HTTPException(status_code=404, detail="Project not found")
    return {"message": "Project deleted"}


@router.get("/{p_id}/students", response_model=StudentListResponse)
def list_project_students(
    p_id: str,
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    q: Optional[str] = Query(None, description="Optional search query (s_id or s_name)"),
    service: StudentService = Depends(get_student_service),
):
    """List students for a given project with pagination and optional search"""
    items, total = service.list_students(page=page, size=size, q=q, project_id=p_id)
    return StudentListResponse(
        items=[StudentResponse(**s.model_dump()) for s in items],
        total=total,
        page=page,
        size=size,
    )
