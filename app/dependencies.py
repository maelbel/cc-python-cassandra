from typing import Generator
from .config.security import settings

def get_db() -> Generator:
    from .main import db
    yield db
