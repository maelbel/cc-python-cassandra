"""Pydantic models describing student domain objects.

These models are used for validation and serialization across the API
layer. Field names use a simple `s_` prefix to match the underlying
storage schema.
"""

from pydantic import BaseModel
from typing import Optional, List

class Student(BaseModel):
    """Complete representation of a student as stored in the database.

    Fields:
    - `s_id`: optional string identifier (UUID stored as string).
    - `s_name`: student's full name.
    - `s_course`: course name or code.
    - `s_branch`: student's branch or specialization.
    - `s_project_id`: optional id of the associated project.
    """

    s_id: Optional[str] = None
    s_name: str
    s_course: str
    s_branch: str
    s_project_id: Optional[str] = None


class StudentCreate(BaseModel):
    """Payload model used when creating a new student.

    Only the fields required to create a student are present.
    """

    s_name: str
    s_course: str
    s_branch: str
    s_project_id: Optional[str] = None


class StudentUpdate(BaseModel):
    """Payload model used to update an existing student.

    All fields are optional to support partial updates.
    """

    s_name: Optional[str] = None
    s_course: Optional[str] = None
    s_branch: Optional[str] = None
    s_project_id: Optional[str] = None


class StudentResponse(BaseModel):
    """Model used in responses when returning student data."""

    s_id: Optional[str] = None
    s_name: str
    s_course: str
    s_branch: str
    s_project_id: Optional[str] = None


class StudentListResponse(BaseModel):
    """Paginated list response for students."""

    items: List[StudentResponse]
    total: int
    page: int
    size: int
