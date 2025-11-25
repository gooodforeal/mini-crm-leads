"""Базовый репозиторий для работы с БД"""

from typing import Generic, TypeVar, Optional, List, Type, Any

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.base_model import BaseModel

ModelType = TypeVar("ModelType", bound=BaseModel)


class BaseRepository(Generic[ModelType]):
    """Базовый репозиторий с общими методами CRUD"""

    def __init__(self, session: AsyncSession, model: Type[ModelType]):
        self.session = session
        self.model = model

    async def get_by_id(self, id: int) -> Optional[ModelType]:
        """Получить запись по ID"""
        result = await self.session.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalar_one_or_none()

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """Получить все записи с пагинацией"""
        result = await self.session.execute(
            select(self.model).offset(skip).limit(limit)
        )
        return list(result.scalars().all())

    async def create(self, **kwargs: Any) -> ModelType:
        """Создать новую запись"""
        try:
            instance = self.model(**kwargs)
            self.session.add(instance)
            await self.session.flush()
            await self.session.commit()
            await self.session.refresh(instance)
            return instance
        except Exception:
            await self.session.rollback()
            raise

    async def update(self, id: int, **kwargs: Any) -> Optional[ModelType]:
        """Обновить запись"""
        try:
            await self.session.execute(
                update(self.model).where(self.model.id == id).values(**kwargs)
            )
            await self.session.flush()
            await self.session.commit()
            return await self.get_by_id(id)
        except Exception:
            await self.session.rollback()
            raise

    async def delete(self, id: int) -> bool:
        """Удалить запись"""
        try:
            await self.session.execute(delete(self.model).where(self.model.id == id))
            await self.session.flush()
            await self.session.commit()
            return True
        except Exception:
            await self.session.rollback()
            raise
