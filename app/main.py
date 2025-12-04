from typing import Union
from contextlib import asynccontextmanager

from fastapi import FastAPI

from .config.database import Database
from .controllers.auth_controller import router as auth_router

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

app = FastAPI(
    title="My FastAPI App",
    description="A simple FastAPI application with Cassandra integration",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(auth_router, prefix="/auth", tags=["Authentication"])

@app.get("/", summary="Root endpoint", description="Returns a simple hello world message", tags=["Default"])
def read_root():
    return {"Hello": "World"}