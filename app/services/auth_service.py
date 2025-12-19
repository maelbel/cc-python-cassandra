"""Authentication and token utilities.

This module exposes `AuthService` which centralizes password hashing,
verification, user authentication, token creation, and token-based
current-user retrieval. It relies on `UserRepository` for persistence
and `settings` for JWT configuration.
"""

from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from fastapi import HTTPException
from ..entities.user import User, UserCreate
from ..repositories.user_repository import UserRepository
from ..config.database import Database
from ..config.security import settings

pwd_context = CryptContext(schemes=["argon2", "bcrypt"], deprecated="auto")


class AuthService:
    """Service providing authentication helpers and JWT token handling.

    Responsibilities:
    - hash and verify passwords using `passlib` contexts,
    - authenticate a user by username/password,
    - create JWT access tokens with expiration,
    - register a new user (hashing the password before persistence),
    - extract the current user from a JWT token.
    """

    def __init__(self, db: Database):
        """Initialize service with a `Database` wrapper used to build repository instances."""
        self.user_repo = UserRepository(db)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Return True if `plain_password` matches `hashed_password`."""
        return pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        """Hash `password` using configured password hashing schemes."""
        return pwd_context.hash(password)

    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Return the authenticated `User` when credentials are valid, else `None`."""
        user = self.user_repo.get_user_by_username(username)
        if not user:
            return None
        if not self.verify_password(password, user.hashed_password):
            return None
        return user

    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None):
        """Create a JWT token containing `data` and an expiration claim.

        If `expires_delta` is not provided the default from `settings` is used.
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
        return encoded_jwt

    def register_user(self, user: UserCreate) -> User:
        """Register a new user by hashing the provided password and persisting the user."""
        hashed_password = self.get_password_hash(user.password)
        return self.user_repo.create_user(user, hashed_password)

    def login_user(self, form_data) -> Optional[str]:
        """Authenticate `form_data` (expected to have `username` and `password`) and
        return an access token string when successful, else `None`."""
        user = self.authenticate_user(form_data.username, form_data.password)
        if not user:
            return None
        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        access_token = self.create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )
        return access_token

    def get_current_user(self, token: str) -> User:
        """Decode `token` and return the corresponding `User` or raise HTTPException.

        Raises 401 HTTPException when token validation fails or the user
        does not exist.
        """
        credentials_exception = HTTPException(
            status_code=401,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
            username: Optional[str] = payload.get("sub")
            if username is None:
                raise credentials_exception
        except JWTError:
            raise credentials_exception
        user = self.user_repo.get_user_by_username(username)
        if user is None:
            raise credentials_exception
        return user