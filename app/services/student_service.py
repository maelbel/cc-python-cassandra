from ..repositories.student_repository import StudentRepository
from ..config.database import Database
from ..entities.student import StudentCreate, StudentUpdate, Student
from typing import List, Optional, Tuple

class StudentService:
    def __init__(self, db: Database):
        self.repo = StudentRepository(db)

    def create_student(self, student: StudentCreate) -> Student:
        return self.repo.create_student(student)

    def update_student(self, s_id: str, student: StudentUpdate) -> Optional[Student]:
        return self.repo.update_student(s_id, student)

    def delete_student(self, s_id: str) -> bool:
        return self.repo.delete_student(s_id)

    def get_student(self, s_id: str) -> Optional[Student]:
        return self.repo.get_student(s_id)

    def list_students(self, page: int = 1, size: int = 10, q: str | None = None, project_id: str | None = None) -> Tuple[List[Student], int]:
        return self.repo.list_students(page=page, size=size, q=q, project_id=project_id)
