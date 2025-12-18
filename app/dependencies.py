from typing import Generator
from .config.security import settings

# Lightweight get_db dependency: imports the db instance from app.main at runtime
def get_db() -> Generator:
    # Import here to avoid circular imports at module import time
    from .main import db
    yield db
