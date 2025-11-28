from typing import Union
from contextlib import asynccontextmanager

from fastapi import FastAPI

from database import Database

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

app = FastAPI(lifespan=lifespan)

@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}