from cassandra.query import SimpleStatement
from ..entities.student import Student, StudentCreate, StudentUpdate
from ..config.database import Database
import uuid
from typing import List, Optional, Tuple

class StudentRepository:
    def __init__(self, db: Database):
        self.db = db

    def _get_session(self):
        session = self.db.get_session()
        if session is None:
            raise RuntimeError("Database session is not available")
        return session

    def create_student(self, student: StudentCreate) -> Student:
        student_id = str(uuid.uuid4())
        query = SimpleStatement("""
        INSERT INTO students (s_id, s_name, s_course, s_branch, s_project_id)
        VALUES (%s, %s, %s, %s, %s)
        """)
        self._get_session().execute(query, (student_id, student.s_name, student.s_course, student.s_branch, student.s_project_id))
        return Student(s_id=student_id, s_name=student.s_name, s_course=student.s_course, s_branch=student.s_branch, s_project_id=student.s_project_id)
    
    def update_student(self, s_id: str, student: StudentUpdate) -> Optional[Student]:
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
        query = SimpleStatement("DELETE FROM students WHERE s_id = %s")
        self._get_session().execute(query, (s_id,))
        return True

    def get_student(self, s_id: str) -> Optional[Student]:
        query = SimpleStatement("SELECT s_id, s_name, s_course, s_branch, s_project_id FROM students WHERE s_id = %s")
        result = self._get_session().execute(query, (s_id,))
        row = result.one()
        if row:
            return Student(s_id=row.s_id, s_name=row.s_name, s_course=row.s_course, s_branch=row.s_branch, s_project_id=row.s_project_id)
        return None

    def list_students(self, page: int = 1, size: int = 10, q: Optional[str] = None, project_id: Optional[str] = None) -> Tuple[List[Student], int]:
        """
        Return (students, total_estimate). Uses client-side slicing for pagination.
        q searches by s_id (exact) or s_name (ALLOW FILTERING fallback).
        """
        session = self._get_session()
        limit = page * size

        if project_id:
            query = SimpleStatement(f"SELECT s_id, s_name, s_course, s_branch, s_project_id FROM students WHERE s_project_id = %s LIMIT {limit}")
            rows = session.execute(query, (project_id,))
        elif q:
            try:
                uuid.UUID(q)
                query = SimpleStatement("SELECT s_id, s_name, s_course, s_branch FROM students WHERE s_id = %s")
                rows = session.execute(query, (q,))
                students = [Student(s_id=row.s_id, s_name=row.s_name, s_course=row.s_course, s_branch=row.s_branch) for row in rows]
                total = len(students)
                start = (page - 1) * size
                return students[start:start+size], total
            except (ValueError, AttributeError):
                pass

            query = SimpleStatement(f"SELECT s_id, s_name, s_course, s_branch, s_project_id FROM students WHERE s_name = %s LIMIT {limit} ALLOW FILTERING")
            rows = session.execute(query, (q,))
        else:
            query = SimpleStatement(f"SELECT s_id, s_name, s_course, s_branch, s_project_id FROM students LIMIT {limit}")
            rows = session.execute(query)

        students = [Student(s_id=row.s_id, s_name=row.s_name, s_course=row.s_course, s_branch=row.s_branch, s_project_id=getattr(row, 's_project_id', None)) for row in rows]

        total = len(students)

        start = (page - 1) * size
        return students[start:start+size], total
