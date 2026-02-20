"""
Клиент для Open Library API.
"""


class OpenLibraryClient:
    """Клиент для обогащения данных книг из Open Library."""

    async def enrich(
        self,
        title: str,
        author: str,
        isbn: str | None = None,
    ) -> dict | None:
        """Обогатить данные книги из Open Library."""
        return None
