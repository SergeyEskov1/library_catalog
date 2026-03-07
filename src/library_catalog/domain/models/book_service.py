"""
Сервис для работы с книгами.
"""

import logging
from uuid import UUID

from src.library_catalog.data.repositories.book_repository import BookRepository
from src.library_catalog.domain.ports.book_enrichment_port import BookEnrichmentPort
from src.library_catalog.domain.models.book_domain import (
    BookDomain,
    CreateBookCommand,
    UpdateBookCommand,
)
from src.library_catalog.domain.exceptions import (
    BookNotFoundException,
    BookAlreadyExistsException,
    OpenLibraryException,
)

logger = logging.getLogger(__name__)


class BookService:
    """Сервис для работы с книгами. Работает только с доменными моделями."""

    def __init__(
        self,
        book_repository: BookRepository,
        openlibrary_client: BookEnrichmentPort,
    ):
        self.book_repo = book_repository
        self.ol_client = openlibrary_client

    async def create_book(self, command: CreateBookCommand) -> BookDomain:
        """Создать новую книгу."""
        if command.isbn:
            existing = await self.book_repo.find_by_isbn(command.isbn)
            if existing:
                raise BookAlreadyExistsException(command.isbn)

        extra = await self._enrich_book_data(command)

        book = await self.book_repo.create(
            title=command.title,
            author=command.author,
            year=command.year,
            genre=command.genre,
            pages=command.pages,
            isbn=command.isbn,
            description=command.description,
            extra=extra,
        )

        return book

    async def get_book(self, book_id: UUID) -> BookDomain:
        """Получить книгу по ID."""
        book = await self.book_repo.get_by_id(book_id)
        if book is None:
            raise BookNotFoundException(book_id)
        return book

    async def update_book(self, book_id: UUID, command: UpdateBookCommand) -> BookDomain:
        """Обновить книгу."""
        existing = await self.book_repo.get_by_id(book_id)
        if existing is None:
            raise BookNotFoundException(book_id)

        updated = await self.book_repo.update(
            book_id,
            **{k: v for k, v in vars(command).items() if v is not None}
        )

        return updated

    async def delete_book(self, book_id: UUID) -> None:
        """Удалить книгу."""
        deleted = await self.book_repo.delete(book_id)
        if not deleted:
            raise BookNotFoundException(book_id)

    async def search_books(
        self,
        title: str | None = None,
        author: str | None = None,
        genre: str | None = None,
        year: int | None = None,
        available: bool | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[BookDomain], int]:
        """Поиск книг с фильтрацией и пагинацией."""
        books = await self.book_repo.find_by_filters(
            title=title,
            author=author,
            genre=genre,
            year=year,
            available=available,
            limit=limit,
            offset=offset,
        )

        total = await self.book_repo.count_by_filters(
            title=title,
            author=author,
            genre=genre,
            year=year,
            available=available,
        )

        return books, total

    async def _enrich_book_data(self, command: CreateBookCommand) -> dict | None:
        try:
            extra = await self.ol_client.enrich(
                title=command.title,
                author=command.author,
                isbn=command.isbn,
            )
            return extra if extra else None
        except OpenLibraryException:
            logger.warning("Failed to enrich book data from Open Library")
            return None
