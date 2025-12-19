"""Repository implementation for student CRUD operations using Cassandra."""

from cassandra.query import SimpleStatement
from ..entities.student import Student, StudentCreate, StudentUpdate
from ..config.database import Database
import uuid
from typing import List, Optional, Tuple
from .base import BaseRepository

class StudentRepository(BaseRepository):
    """Encapsulates Cassandra queries for the `students` table.

    Methods return `Student` Pydantic models or primitives (e.g.
    boolean for deletion). The repository uses the helpers on
    `BaseRepository` to fetch sessions and perform simple searches.
    """

    def __init__(self, db: Database):
        super().__init__(db)
        self.table = "students"
        self.select_cols = "s_id, s_name, s_course, s_branch, s_project_id"
        self.prefix = "s"

    def create_student(self, student: StudentCreate) -> Student:
        """Insert a new student row and return the created `Student` model.

        A UUID is generated for the `s_id` field.
        """
        student_id = str(uuid.uuid4())
        query = SimpleStatement("""
        INSERT INTO students (s_id, s_name, s_course, s_branch, s_project_id)
        VALUES (%s, %s, %s, %s, %s)
        """)
        self._get_session().execute(query, (student_id, student.s_name, student.s_course, student.s_branch, student.s_project_id))
        return Student(s_id=student_id, s_name=student.s_name, s_course=student.s_course, s_branch=student.s_branch, s_project_id=student.s_project_id)

    def update_student(self, s_id: str, student: StudentUpdate) -> Optional[Student]:
        """Apply partial updates to a student and return the updated model.

        If the provided `student` has no fields set, the method returns
        `None` to indicate there was nothing to change.
        """
        sets = []
        params = []
        if student.s_name is not None:
            sets.append("s_name = %s")
            params.append(student.s_name)
        if student.s_course is not None:
            sets.append("s_course = %s")
            params.append(student.s_course)
        if student.s_branch is not None:
            sets.append("s_branch = %s")
            params.append(student.s_branch)
        if student.s_project_id is not None:
            sets.append("s_project_id = %s")
            params.append(student.s_project_id)
        if not sets:
            return None
        set_clause = ", ".join(sets)
        query = SimpleStatement(f"UPDATE students SET {set_clause} WHERE s_id = %s")
        params.append(s_id)
        self._get_session().execute(query, tuple(params))
        return self.get_student(s_id)

    def delete_student(self, s_id: str) -> bool:
        """Delete the student with the given id. Returns True on success."""
        query = SimpleStatement("DELETE FROM students WHERE s_id = %s")
        self._get_session().execute(query, (s_id,))
        return True

    def get_student(self, s_id: str) -> Optional[Student]:
        """Fetch a single student by id and return a `Student` model or None."""
        query = SimpleStatement("SELECT s_id, s_name, s_course, s_branch, s_project_id FROM students WHERE s_id = %s")
        result = self._get_session().execute(query, (s_id,))
        row = result.one()
        if row:
            return Student(s_id=row.s_id, s_name=row.s_name, s_course=row.s_course, s_branch=row.s_branch, s_project_id=row.s_project_id)
        return None

    def list_students(self, page: int = 1, size: int = 10, q: Optional[str] = None, project_id: Optional[str] = None) -> Tuple[List[Student], int]:
        """Return a paginated list of students and the total count.

        Optionally filter by `project_id` and search using `q` (delegated
        to `BaseRepository.list_with_search`).
        """
        filters = None
        if project_id:
            filters = {"s_project_id": project_id}

        rows, total = self.list_with_search(
            page=page,
            size=size,
            q=q,
            filters=filters,
        )

        students = [Student(s_id=row.s_id, s_name=row.s_name, s_course=row.s_course, s_branch=row.s_branch, s_project_id=getattr(row, 's_project_id', None)) for row in rows]

        return students, total
