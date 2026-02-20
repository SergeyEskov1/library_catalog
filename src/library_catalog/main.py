"""
Library Catalog API - Точка входа приложения.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.library_catalog.core.config import settings
from src.library_catalog.core.database import dispose_engine
from src.library_catalog.core.exceptions import register_exception_handlers
from src.library_catalog.core.logging_config import setup_logging
from src.library_catalog.api.v1.routers import books, health


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    print("Application started")
    yield
    await dispose_engine()
    print("Application stopped")


app = FastAPI(
    title=settings.app_name,
    description="REST API для управления библиотечным каталогом",
    version="1.0.0",
    docs_url=settings.docs_url,
    redoc_url=settings.redoc_url,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)

app.include_router(books.router, prefix=settings.api_v1_prefix)
app.include_router(health.router, prefix=settings.api_v1_prefix)


@app.get("/")
async def root():
    return {
        "message": "Welcome to Library Catalog API",
        "docs": settings.docs_url,
        "version": "1.0.0",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=settings.debug)
