"""Роутеры для источников"""

from typing import List

from fastapi import APIRouter, status

from src.core.schemas import StandardResponse
from src.domains.sources.dependencies import SourceServiceDep
from src.domains.sources.schemas import (
    SourceCreate,
    SourceUpdate,
    SourceResponse,
    SourceWithWeightsResponse,
    SourceOperatorWeightCreate,
    SourceOperatorWeightResponse,
)

router = APIRouter()


@router.post(
    "",
    response_model=StandardResponse[SourceResponse],
    status_code=status.HTTP_201_CREATED,
)
async def create_source(
    data: SourceCreate, service: SourceServiceDep
) -> StandardResponse[SourceResponse]:
    """Создать источник"""
    source = await service.create_source(data)
    return StandardResponse(success=True, data=source)


@router.get("", response_model=StandardResponse[List[SourceResponse]])
async def get_sources(
    service: SourceServiceDep, skip: int = 0, limit: int = 100
) -> StandardResponse[List[SourceResponse]]:
    """Получить список источников"""
    sources = await service.get_all_sources(skip=skip, limit=limit)
    return StandardResponse(success=True, data=sources)


@router.get("/{source_id}", response_model=StandardResponse[SourceResponse])
async def get_source(
    source_id: int, service: SourceServiceDep
) -> StandardResponse[SourceResponse]:
    """Получить источник по ID"""
    source = await service.get_source(source_id)
    return StandardResponse(success=True, data=source)


@router.get(
    "/{source_id}/with-weights",
    response_model=StandardResponse[SourceWithWeightsResponse],
)
async def get_source_with_weights(
    source_id: int, service: SourceServiceDep
) -> StandardResponse[SourceWithWeightsResponse]:
    """Получить источник с весами операторов"""
    source = await service.get_source_with_weights(source_id)
    return StandardResponse(success=True, data=source)


@router.patch("/{source_id}", response_model=StandardResponse[SourceResponse])
async def update_source(
    source_id: int, data: SourceUpdate, service: SourceServiceDep
) -> StandardResponse[SourceResponse]:
    """Обновить источник"""
    source = await service.update_source(source_id, data)
    return StandardResponse(success=True, data=source)


@router.delete("/{source_id}", response_model=StandardResponse[dict])
async def delete_source(
    source_id: int, service: SourceServiceDep
) -> StandardResponse[dict]:
    """Удалить источник"""
    await service.delete_source(source_id)
    return StandardResponse(success=True, data={"deleted": True})


@router.post(
    "/{source_id}/operator-weights",
    response_model=StandardResponse[SourceOperatorWeightResponse],
    status_code=status.HTTP_201_CREATED,
)
async def set_operator_weight(
    source_id: int, data: SourceOperatorWeightCreate, service: SourceServiceDep
) -> StandardResponse[SourceOperatorWeightResponse]:
    """Установить вес оператора для источника"""
    weight = await service.set_operator_weight(source_id, data)
    return StandardResponse(success=True, data=weight)


@router.delete(
    "/{source_id}/operator-weights/{operator_id}", response_model=StandardResponse[dict]
)
async def remove_operator_weight(
    source_id: int, operator_id: int, service: SourceServiceDep
) -> StandardResponse[dict]:
    """Удалить вес оператора для источника"""
    await service.remove_operator_weight(source_id, operator_id)
    return StandardResponse(success=True, data={"deleted": True})
