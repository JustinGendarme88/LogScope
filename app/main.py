from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI

from app.database import Base, engine
from app.routers.logs import router as logs_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="LogScope API",
    description="API for uploading and analyzing server log files.",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(logs_router)


@app.get("/")
def read_root():
    return {"message": "Welcome to LogScope API"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}