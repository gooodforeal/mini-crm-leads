"""Роутеры для операторов"""

from typing import List

from fastapi import APIRouter, status

from src.core.schemas import StandardResponse
from src.domains.operators.dependencies import OperatorServiceDep
from src.domains.operators.schemas import (
    OperatorCreate,
    OperatorUpdate,
    OperatorResponse,
)

router = APIRouter()


@router.post(
    "",
    response_model=StandardResponse[OperatorResponse],
    status_code=status.HTTP_201_CREATED,
)
async def create_operator(
    data: OperatorCreate, service: OperatorServiceDep
) -> StandardResponse[OperatorResponse]:
    """Создать оператора"""
    operator = await service.create_operator(data)
    return StandardResponse(success=True, data=operator)


@router.get("", response_model=StandardResponse[List[OperatorResponse]])
async def get_operators(
    service: OperatorServiceDep, skip: int = 0, limit: int = 100
) -> StandardResponse[List[OperatorResponse]]:
    """Получить список операторов"""
    operators = await service.get_all_operators(skip=skip, limit=limit)
    return StandardResponse(success=True, data=operators)


@router.get("/{operator_id}", response_model=StandardResponse[OperatorResponse])
async def get_operator(
    operator_id: int, service: OperatorServiceDep
) -> StandardResponse[OperatorResponse]:
    """Получить оператора по ID"""
    operator = await service.get_operator(operator_id)
    return StandardResponse(success=True, data=operator)


@router.patch("/{operator_id}", response_model=StandardResponse[OperatorResponse])
async def update_operator(
    operator_id: int, data: OperatorUpdate, service: OperatorServiceDep
) -> StandardResponse[OperatorResponse]:
    """Обновить оператора"""
    operator = await service.update_operator(operator_id, data)
    return StandardResponse(success=True, data=operator)


@router.delete("/{operator_id}", response_model=StandardResponse[dict])
async def delete_operator(
    operator_id: int, service: OperatorServiceDep
) -> StandardResponse[dict]:
    """Удалить оператора"""
    await service.delete_operator(operator_id)
    return StandardResponse(success=True, data={"deleted": True})
