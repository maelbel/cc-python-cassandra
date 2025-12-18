from pydantic import BaseModel
from typing import Optional
from typing import List

class Student(BaseModel):
    s_id: Optional[str] = None
    s_name: str
    s_course: str
    s_branch: str
    s_project_id: Optional[str] = None

class StudentCreate(BaseModel):
    s_name: str
    s_course: str
    s_branch: str
    s_project_id: Optional[str] = None

class StudentUpdate(BaseModel):
    s_name: Optional[str] = None
    s_course: Optional[str] = None
    s_branch: Optional[str] = None
    s_project_id: Optional[str] = None

class StudentResponse(BaseModel):
    s_id: Optional[str] = None
    s_name: str
    s_course: str
    s_branch: str
    s_project_id: Optional[str] = None


class StudentListResponse(BaseModel):
    items: List[StudentResponse]
    total: int
    page: int
    size: int
