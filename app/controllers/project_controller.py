from fastapi import APIRouter, Depends, HTTPException
from ..services.project_service import ProjectService
from ..entities.project import ProjectCreate, ProjectUpdate, ProjectResponse, Project
from ..controllers.auth_controller import get_auth_service, get_current_user
from ..entities.user import User
from typing import List

router = APIRouter()

def get_project_service() -> ProjectService:
    from ..main import db
    return ProjectService(db)

@router.get("/", response_model=List[ProjectResponse])
def list_projects(service: ProjectService = Depends(get_project_service)):
    """List all projects"""
    return [ProjectResponse(**p.model_dump()) for p in service.list_projects()]

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
