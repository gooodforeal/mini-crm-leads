"""Базовый роутер API"""

from fastapi import APIRouter

from src.core.schemas import StandardResponse

router = APIRouter()


@router.get("/", response_model=StandardResponse[dict])
async def root() -> StandardResponse[dict]:
    """Корневой эндпоинт"""
    return StandardResponse(
        success=True, data={"message": "Mini CRM Leads API"}, message=None
    )


@router.get("/health", response_model=StandardResponse[dict])
async def health() -> StandardResponse[dict]:
    """Проверка здоровья приложения"""
    return StandardResponse(success=True, data={"status": "healthy"}, message=None)
