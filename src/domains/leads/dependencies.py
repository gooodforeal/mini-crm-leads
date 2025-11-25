"""Зависимости для лидов"""

from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.domains.leads.repository import LeadRepository
from src.domains.leads.service import LeadService


def get_lead_repository(session: AsyncSession = Depends(get_db)) -> LeadRepository:
    """Получить репозиторий лидов"""
    return LeadRepository(session)


def get_lead_service(
    repository: LeadRepository = Depends(get_lead_repository),
) -> LeadService:
    """Получить сервис лидов"""
    return LeadService(repository)


LeadServiceDep = Annotated[LeadService, Depends(get_lead_service)]
