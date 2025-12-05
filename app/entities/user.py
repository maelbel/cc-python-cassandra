from pydantic import BaseModel
from typing import Optional

class User(BaseModel):
    id: Optional[str] = None
    username: str
    email: str
    hashed_password: str
    is_active: bool = True

class UserResponse(BaseModel):
    id: Optional[str] = None
    username: str
    email: str
    is_active: bool = True

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None