from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from db import create_db_and_tables
from routes import books, users


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(title="Kitaab API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router)
app.include_router(books.router)

@app.get("/", tags=["Root"])
def root():
    return {"message": "Welcome to Kitaab API!"}
@app.get("/health", tags=["Health"])
def health():
    """Unauthenticated, so a load balancer can probe it without a key."""
    return {"status": "ok"}
