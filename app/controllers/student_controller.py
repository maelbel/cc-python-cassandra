from fastapi import APIRouter, Depends, HTTPException, Query
from ..services.student_service import StudentService
from ..entities.student import StudentCreate, StudentUpdate, StudentResponse, Student, StudentListResponse
from ..controllers.auth_controller import get_auth_service, get_current_user
from ..entities.user import User
from typing import List, Optional, Tuple

router = APIRouter(dependencies=[Depends(get_current_user)])

def get_student_service() -> StudentService:
    from ..main import db
    return StudentService(db)

@router.get("/", response_model=StudentListResponse)
def list_students(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    q: Optional[str] = Query(None, description="Optional search query (s_id or s_name)"),
    service: StudentService = Depends(get_student_service),
):
    """List students with pagination and optional search"""
    items, total = service.list_students(page=page, size=size, q=q)
    return StudentListResponse(
        items=[StudentResponse(**s.model_dump()) for s in items],
        total=total,
        page=page,
        size=size,
    )

@router.post("/", response_model=StudentResponse)
def create_student(student: StudentCreate, service: StudentService = Depends(get_student_service)):
    """Create a new student (requires authentication)"""
    return service.create_student(student)

@router.put("/{s_id}", response_model=StudentResponse)
def update_student(s_id: str, student: StudentUpdate, service: StudentService = Depends(get_student_service)):
    """Update a student (requires authentication)"""
    updated = service.update_student(s_id, student)
    if not updated:
        raise HTTPException(status_code=404, detail="Student not found or no changes provided")
    return updated

@router.delete("/{s_id}")
def delete_student(s_id: str, service: StudentService = Depends(get_student_service)):
    """Delete a student (requires authentication)"""
    success = service.delete_student(s_id)
    if not success:
        raise HTTPException(status_code=404, detail="Student not found")
    return {"message": "Student deleted"}


