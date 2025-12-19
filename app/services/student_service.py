"""Business logic related to students.

This service exposes methods used by the API layer to create, update,
delete and list students. It translates repository return values into
Pydantic response models and raises domain-specific exceptions when
resources are not found.
"""

from ..repositories.student_repository import StudentRepository
from ..config.database import Database
from ..entities.student import StudentCreate, StudentUpdate, StudentResponse
from typing import List, Tuple, Optional
from ..exceptions import NotFoundError


class StudentService:
    """Service layer orchestrating student repository operations."""

    def __init__(self, db: Database):
        """Create a `StudentService` using the provided `db` wrapper."""
        self.repo = StudentRepository(db)

    def create_student(self, student: StudentCreate) -> StudentResponse:
        """Create a new student and return a `StudentResponse`.

        Args:
            student: `StudentCreate` payload.

        Returns:
            Created `StudentResponse`.
        """
        s = self.repo.create_student(student)
        return StudentResponse(**s.model_dump())

    def update_student(self, s_id: str, student: StudentUpdate) -> StudentResponse:
        """Update student identified by `s_id`.

        Raises `NotFoundError` if the student does not exist or no changes
        were applied.
        """
        updated = self.repo.update_student(s_id, student)
        if updated is None:
            raise NotFoundError(f"Student with id {s_id} not found or no changes provided")
        return StudentResponse(**updated.model_dump())

    def delete_student(self, s_id: str) -> bool:
        """Delete the student with id `s_id`.

        Raises `NotFoundError` when the student is not found.
        Returns True on successful deletion.
        """
        success = self.repo.delete_student(s_id)
        if not success:
            raise NotFoundError(f"Student with id {s_id} not found")
        return True

    def get_student(self, s_id: str) -> StudentResponse:
        """Retrieve a student by id, raising `NotFoundError` if absent."""
        s = self.repo.get_student(s_id)
        if s is None:
            raise NotFoundError(f"Student with id {s_id} not found")
        return StudentResponse(**s.model_dump())

    def list_students(self, page: int = 1, size: int = 10, q: Optional[str] = None, project_id: Optional[str] = None) -> Tuple[List[StudentResponse], int]:
        """Return a paginated list of students as `StudentResponse` objects.

        Supports an optional search `q` and filtering by `project_id`.
        """
        items, total = self.repo.list_students(page=page, size=size, q=q, project_id=project_id)
        return [StudentResponse(**s.model_dump()) for s in items], total
