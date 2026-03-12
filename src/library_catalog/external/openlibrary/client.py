"""
Клиент для Open Library API.
"""

import httpx

from src.library_catalog.external.base.base_client import BaseApiClient
from src.library_catalog.domain.exceptions import (
    OpenLibraryException,
    OpenLibraryTimeoutException,
)
from src.library_catalog.domain.ports.book_enrichment_port import BookEnrichmentPort


class OpenLibraryClient(BaseApiClient, BookEnrichmentPort):
    """Клиент для Open Library API."""

    def __init__(
        self,
        base_url: str = "https://openlibrary.org",
        timeout: float = 10.0,
    ):
        super().__init__(base_url, timeout=timeout)

    def client_name(self) -> str:
        return "openlibrary"

    async def search_by_isbn(self, isbn: str) -> dict:
        """Поиск книги по ISBN."""
        try:
            data = await self._get(
                "/search.json",
                params={"isbn": isbn, "limit": 1}
            )
            docs = data.get("docs", [])
            if not docs:
                return {}
            return self._extract_book_data(docs[0])
        except httpx.TimeoutException:
            raise OpenLibraryTimeoutException(self.timeout)
        except httpx.HTTPError as e:
            raise OpenLibraryException(str(e))

    async def search_by_title_author(self, title: str, author: str) -> dict:
        """Поиск по названию и автору."""
        try:
            data = await self._get(
                "/search.json",
                params={"title": title, "author": author, "limit": 1}
            )
            docs = data.get("docs", [])
            if not docs:
                return {}
            return self._extract_book_data(docs[0])
        except httpx.TimeoutException:
            raise OpenLibraryTimeoutException(self.timeout)
        except httpx.HTTPError as e:
            raise OpenLibraryException(str(e))

    async def enrich(
        self,
        title: str,
        author: str,
        isbn: str | None = None,
    ) -> dict:
        """Обогатить данные книги."""
        if isbn:
            data = await self.search_by_isbn(isbn)
            if data:
                return data
        return await self.search_by_title_author(title, author)

    def _extract_book_data(self, doc: dict) -> dict:
        """Извлечь нужные поля из ответа Open Library."""
        result = {}

        if cover_id := doc.get("cover_i"):
            result["cover_url"] = (
                f"https://covers.openlibrary.org/b/id/{cover_id}-L.jpg"
            )
        if subjects := doc.get("subject"):
            result["subjects"] = subjects[:10]
        if publisher := doc.get("publisher"):
            result["publisher"] = publisher[0] if publisher else None
        if language := doc.get("language"):
            result["language"] = language[0] if language else None
        if ratings := doc.get("ratings_average"):
            result["rating"] = ratings

        return result