"""
Порт для обогащения данных книги из внешних источников.
"""

from abc import ABC, abstractmethod


class BookEnrichmentPort(ABC):
    """Абстракция для получения дополнительных данных о книге."""

    @abstractmethod
    async def enrich(
        self,
        title: str,
        author: str,
        isbn: str | None = None,
    ) -> dict | None:
        """
        Обогатить данные книги из внешнего источника.

        Returns:
            dict с дополнительными данными или None если данные недоступны.
        """
        pass
