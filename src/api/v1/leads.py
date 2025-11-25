"""Роутеры для лидов"""

from typing import List

from fastapi import APIRouter

from src.core.schemas import StandardResponse
from src.domains.leads.dependencies import LeadServiceDep
from src.domains.leads.schemas import LeadUpdate, LeadResponse, LeadWithContactsResponse

router = APIRouter()


@router.get("", response_model=StandardResponse[List[LeadResponse]])
async def get_leads(
    service: LeadServiceDep, skip: int = 0, limit: int = 100
) -> StandardResponse[List[LeadResponse]]:
    """Получить список лидов"""
    leads = await service.get_all_leads(skip=skip, limit=limit)
    return StandardResponse(success=True, data=leads)


@router.get("/{lead_id}", response_model=StandardResponse[LeadResponse])
async def get_lead(
    lead_id: int, service: LeadServiceDep
) -> StandardResponse[LeadResponse]:
    """Получить лида по ID"""
    lead = await service.get_lead(lead_id)
    return StandardResponse(success=True, data=lead)


@router.get(
    "/{lead_id}/with-contacts",
    response_model=StandardResponse[LeadWithContactsResponse],
)
async def get_lead_with_contacts(
    lead_id: int, service: LeadServiceDep
) -> StandardResponse[LeadWithContactsResponse]:
    """Получить лида с обращениями"""
    lead = await service.get_lead_with_contacts(lead_id)
    return StandardResponse(success=True, data=lead)


@router.patch("/{lead_id}", response_model=StandardResponse[LeadResponse])
async def update_lead(
    lead_id: int, data: LeadUpdate, service: LeadServiceDep
) -> StandardResponse[LeadResponse]:
    """Обновить лида"""
    lead = await service.update_lead(lead_id, data)
    return StandardResponse(success=True, data=lead)
