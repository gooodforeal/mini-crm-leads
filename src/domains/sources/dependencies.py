"""Зависимости для источников"""

from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.domains.sources.repository import (
    SourceRepository,
    SourceOperatorWeightRepository,
)
from src.domains.operators.repository import OperatorRepository
from src.domains.sources.service import SourceService


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


def get_source_service(
    repository: SourceRepository = Depends(get_source_repository),
    weight_repository: SourceOperatorWeightRepository = Depends(
        get_source_operator_weight_repository
    ),
    operator_repository: OperatorRepository = Depends(get_operator_repository),
) -> SourceService:
    """Получить сервис источников"""
    return SourceService(
        repository=repository,
        weight_repository=weight_repository,
        operator_repository=operator_repository,
    )


SourceServiceDep = Annotated[SourceService, Depends(get_source_service)]
