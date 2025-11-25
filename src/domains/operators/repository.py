"""Репозиторий для работы с операторами"""

from typing import List, Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.base_repository import BaseRepository
from src.domains.operators.model import Operator
from src.domains.contacts.model import Contact


class OperatorRepository(BaseRepository[Operator]):
    """Репозиторий операторов"""

    def __init__(self, session: AsyncSession):
        super().__init__(session, Operator)

    async def get_by_name(self, name: str) -> Optional[Operator]:
        """Получить оператора по имени"""
        result = await self.session.execute(
            select(Operator).where(Operator.name == name)
        )
        return result.scalar_one_or_none()

    async def get_active_operators(self) -> List[Operator]:
        """Получить всех активных операторов"""
        result = await self.session.execute(select(Operator).where(Operator.is_active))
        return list(result.scalars().all())

    async def get_current_load(self, operator_id: int) -> int:
        """Получить текущую нагрузку оператора (количество активных обращений)"""
        result = await self.session.execute(
            select(func.count(Contact.id))
            .where(Contact.operator_id == operator_id)
            .where(Contact.is_active)
        )
        return result.scalar_one() or 0

    async def get_available_operators(self, source_id: int) -> List[Operator]:
        """Получить доступных операторов для источника (активные и не превышающие лимит)"""
        from src.domains.sources.model import SourceOperatorWeight

        # Получаем операторов, назначенных на источник, с подсчетом их текущей нагрузки одним запросом
        # Используем подзапрос для подсчета активных обращений каждого оператора
        load_subquery = (
            select(Contact.operator_id, func.count(Contact.id).label("current_load"))
            .where(Contact.is_active)
            .where(Contact.operator_id.isnot(None))
            .group_by(Contact.operator_id)
        ).subquery()

        # Фильтруем прямо в SQL по лимиту нагрузки
        result = await self.session.execute(
            select(Operator)
            .join(SourceOperatorWeight, Operator.id == SourceOperatorWeight.operator_id)
            .outerjoin(load_subquery, Operator.id == load_subquery.c.operator_id)
            .where(SourceOperatorWeight.source_id == source_id)
            .where(Operator.is_active)
            .where(func.coalesce(load_subquery.c.current_load, 0) < Operator.load_limit)
        )

        return list(result.scalars().all())
