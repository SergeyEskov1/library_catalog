"""
Dependency Injection контейнер для FastAPI.

Стратегия кеширования:
- get_openlibrary_client() — singleton: HTTP-клиент держит пул соединений,
  пересоздавать на каждый запрос дорого. Используется functools.cache вместо
  lru_cache для явного управления временем жизни через reset_clients().
- get_book_repository()   — per-request: репозиторий привязан к сессии БД.
- get_book_service()      — per-request: lightweight, singleton не нужен.

Тестирование:
  Для сброса кеша используйте reset_clients():

      @pytest.fixture(autouse=True)
      def clear_dependency_caches():
          reset_clients()
          yield
          reset_clients()

  Затем подменяйте через dependency_overrides:

      app.dependency_overrides[get_openlibrary_client] = lambda: MockOpenLibraryClient()
"""

from functools import cache
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.library_catalog.core.database import get_db
from src.library_catalog.core.config import settings
from src.library_catalog.data.repositories.book_repository import BookRepository
from src.library_catalog.domain.services.book_service import BookService
from src.library_catalog.external.openlibrary.client import OpenLibraryClient


# ========== EXTERNAL CLIENTS ==========

@cache
def get_openlibrary_client() -> OpenLibraryClient:
    """Singleton OpenLibraryClient (cached via functools.cache).

    Переиспользует пул TCP-соединений. Для сброса в тестах — reset_clients().
    """
    return OpenLibraryClient(
        base_url=settings.openlibrary_base_url,
        timeout=settings.openlibrary_timeout,
    )


def reset_clients() -> None:
    """Сбросить все singleton-кеши. Вызывать в тестовых фикстурах."""
    get_openlibrary_client.cache_clear()


# ========== REPOSITORIES ==========

async def get_book_repository(
    db: Annotated[AsyncSession, Depends(get_db)]
) -> BookRepository:
    """BookRepository для текущей сессии БД."""
    return BookRepository(db)


# ========== SERVICES ==========

async def get_book_service(
    book_repo: Annotated[BookRepository, Depends(get_book_repository)],
    ol_client: Annotated[OpenLibraryClient, Depends(get_openlibrary_client)],
) -> BookService:
    """BookService с внедренными зависимостями."""
    return BookService(
        book_repository=book_repo,
        openlibrary_client=ol_client,
    )


# ========== TYPE ALIASES ==========

BookServiceDep = Annotated[BookService, Depends(get_book_service)]
BookRepoDep = Annotated[BookRepository, Depends(get_book_repository)]
DbSessionDep = Annotated[AsyncSession, Depends(get_db)]