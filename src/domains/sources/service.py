"""Сервис для бизнес-логики источников"""

from typing import List

from src.core.exceptions import NotFoundError
from src.domains.sources.repository import (
    SourceRepository,
    SourceOperatorWeightRepository,
)
from src.domains.sources.schemas import (
    SourceCreate,
    SourceUpdate,
    SourceResponse,
    SourceOperatorWeightCreate,
    SourceOperatorWeightResponse,
    SourceWithWeightsResponse,
)
from src.domains.operators.repository import OperatorRepository
from src.utils.logger import logger


class SourceService:
    """Сервис источников"""

    def __init__(
        self,
        repository: SourceRepository,
        weight_repository: SourceOperatorWeightRepository,
        operator_repository: OperatorRepository,
    ):
        self.repository = repository
        self.weight_repository = weight_repository
        self.operator_repository = operator_repository

    async def create_source(self, data: SourceCreate) -> SourceResponse:
        """Создать источник"""
        source = await self.repository.create(**data.model_dump())
        return SourceResponse.model_validate(source)

    async def get_source(self, source_id: int) -> SourceResponse:
        """Получить источник по ID"""
        source = await self.repository.get_by_id(source_id)
        if not source:
            logger.warning(f"Source not found: source_id={source_id}")
            raise NotFoundError("Source")
        return SourceResponse.model_validate(source)

    async def get_source_with_weights(
        self, source_id: int
    ) -> SourceWithWeightsResponse:
        """Получить источник с весами операторов"""
        source = await self.repository.get_with_weights(source_id)
        if not source:
            logger.warning(f"Source not found: source_id={source_id}")
            raise NotFoundError("Source")

        # Веса уже загружены через eager loading в get_with_weights
        return SourceWithWeightsResponse(
            **SourceResponse.model_validate(source).model_dump(),
            operator_weights=[
                SourceOperatorWeightResponse.model_validate(w)
                for w in source.operator_weights
            ],
        )

    async def get_all_sources(
        self, skip: int = 0, limit: int = 100
    ) -> List[SourceResponse]:
        """Получить все источники"""
        sources = await self.repository.get_all(skip=skip, limit=limit)
        return [SourceResponse.model_validate(s) for s in sources]

    async def update_source(self, source_id: int, data: SourceUpdate) -> SourceResponse:
        """Обновить источник"""
        source = await self.repository.get_by_id(source_id)
        if not source:
            logger.warning(f"Source not found for update: source_id={source_id}")
            raise NotFoundError("Source")

        update_data = data.model_dump(exclude_unset=True)
        updated_source = await self.repository.update(source_id, **update_data)
        return SourceResponse.model_validate(updated_source)

    async def delete_source(self, source_id: int) -> bool:
        """Удалить источник"""
        source = await self.repository.get_by_id(source_id)
        if not source:
            logger.warning(f"Source not found for delete: source_id={source_id}")
            raise NotFoundError("Source")
        return await self.repository.delete(source_id)

    async def set_operator_weight(
        self, source_id: int, data: SourceOperatorWeightCreate
    ) -> SourceOperatorWeightResponse:
        """Установить вес оператора для источника"""
        # Проверяем существование источника и оператора
        source = await self.repository.get_by_id(source_id)
        if not source:
            logger.warning(f"Source not found: source_id={source_id}")
            raise NotFoundError("Source")

        operator = await self.operator_repository.get_by_id(data.operator_id)
        if not operator:
            logger.warning(f"Operator not found: operator_id={data.operator_id}")
            raise NotFoundError("Operator")

        # Проверяем, существует ли уже такая связь
        existing = await self.weight_repository.get_by_source_and_operator(
            source_id, data.operator_id
        )

        if existing:
            # Обновляем существующий вес
            updated = await self.weight_repository.update(
                existing.id, weight=data.weight
            )
            return SourceOperatorWeightResponse.model_validate(updated)
        else:
            # Создаем новую связь
            weight = await self.weight_repository.create(
                source_id=source_id, operator_id=data.operator_id, weight=data.weight
            )
            return SourceOperatorWeightResponse.model_validate(weight)

    async def remove_operator_weight(self, source_id: int, operator_id: int) -> bool:
        """Удалить вес оператора для источника"""
        weight = await self.weight_repository.get_by_source_and_operator(
            source_id, operator_id
        )
        if not weight:
            logger.warning(
                f"SourceOperatorWeight not found: source_id={source_id}, operator_id={operator_id}"
            )
            raise NotFoundError("SourceOperatorWeight")
        return await self.weight_repository.delete(weight.id)
