"""API routes for student management.

All endpoints in this router require an authenticated user. The router
provides list, create, update and delete operations for `Student`
resources. The endpoints delegate business logic to
`StudentService`.
"""

from fastapi import APIRouter, Depends, Query
from ..services.student_service import StudentService
from ..dependencies import get_db
from ..entities.student import StudentCreate, StudentUpdate, StudentResponse, StudentListResponse
from ..controllers.auth_controller import get_current_user
from typing import Optional

router = APIRouter(dependencies=[Depends(get_current_user)])


def get_student_service(db=Depends(get_db)) -> StudentService:
    """Dependency provider returning a `StudentService` instance."""
    return StudentService(db)


@router.get("/", response_model=StudentListResponse)
def list_students(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    q: Optional[str] = Query(None, description="Optional search query (s_id or s_name)"),
    service: StudentService = Depends(get_student_service),
):
    """Return a paginated list of students.

    Query param `q` may be a UUID to search by id or a string to search
    by name. Results are returned in a `StudentListResponse` object.
    """
    items, total = service.list_students(page=page, size=size, q=q)
    return StudentListResponse(
        items=items,
        total=total,
        page=page,
        size=size,
    )


@router.post("/", response_model=StudentResponse)
def create_student(student: StudentCreate, service: StudentService = Depends(get_student_service)):
    """Create and return a new student. Requires authentication."""
    return service.create_student(student)


@router.put("/{s_id}", response_model=StudentResponse)
def update_student(s_id: str, student: StudentUpdate, service: StudentService = Depends(get_student_service)):
    """Update an existing student identified by `s_id`. Returns the updated student."""
    updated = service.update_student(s_id, student)
    return updated


@router.delete("/{s_id}")
def delete_student(s_id: str, service: StudentService = Depends(get_student_service)):
    """Delete the student with the given `s_id` and return a confirmation message."""
    service.delete_student(s_id)
    return {"message": "Student deleted"}


