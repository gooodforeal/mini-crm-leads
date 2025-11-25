"""Сервис для бизнес-логики операторов"""

from typing import List

from src.core.exceptions import NotFoundError
from src.domains.operators.repository import OperatorRepository
from src.domains.operators.schemas import (
    OperatorCreate,
    OperatorUpdate,
    OperatorResponse,
)
from src.utils.logger import logger


class OperatorService:
    """Сервис операторов"""

    def __init__(self, repository: OperatorRepository):
        self.repository = repository

    async def create_operator(self, data: OperatorCreate) -> OperatorResponse:
        """Создать оператора"""
        operator = await self.repository.create(**data.model_dump())
        return OperatorResponse.model_validate(operator)

    async def get_operator(self, operator_id: int) -> OperatorResponse:
        """Получить оператора по ID"""
        operator = await self.repository.get_by_id(operator_id)
        if not operator:
            logger.warning(f"Operator not found: operator_id={operator_id}")
            raise NotFoundError("Operator")
        return OperatorResponse.model_validate(operator)

    async def get_all_operators(
        self, skip: int = 0, limit: int = 100
    ) -> List[OperatorResponse]:
        """Получить всех операторов"""
        operators = await self.repository.get_all(skip=skip, limit=limit)
        return [OperatorResponse.model_validate(op) for op in operators]

    async def update_operator(
        self, operator_id: int, data: OperatorUpdate
    ) -> OperatorResponse:
        """Обновить оператора"""
        operator = await self.repository.get_by_id(operator_id)
        if not operator:
            logger.warning(f"Operator not found for update: operator_id={operator_id}")
            raise NotFoundError("Operator")

        update_data = data.model_dump(exclude_unset=True)
        updated_operator = await self.repository.update(operator_id, **update_data)
        return OperatorResponse.model_validate(updated_operator)

    async def delete_operator(self, operator_id: int) -> bool:
        """Удалить оператора"""
        operator = await self.repository.get_by_id(operator_id)
        if not operator:
            logger.warning(f"Operator not found for delete: operator_id={operator_id}")
            raise NotFoundError("Operator")
        return await self.repository.delete(operator_id)
