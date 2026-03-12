"""
Доменная модель книги.
"""
from src.library_catalog.api.v1.schemas.book import ShowBook
from src.library_catalog.data.models.book import Book
from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID


@dataclass
class BookDomain:
    """Доменная модель книги — не зависит от API или ORM."""

    book_id: UUID
    title: str
    author: str
    year: int
    genre: str
    pages: int
    available: bool
    isbn: str | None = None
    description: str | None = None
    extra: dict | None = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class CreateBookCommand:
    """Команда для создания книги."""

    title: str
    author: str
    year: int
    genre: str
    pages: int
    isbn: str | None = None
    description: str | None = None


@dataclass
class UpdateBookCommand:
    """Команда для обновления книги."""

    title: str | None = None
    author: str | None = None
    year: int | None = None
    genre: str | None = None
    pages: int | None = None
    available: bool | None = None
    isbn: str | None = None
    description: str | None = None

class BookMapper:
    """Преобразование ORM Book → схема ShowBook."""

    @staticmethod
    def to_show_book(book: Book) -> ShowBook:
        """Преобразовать одну книгу."""
        return ShowBook.model_validate(book)

    @staticmethod
    def to_show_books(books: list[Book]) -> list[ShowBook]:
        """Преобразовать список книг."""
        return [ShowBook.model_validate(book) for book in books]