from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from fastapi import HTTPException
from ..entities.user import User, UserCreate, TokenData
from ..repositories.user_repository import UserRepository
from ..config.database import Database
from ..config.security import settings

pwd_context = CryptContext(schemes=["argon2", "bcrypt"], deprecated="auto")

class AuthService:
    def __init__(self, db: Database):
        self.user_repo = UserRepository(db)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        return pwd_context.hash(password)

    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        user = self.user_repo.get_user_by_username(username)
        if not user:
            return None
        if not self.verify_password(password, user.hashed_password):
            return None
        return user

    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
        return encoded_jwt

    def register_user(self, user: UserCreate) -> User:
        hashed_password = self.get_password_hash(user.password)
        return self.user_repo.create_user(user, hashed_password)

    def login_user(self, form_data) -> Optional[str]:
        user = self.authenticate_user(form_data.username, form_data.password)
        if not user:
            return None
        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        access_token = self.create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )
        return access_token

    def get_current_user(self, token: str) -> User:
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