"""Тесты для эндпоинтов лидов"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.domains.leads.model import Lead
from src.domains.contacts.model import Contact
from src.domains.sources.model import Source


@pytest.mark.asyncio
async def test_get_leads_empty(client: AsyncClient):
    """Тест получения списка лидов (пустой список)"""
    response = await client.get("/api/v1/leads")
    assert response.status_code == 200
    result = response.json()
    assert result["success"] is True
    assert result["data"] == []


@pytest.mark.asyncio
async def test_get_leads(client: AsyncClient, test_lead: Lead):
    """Тест получения списка лидов"""
    response = await client.get("/api/v1/leads")
    assert response.status_code == 200
    result = response.json()
    assert result["success"] is True
    assert len(result["data"]) == 1
    assert result["data"][0]["id"] == test_lead.id
    assert result["data"][0]["phone"] == test_lead.phone


@pytest.mark.asyncio
async def test_get_leads_with_pagination(client: AsyncClient, db_session: AsyncSession):
    """Тест пагинации списка лидов"""
    # Создаем несколько лидов
    for i in range(5):
        lead = Lead(
            external_id=f"ext_{i}",
            phone=f"+7999123456{i}",
            email=f"test{i}@example.com",
            name=f"Лид {i}",
        )
        db_session.add(lead)
    await db_session.commit()

    # Тест с limit
    response = await client.get("/api/v1/leads?limit=2")
    assert response.status_code == 200
    result = response.json()
    assert len(result["data"]) == 2

    # Тест с skip
    response = await client.get("/api/v1/leads?skip=2&limit=2")
    assert response.status_code == 200
    result = response.json()
    assert len(result["data"]) == 2


@pytest.mark.asyncio
async def test_get_lead_by_id(client: AsyncClient, test_lead: Lead):
    """Тест получения лида по ID"""
    response = await client.get(f"/api/v1/leads/{test_lead.id}")
    assert response.status_code == 200
    result = response.json()
    assert result["success"] is True
    assert result["data"]["id"] == test_lead.id
    assert result["data"]["phone"] == test_lead.phone
    assert result["data"]["email"] == test_lead.email
    assert result["data"]["name"] == test_lead.name


@pytest.mark.asyncio
async def test_get_lead_not_found(client: AsyncClient):
    """Тест получения несуществующего лида"""
    response = await client.get("/api/v1/leads/99999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_lead_with_contacts(
    client: AsyncClient,
    test_lead: Lead,
    test_source: Source,
    db_session: AsyncSession,
):
    """Тест получения лида с обращениями"""
    # Создаем обращение для лида
    contact = Contact(
        lead_id=test_lead.id,
        source_id=test_source.id,
        message="Тестовое обращение",
    )
    db_session.add(contact)
    await db_session.flush()
    await db_session.commit()

    response = await client.get(f"/api/v1/leads/{test_lead.id}/with-contacts")
    assert response.status_code == 200
    result = response.json()
    assert result["success"] is True
    assert result["data"]["id"] == test_lead.id
    assert len(result["data"]["contacts"]) == 1
    assert result["data"]["contacts"][0]["message"] == "Тестовое обращение"


@pytest.mark.asyncio
async def test_get_lead_with_contacts_empty(client: AsyncClient, test_lead: Lead):
    """Тест получения лида без обращений"""
    response = await client.get(f"/api/v1/leads/{test_lead.id}/with-contacts")
    assert response.status_code == 200
    result = response.json()
    assert result["success"] is True
    assert result["data"]["id"] == test_lead.id
    assert result["data"]["contacts"] == []


@pytest.mark.asyncio
async def test_update_lead(client: AsyncClient, test_lead: Lead):
    """Тест обновления лида"""
    data = {
        "phone": "+79997654321",
        "email": "updated@example.com",
        "name": "Обновленное имя",
        "external_id": "updated_ext",
    }
    response = await client.patch(f"/api/v1/leads/{test_lead.id}", json=data)
    assert response.status_code == 200
    result = response.json()
    assert result["success"] is True
    assert result["data"]["phone"] == data["phone"]
    assert result["data"]["email"] == data["email"]
    assert result["data"]["name"] == data["name"]
    assert result["data"]["external_id"] == data["external_id"]


@pytest.mark.asyncio
async def test_update_lead_partial(client: AsyncClient, test_lead: Lead):
    """Тест частичного обновления лида"""
    data = {"name": "Только имя"}
    response = await client.patch(f"/api/v1/leads/{test_lead.id}", json=data)
    assert response.status_code == 200
    result = response.json()
    assert result["success"] is True
    assert result["data"]["name"] == data["name"]
    # Остальные поля не должны измениться
    assert result["data"]["phone"] == test_lead.phone


@pytest.mark.asyncio
async def test_update_lead_not_found(client: AsyncClient):
    """Тест обновления несуществующего лида"""
    data = {"name": "Новое имя"}
    response = await client.patch("/api/v1/leads/99999", json=data)
    assert response.status_code == 404
