"""
Репозиторий для работы с книгами.
"""

from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.library_catalog.data.models.book import Book
from src.library_catalog.data.repositories.base_repository import BaseRepository


class BookRepository(BaseRepository[Book]):
    """Репозиторий для книг с дополнительными методами фильтрации."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, Book)

    async def find_by_filters(
        self,
        title: str | None = None,
        author: str | None = None,
        genre: str | None = None,
        year: int | None = None,
        available: bool | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[Book]:
        """Поиск книг с фильтрацией."""
        query = select(Book)
        if title is not None:
            query = query.where(Book.title.ilike(f"%{title}%"))
        if author is not None:
            query = query.where(Book.author.ilike(f"%{author}%"))
        if genre is not None:
            query = query.where(Book.genre.ilike(f"%{genre}%"))
        if year is not None:
            query = query.where(Book.year == year)
        if available is not None:
            query = query.where(Book.available == available)
        query = query.limit(limit).offset(offset)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def find_by_isbn(self, isbn: str) -> Book | None:
        """Найти книгу по ISBN."""
        result = await self.session.execute(
            select(Book).where(Book.isbn == isbn)
        )
        return result.scalar_one_or_none()

    async def count_by_filters(
        self,
        title: str | None = None,
        author: str | None = None,
        genre: str | None = None,
        year: int | None = None,
        available: bool | None = None,
    ) -> int:
        """Подсчитать количество книг по фильтрам."""
        query = select(func.count()).select_from(Book)
        if title is not None:
            query = query.where(Book.title.ilike(f"%{title}%"))
        if author is not None:
            query = query.where(Book.author.ilike(f"%{author}%"))
        if genre is not None:
            query = query.where(Book.genre.ilike(f"%{genre}%"))
        if year is not None:
            query = query.where(Book.year == year)
        if available is not None:
            query = query.where(Book.available == available)
        result = await self.session.execute(query)
        return result.scalar_one()


