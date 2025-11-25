"""Тесты для базовых эндпоинтов"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_root_endpoint(client: AsyncClient):
    """Тест корневого эндпоинта"""
    response = await client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "message" in data["data"]
    assert data["data"]["message"] == "Mini CRM Leads API"


@pytest.mark.asyncio
async def test_health_endpoint(client: AsyncClient):
    """Тест эндпоинта проверки здоровья"""
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["status"] == "healthy"
