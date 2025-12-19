"""Pydantic models for user and authentication payloads."""

from pydantic import BaseModel
from typing import Optional

class User(BaseModel):
    """Complete user model stored in the database.

    The `hashed_password` field stores the password hash and is not
    exposed in response models.
    """

    id: Optional[str] = None
    username: str
    email: str
    hashed_password: str
    is_active: bool = True


class UserResponse(BaseModel):
    """Public-facing user model returned by the API."""

    id: Optional[str] = None
    username: str
    email: str
    is_active: bool = True


class UserCreate(BaseModel):
    """Payload for registering a new user."""

    username: str
    email: str
    password: str


class UserLogin(BaseModel):
    """Payload used when a user attempts to authenticate."""

    username: str
    password: str


class Token(BaseModel):
    """OAuth2-style response containing an access token."""

    access_token: str
    token_type: str


class TokenData(BaseModel):
    """Optional token payload data extracted from token claims."""

    username: Optional[str] = None