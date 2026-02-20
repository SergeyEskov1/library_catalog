"""
Роутер для эндпоинтов книг.
"""

from uuid import UUID
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from src.library_catalog.api.v1.schemas.book import BookCreate, BookUpdate, ShowBook
from src.library_catalog.api.v1.schemas.common import PaginatedResponse, PaginationParams
from src.library_catalog.api.dependencies import BookServiceDep

router = APIRouter(prefix="/books", tags=["Books"])


@router.post(
    "/",
    response_model=ShowBook,
    status_code=status.HTTP_201_CREATED,
    summary="Создать книгу",
)
async def create_book(book_data: BookCreate, service: BookServiceDep):
    """Создать новую книгу с обогащением из Open Library."""
    return await service.create_book(book_data)


@router.get(
    "/",
    response_model=PaginatedResponse[ShowBook],
    summary="Получить список книг",
)
async def get_books(
    service: BookServiceDep,
    pagination: Annotated[PaginationParams, Depends()],
    title: str | None = Query(None, description="Поиск по названию"),
    author: str | None = Query(None, description="Поиск по автору"),
    genre: str | None = Query(None, description="Фильтр по жанру"),
    year: int | None = Query(None, description="Фильтр по году"),
    available: bool | None = Query(None, description="Фильтр по доступности"),
):
    """Получить список книг с фильтрацией и пагинацией."""
    books, total = await service.search_books(
        title=title,
        author=author,
        genre=genre,
        year=year,
        available=available,
        limit=pagination.limit,
        offset=pagination.offset,
    )
    return PaginatedResponse.create(books, total, pagination)


@router.get(
    "/{book_id}",
    response_model=ShowBook,
    summary="Получить книгу",
)
async def get_book(book_id: UUID, service: BookServiceDep):
    """Получить книгу по ID."""
    return await service.get_book(book_id)


@router.patch(
    "/{book_id}",
    response_model=ShowBook,
    summary="Обновить книгу",
)
async def update_book(book_id: UUID, book_data: BookUpdate, service: BookServiceDep):
    """Частичное обновление книги."""
    return await service.update_book(book_id, book_data)


@router.delete(
    "/{book_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить книгу",
)
async def delete_book(book_id: UUID, service: BookServiceDep):
    """Удалить книгу."""
    await service.delete_book(book_id)
