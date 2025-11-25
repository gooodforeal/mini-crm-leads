"""Репозиторий для работы с обращениями"""

from typing import List, Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.core.base_repository import BaseRepository
from src.domains.contacts.model import Contact


class ContactRepository(BaseRepository[Contact]):
    """Репозиторий обращений"""

    def __init__(self, session: AsyncSession):
        super().__init__(session, Contact)

    async def get_by_id_with_relations(self, id: int) -> Optional[Contact]:
        """Получить обращение по ID с загрузкой связанных объектов"""
        result = await self.session.execute(
            select(Contact)
            .options(
                selectinload(Contact.lead),
                selectinload(Contact.source),
                selectinload(Contact.operator),
            )
            .where(Contact.id == id)
        )
        return result.scalar_one_or_none()

    async def get_by_lead(self, lead_id: int) -> List[Contact]:
        """Получить все обращения лида с загрузкой связанных объектов"""
        result = await self.session.execute(
            select(Contact)
            .options(
                selectinload(Contact.lead),
                selectinload(Contact.source),
                selectinload(Contact.operator),
            )
            .where(Contact.lead_id == lead_id)
        )
        return list(result.scalars().all())

    async def get_by_source(self, source_id: int) -> List[Contact]:
        """Получить все обращения по источнику"""
        result = await self.session.execute(
            select(Contact).where(Contact.source_id == source_id)
        )
        return list(result.scalars().all())

    async def get_by_operator(self, operator_id: int) -> List[Contact]:
        """Получить все обращения оператора"""
        result = await self.session.execute(
            select(Contact).where(Contact.operator_id == operator_id)
        )
        return list(result.scalars().all())

    async def get_active_by_operator(self, operator_id: int) -> List[Contact]:
        """Получить активные обращения оператора"""
        result = await self.session.execute(
            select(Contact)
            .where(Contact.operator_id == operator_id)
            .where(Contact.is_active)
        )
        return list(result.scalars().all())

    async def get_statistics(self) -> dict:
        """Получить статистику распределения обращений"""
        # Статистика по источникам и операторам
        result = await self.session.execute(
            select(
                Contact.source_id,
                Contact.operator_id,
                func.count(Contact.id).label("count"),
            ).group_by(Contact.source_id, Contact.operator_id)
        )

        stats = {}
        for row in result.all():
            source_id = row.source_id
            operator_id = row.operator_id
            count = row.count

            if source_id not in stats:
                stats[source_id] = {}
            stats[source_id][operator_id] = count

        return stats
