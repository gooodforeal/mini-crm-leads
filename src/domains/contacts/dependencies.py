"""Зависимости для обращений"""

from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.domains.contacts.repository import ContactRepository
from src.domains.leads.repository import LeadRepository
from src.domains.sources.repository import (
    SourceRepository,
    SourceOperatorWeightRepository,
)
from src.domains.operators.repository import OperatorRepository
from src.domains.contacts.service import ContactService


def get_contact_repository(
    session: AsyncSession = Depends(get_db),
) -> ContactRepository:
    """Получить репозиторий обращений"""
    return ContactRepository(session)


def get_lead_repository(session: AsyncSession = Depends(get_db)) -> LeadRepository:
    """Получить репозиторий лидов"""
    return LeadRepository(session)


def get_source_repository(session: AsyncSession = Depends(get_db)) -> SourceRepository:
    """Получить репозиторий источников"""
    return SourceRepository(session)


def get_source_operator_weight_repository(
    session: AsyncSession = Depends(get_db),
) -> SourceOperatorWeightRepository:
    """Получить репозиторий весов операторов"""
    return SourceOperatorWeightRepository(session)


def get_operator_repository(
    session: AsyncSession = Depends(get_db),
) -> OperatorRepository:
    """Получить репозиторий операторов"""
    return OperatorRepository(session)


def get_contact_service(
    repository: ContactRepository = Depends(get_contact_repository),
    lead_repository: LeadRepository = Depends(get_lead_repository),
    source_repository: SourceRepository = Depends(get_source_repository),
    operator_repository: OperatorRepository = Depends(get_operator_repository),
    weight_repository: SourceOperatorWeightRepository = Depends(
        get_source_operator_weight_repository
    ),
) -> ContactService:
    """Получить сервис обращений"""
    return ContactService(
        repository=repository,
        lead_repository=lead_repository,
        source_repository=source_repository,
        operator_repository=operator_repository,
        weight_repository=weight_repository,
    )


ContactServiceDep = Annotated[ContactService, Depends(get_contact_service)]
