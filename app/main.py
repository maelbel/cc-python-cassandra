from typing import Union
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
import os

from .config.database import Database
from .controllers.auth_controller import router as auth_router
from .controllers.project_controller import router as project_router
from .controllers.student_controller import router as student_router
from .config.security import settings, is_default_secret, SecurityHeadersMiddleware
from fastapi import Request
from fastapi.responses import JSONResponse
from .exceptions import AppError, NotFoundError, ConflictError, DatabaseError

db = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global db

    contact_points = ['cassandra']
    keyspace = 'dawan'
    db = Database(contact_points, keyspace)
    yield
    if db:
        db.close()

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("app")

app = FastAPI(
    title="My FastAPI App",
    description="A simple FastAPI application with Cassandra integration",
    version="1.0.0",
    lifespan=lifespan,
)


@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    logger.exception("Application error handled: %s", exc)
    if isinstance(exc, NotFoundError):
        return JSONResponse(status_code=404, content={"detail": str(exc) or "Not found"})
    if isinstance(exc, ConflictError):
        return JSONResponse(status_code=409, content={"detail": str(exc) or "Conflict"})
    if isinstance(exc, DatabaseError):
        return JSONResponse(status_code=500, content={"detail": str(exc) or "Database error"})
    return JSONResponse(status_code=400, content={"detail": str(exc) or "Application error"})


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled exception: %s", exc)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})

allowed_origins = os.getenv("ALLOWED_ORIGINS")
if allowed_origins:
    origins = [o.strip() for o in allowed_origins.split(",") if o.strip()]
else:
    origins = ["http://localhost:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.add_middleware(SecurityHeadersMiddleware)


@app.get("/", summary="Root endpoint", description="Returns a simple hello world message", tags=["Default"])
def read_root():
    return {"Hello": "World"}


if is_default_secret():
    logger.warning("SECRET_KEY is set to default value — please set a secure SECRET_KEY in .env")


app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(project_router, prefix="/projects", tags=["Projects"])
app.include_router(student_router, prefix="/students", tags=["Students"])
