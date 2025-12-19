from dotenv import load_dotenv
import os
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

load_dotenv()


class SecuritySettings:
    """Lightweight settings loader that reads from environment variables.

    Avoids dependency on `pydantic.BaseSettings` which may be unavailable
    depending on installed pydantic/pydantic-settings versions.
    """

    def __init__(self) -> None:
        self.secret_key: str = os.getenv("SECRET_KEY", "change-me")
        self.algorithm: str = os.getenv("ALGORITHM", "HS256")
        try:
            self.access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
        except ValueError:
            self.access_token_expire_minutes = 60
        self.allowed_origins: list[str] = [o.strip() for o in os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",") if o.strip()]


settings = SecuritySettings()


def is_default_secret() -> bool:
    """Return True if the configured secret is still the insecure default."""
    val = os.getenv("SECRET_KEY") or settings.secret_key
    return val in (None, "", "change-me")


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response: Response = await call_next(request)
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("Referrer-Policy", "no-referrer")

        return response
