from pydantic import BaseModel
from typing import Optional

class Project(BaseModel):
    p_id: Optional[str] = None
    p_name: str
    p_head: str

class ProjectCreate(BaseModel):
    p_name: str
    p_head: str

class ProjectUpdate(BaseModel):
    p_name: Optional[str] = None
    p_head: Optional[str] = None

class ProjectResponse(BaseModel):
    p_id: Optional[str] = None
    p_name: str
    p_head: str
