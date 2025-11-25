"""Репозиторий для работы с лидами"""

from typing import Optional

from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.core.base_repository import BaseRepository
from src.domains.leads.model import Lead


class LeadRepository(BaseRepository[Lead]):
    """Репозиторий лидов"""

    def __init__(self, session: AsyncSession):
        super().__init__(session, Lead)

    async def find_by_identifiers(
        self,
        external_id: Optional[str] = None,
        phone: Optional[str] = None,
        email: Optional[str] = None,
    ) -> Optional[Lead]:
        """Найти лида по идентификаторам (external_id, phone, email)"""
        conditions = []

        if external_id:
            conditions.append(Lead.external_id == external_id)
        if phone:
            conditions.append(Lead.phone == phone)
        if email:
            conditions.append(Lead.email == email)

        if not conditions:
            return None

        result = await self.session.execute(select(Lead).where(or_(*conditions)))
        return result.scalar_one_or_none()

    async def find_or_create(
        self,
        external_id: Optional[str] = None,
        phone: Optional[str] = None,
        email: Optional[str] = None,
        name: Optional[str] = None,
    ) -> Lead:
        """Найти существующего лида или создать нового"""
        try:
            lead = await self.find_by_identifiers(
                external_id=external_id, phone=phone, email=email
            )

            if not lead:
                lead = await self.create(
                    external_id=external_id, phone=phone, email=email, name=name
                )

            return lead
        except Exception:
            await self.session.rollback()
            raise

    async def get_by_id_with_contacts(self, id: int) -> Optional[Lead]:
        """Получить лида по ID с загрузкой обращений и их связанных объектов"""
        from src.domains.contacts.model import Contact

        result = await self.session.execute(
            select(Lead)
            .options(
                selectinload(Lead.contacts).selectinload(Contact.source),
                selectinload(Lead.contacts).selectinload(Contact.operator),
            )
            .where(Lead.id == id)
        )
        return result.scalar_one_or_none()
