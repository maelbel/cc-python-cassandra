from pydantic import BaseModel
from typing import Optional

class Student(BaseModel):
    s_id: Optional[str] = None
    s_name: str
    s_course: str
    s_branch: str

class StudentCreate(BaseModel):
    s_name: str
    s_course: str
    s_branch: str

class StudentUpdate(BaseModel):
    s_name: Optional[str] = None
    s_course: Optional[str] = None
    s_branch: Optional[str] = None

class StudentResponse(BaseModel):
    s_id: Optional[str] = None
    s_name: str
    s_course: str
    s_branch: str
