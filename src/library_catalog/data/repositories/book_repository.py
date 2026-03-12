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

    def _build_filter_conditions(
        self,
        title: str | None,
        author: str | None,
        genre: str | None,
        year: int | None,
        available: bool | None,
    ) -> list:
        """Собрать список WHERE-условий из переданных фильтров."""
        conditions = []
        if title is not None:
            conditions.append(Book.title.ilike(f"%{title}%"))
        if author is not None:
            conditions.append(Book.author.ilike(f"%{author}%"))
        if genre is not None:
            conditions.append(Book.genre.ilike(f"%{genre}%"))
        if year is not None:
            conditions.append(Book.year == year)
        if available is not None:
            conditions.append(Book.available == available)
        return conditions

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
        conditions = self._build_filter_conditions(title, author, genre, year, available)
        query = select(Book).where(*conditions).limit(limit).offset(offset)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def find_with_total(
        self,
        title: str | None = None,
        author: str | None = None,
        genre: str | None = None,
        year: int | None = None,
        available: bool | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[Book], int]:
        """Поиск книг с подсчётом через window function — один запрос к БД.

        Использует COUNT(*) OVER() вместо отдельного SELECT COUNT(*),
        что вдвое сокращает количество round-trips при пагинации.
        """
        conditions = self._build_filter_conditions(title, author, genre, year, available)
        query = (
            select(Book, func.count().over().label("total_count"))
            .where(*conditions)
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(query)
        rows = result.all()
        if not rows:
            return [], 0
        books = [row[0] for row in rows]
        total = rows[0][1]
        return books, total

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
        conditions = self._build_filter_conditions(title, author, genre, year, available)
        query = select(func.count()).select_from(Book).where(*conditions)
        result = await self.session.execute(query)
        return result.scalar_one()