"""Зависимости для операторов"""

from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.domains.operators.repository import OperatorRepository
from src.domains.operators.service import OperatorService


def get_operator_repository(
    session: AsyncSession = Depends(get_db),
) -> OperatorRepository:
    """Получить репозиторий операторов"""
    return OperatorRepository(session)


def get_operator_service(
    repository: OperatorRepository = Depends(get_operator_repository),
) -> OperatorService:
    """Получить сервис операторов"""
    return OperatorService(repository)


OperatorServiceDep = Annotated[OperatorService, Depends(get_operator_service)]
