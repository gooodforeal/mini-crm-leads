"""Сервис для бизнес-логики лидов"""

from typing import List

from src.core.exceptions import NotFoundError
from src.domains.leads.repository import LeadRepository
from src.domains.leads.schemas import (
    LeadCreate,
    LeadUpdate,
    LeadResponse,
    LeadWithContactsResponse,
)
from src.utils.logger import logger


class LeadService:
    """Сервис лидов"""

    def __init__(self, repository: LeadRepository):
        self.repository = repository

    async def create_lead(self, data: LeadCreate) -> LeadResponse:
        """Создать лида"""
        lead = await self.repository.create(**data.model_dump())
        return LeadResponse.model_validate(lead)

    async def get_lead(self, lead_id: int) -> LeadResponse:
        """Получить лида по ID"""
        lead = await self.repository.get_by_id(lead_id)
        if not lead:
            logger.warning(f"Lead not found: lead_id={lead_id}")
            raise NotFoundError("Lead")
        return LeadResponse.model_validate(lead)

    async def get_lead_with_contacts(self, lead_id: int) -> LeadWithContactsResponse:
        """Получить лида с обращениями"""
        lead = await self.repository.get_by_id_with_contacts(lead_id)
        if not lead:
            logger.warning(f"Lead not found: lead_id={lead_id}")
            raise NotFoundError("Lead")
        return LeadWithContactsResponse.model_validate(lead)

    async def get_all_leads(
        self, skip: int = 0, limit: int = 100
    ) -> List[LeadResponse]:
        """Получить всех лидов"""
        leads = await self.repository.get_all(skip=skip, limit=limit)
        return [LeadResponse.model_validate(lead) for lead in leads]

    async def update_lead(self, lead_id: int, data: LeadUpdate) -> LeadResponse:
        """Обновить лида"""
        lead = await self.repository.get_by_id(lead_id)
        if not lead:
            logger.warning(f"Lead not found for update: lead_id={lead_id}")
            raise NotFoundError("Lead")

        update_data = data.model_dump(exclude_unset=True)
        updated_lead = await self.repository.update(lead_id, **update_data)
        return LeadResponse.model_validate(updated_lead)

    async def find_or_create_lead(self, data: LeadCreate) -> LeadResponse:
        """Найти существующего лида или создать нового"""
        lead = await self.repository.find_or_create(**data.model_dump())
        return LeadResponse.model_validate(lead)
