"""Repository utilities for user persistence in Cassandra."""

from cassandra.query import SimpleStatement
from ..entities.user import User, UserCreate
from ..config.database import Database
import uuid
from typing import Optional

class UserRepository:
    """Handles user creation and lookup operations.

    Note: the repository returns `User` Pydantic models including the
    `hashed_password` field. Callers should avoid exposing that field in
    API responses and use `UserResponse` where appropriate.
    """

    def __init__(self, db: Database):
        self.db = db

    def create_user(self, user: UserCreate, hashed_password: str) -> User:
        """Create a new user row and return the stored `User` model."""
        user_id = str(uuid.uuid4())
        query = SimpleStatement("""
        INSERT INTO users (id, username, email, hashed_password, is_active)
        VALUES (%s, %s, %s, %s, %s)
        """)
        self.db.get_session().execute(query, (user_id, user.username, user.email, hashed_password, True))
        return User(id=user_id, username=user.username, email=user.email, hashed_password=hashed_password)

    def get_user_by_username(self, username: str) -> Optional[User]:
        """Return the `User` with the given username or `None` if absent."""
        query = SimpleStatement("SELECT id, username, email, hashed_password, is_active FROM users WHERE username = %s")
        result = self.db.get_session().execute(query, (username,))
        row = result.one()
        if row:
            return User(id=row.id, username=row.username, email=row.email, hashed_password=row.hashed_password, is_active=row.is_active)
        return None

    def get_user_by_email(self, email: str) -> Optional[User]:
        """Return the `User` with the given email or `None` if absent."""
        query = SimpleStatement("SELECT id, username, email, hashed_password, is_active FROM users WHERE email = %s")
        result = self.db.get_session().execute(query, (email,))
        row = result.one()
        if row:
            return User(id=row.id, username=row.username, email=row.email, hashed_password=row.hashed_password, is_active=row.is_active)
        return None