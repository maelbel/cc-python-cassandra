from ..repositories.student_repository import StudentRepository
from ..config.database import Database
from ..entities.student import StudentCreate, StudentUpdate, Student, StudentResponse
from typing import List, Optional, Tuple
from ..exceptions import NotFoundError


class StudentService:
    def __init__(self, db: Database):
        self.repo = StudentRepository(db)

    def create_student(self, student: StudentCreate) -> StudentResponse:
        s = self.repo.create_student(student)
        return StudentResponse(**s.model_dump())

    def update_student(self, s_id: str, student: StudentUpdate) -> StudentResponse:
        updated = self.repo.update_student(s_id, student)
        if updated is None:
            raise NotFoundError(f"Student with id {s_id} not found or no changes provided")
        return StudentResponse(**updated.model_dump())

    def delete_student(self, s_id: str) -> bool:
        success = self.repo.delete_student(s_id)
        if not success:
            raise NotFoundError(f"Student with id {s_id} not found")
        return True

    def get_student(self, s_id: str) -> StudentResponse:
        s = self.repo.get_student(s_id)
        if s is None:
            raise NotFoundError(f"Student with id {s_id} not found")
        return StudentResponse(**s.model_dump())

    def list_students(self, page: int = 1, size: int = 10, q: str | None = None, project_id: str | None = None) -> Tuple[List[StudentResponse], int]:
        items, total = self.repo.list_students(page=page, size=size, q=q, project_id=project_id)
        return [StudentResponse(**s.model_dump()) for s in items], total
