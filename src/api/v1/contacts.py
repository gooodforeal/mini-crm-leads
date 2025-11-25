"""Роутеры для обращений"""

from typing import List

from fastapi import APIRouter, status

from src.core.schemas import StandardResponse
from src.domains.contacts.dependencies import ContactServiceDep
from src.domains.contacts.schemas import (
    ContactCreate,
    ContactUpdate,
    ContactResponse,
    ContactDetailResponse,
)

router = APIRouter()


@router.post(
    "",
    response_model=StandardResponse[ContactDetailResponse],
    status_code=status.HTTP_201_CREATED,
)
async def create_contact(
    data: ContactCreate, service: ContactServiceDep
) -> StandardResponse[ContactDetailResponse]:
    """Создать обращение (автоматически распределяется оператор)"""
    contact = await service.create_contact(data)
    return StandardResponse(success=True, data=contact)


@router.get("", response_model=StandardResponse[List[ContactResponse]])
async def get_contacts(
    service: ContactServiceDep, skip: int = 0, limit: int = 100
) -> StandardResponse[List[ContactResponse]]:
    """Получить список обращений"""
    contacts = await service.get_all_contacts(skip=skip, limit=limit)
    return StandardResponse(success=True, data=contacts)


@router.get("/{contact_id}", response_model=StandardResponse[ContactDetailResponse])
async def get_contact(
    contact_id: int, service: ContactServiceDep
) -> StandardResponse[ContactDetailResponse]:
    """Получить обращение по ID"""
    contact = await service.get_contact(contact_id)
    return StandardResponse(success=True, data=contact)


@router.patch("/{contact_id}", response_model=StandardResponse[ContactResponse])
async def update_contact(
    contact_id: int, data: ContactUpdate, service: ContactServiceDep
) -> StandardResponse[ContactResponse]:
    """Обновить обращение"""
    contact = await service.update_contact(contact_id, data)
    return StandardResponse(success=True, data=contact)


@router.get("/statistics/distribution", response_model=StandardResponse[dict])
async def get_distribution_statistics(
    service: ContactServiceDep,
) -> StandardResponse[dict]:
    """Получить статистику распределения обращений по источникам и операторам"""
    stats = await service.get_statistics()
    return StandardResponse(success=True, data=stats)
