"""Репозиторий для работы с источниками"""

from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.core.base_repository import BaseRepository
from src.domains.sources.model import Source, SourceOperatorWeight


class SourceRepository(BaseRepository[Source]):
    """Репозиторий источников"""

    def __init__(self, session: AsyncSession):
        super().__init__(session, Source)

    async def get_by_name(self, name: str) -> Optional[Source]:
        """Получить источник по имени"""
        result = await self.session.execute(select(Source).where(Source.name == name))
        return result.scalar_one_or_none()

    async def get_with_weights(self, source_id: int) -> Optional[Source]:
        """Получить источник с весами операторов"""
        result = await self.session.execute(
            select(Source)
            .options(
                selectinload(Source.operator_weights).selectinload(
                    SourceOperatorWeight.operator
                )
            )
            .where(Source.id == source_id)
        )
        return result.scalar_one_or_none()


class SourceOperatorWeightRepository(BaseRepository[SourceOperatorWeight]):
    """Репозиторий весов операторов для источников"""

    def __init__(self, session: AsyncSession):
        super().__init__(session, SourceOperatorWeight)

    async def get_by_source_and_operator(
        self, source_id: int, operator_id: int
    ) -> Optional[SourceOperatorWeight]:
        """Получить вес по источнику и оператору"""
        result = await self.session.execute(
            select(SourceOperatorWeight)
            .where(SourceOperatorWeight.source_id == source_id)
            .where(SourceOperatorWeight.operator_id == operator_id)
        )
        return result.scalar_one_or_none()

    async def get_by_source(self, source_id: int) -> List[SourceOperatorWeight]:
        """Получить все веса для источника"""
        result = await self.session.execute(
            select(SourceOperatorWeight).where(
                SourceOperatorWeight.source_id == source_id
            )
        )
        return list(result.scalars().all())

    async def get_by_operator(self, operator_id: int) -> List[SourceOperatorWeight]:
        """Получить все веса для оператора"""
        result = await self.session.execute(
            select(SourceOperatorWeight).where(
                SourceOperatorWeight.operator_id == operator_id
            )
        )
        return list(result.scalars().all())
