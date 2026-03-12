"""
Базовый репозиторий с Generic CRUD операциями.
"""

from typing import Any, Generic, TypeVar, Type
from uuid import UUID

from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar("T")


class BaseRepository(Generic[T]):
    """Generic базовый класс для CRUD операций."""

    def __init__(self, session: AsyncSession, model: Type[T]):
        self.session = session
        self.model = model

    async def create(self, data: BaseModel | None = None, **kwargs: Any) -> T:
        """Создать запись.

        Принимает Pydantic-схему (предпочтительно) или kwargs:
            await repo.create(BookCreate(...))
            await repo.create(title="...", author="...")  # устаревший вызов
        """
        fields = data.model_dump(exclude_unset=True) if data is not None else kwargs
        instance = self.model(**fields)
        self.session.add(instance)
        await self.session.flush()
        await self.session.refresh(instance)
        return instance

    async def get_by_id(self, id: UUID) -> T | None:
        """Получить по ID."""
        return await self.session.get(self.model, id)

    async def update(self, id: UUID, data: BaseModel | None = None, **kwargs: Any) -> T | None:
        """Обновить запись.

        Принимает Pydantic-схему (предпочтительно) или kwargs:
            await repo.update(id, BookUpdate(...))
            await repo.update(id, title="...")  # устаревший вызов
        """
        instance = await self.get_by_id(id)
        if instance is None:
            return None
        fields = data.model_dump(exclude_unset=True) if data is not None else kwargs
        for key, value in fields.items():
            setattr(instance, key, value)
        await self.session.commit()
        await self.session.refresh(instance)
        return instance

    async def delete(self, id: UUID) -> bool:
        """Удалить запись."""
        instance = await self.get_by_id(id)
        if instance is None:
            return False
        await self.session.delete(instance)
        await self.session.commit()
        return True

    async def get_all(self, limit: int = 100, offset: int = 0) -> list[T]:
        """Получить все записи с пагинацией."""
        result = await self.session.execute(
            select(self.model).limit(limit).offset(offset)
        )
        return list(result.scalars().all())