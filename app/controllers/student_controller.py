from fastapi import APIRouter, Depends, HTTPException
from ..services.student_service import StudentService
from ..entities.student import StudentCreate, StudentUpdate, StudentResponse, Student
from ..controllers.auth_controller import get_auth_service, get_current_user
from ..entities.user import User
from ..config.database import Database
from typing import List

router = APIRouter()

def get_student_service() -> StudentService:
    from ..main import db
    return StudentService(db)

@router.get("/", response_model=List[StudentResponse])
def list_students(service: StudentService = Depends(get_student_service), current_user: User = Depends(get_current_user)):
    """List all students"""
    return [StudentResponse(**s.model_dump()) for s in service.list_students()]

@router.post("/", response_model=StudentResponse)
def create_student(student: StudentCreate, service: StudentService = Depends(get_student_service), current_user: User = Depends(get_current_user)):
    """Create a new student (requires authentication)"""
    return service.create_student(student)

@router.put("/{s_id}", response_model=StudentResponse)
def update_student(s_id: str, student: StudentUpdate, service: StudentService = Depends(get_student_service), current_user: User = Depends(get_current_user)):
    """Update a student (requires authentication)"""
    updated = service.update_student(s_id, student)
    if not updated:
        raise HTTPException(status_code=404, detail="Student not found or no changes provided")
    return updated

@router.delete("/{s_id}")
def delete_student(s_id: str, service: StudentService = Depends(get_student_service), current_user: User = Depends(get_current_user)):
    """Delete a student (requires authentication)"""
    success = service.delete_student(s_id)
    if not success:
        raise HTTPException(status_code=404, detail="Student not found")
    return {"message": "Student deleted"}


