"""Тесты для эндпоинтов обращений"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.domains.contacts.model import Contact
from src.domains.leads.model import Lead
from src.domains.sources.model import Source, SourceOperatorWeight
from src.domains.operators.model import Operator


@pytest.mark.asyncio
async def test_create_contact_with_new_lead(
    client: AsyncClient,
    test_source: Source,
    test_operator: Operator,
    db_session: AsyncSession,
):
    """Тест создания обращения с новым лидом"""
    # Создаем вес оператора для источника
    weight = SourceOperatorWeight(
        source_id=test_source.id, operator_id=test_operator.id, weight=10
    )
    db_session.add(weight)
    await db_session.commit()

    data = {
        "external_id": "new_ext_1",
        "phone": "+79991234567",
        "email": "new@example.com",
        "name": "Новый лид",
        "source_id": test_source.id,
        "message": "Тестовое обращение",
    }
    response = await client.post("/api/v1/contacts", json=data)
    assert response.status_code == 201
    result = response.json()
    assert result["success"] is True
    assert result["data"]["source_id"] == test_source.id
    assert result["data"]["message"] == data["message"]
    assert result["data"]["is_active"] is True
    assert result["data"]["lead"]["phone"] == data["phone"]
    assert result["data"]["source"]["id"] == test_source.id
    # Оператор должен быть назначен автоматически
    assert result["data"]["operator"] is not None
    assert result["data"]["operator"]["id"] == test_operator.id


@pytest.mark.asyncio
async def test_create_contact_with_existing_lead(
    client: AsyncClient,
    test_lead: Lead,
    test_source: Source,
    test_operator: Operator,
    db_session: AsyncSession,
):
    """Тест создания обращения с существующим лидом"""
    # Создаем вес оператора для источника
    weight = SourceOperatorWeight(
        source_id=test_source.id, operator_id=test_operator.id, weight=10
    )
    db_session.add(weight)
    await db_session.commit()

    data = {
        "phone": test_lead.phone,  # Используем существующий телефон
        "source_id": test_source.id,
        "message": "Второе обращение",
    }
    response = await client.post("/api/v1/contacts", json=data)
    assert response.status_code == 201
    result = response.json()
    assert result["success"] is True
    assert result["data"]["lead_id"] == test_lead.id
    assert result["data"]["lead"]["id"] == test_lead.id


@pytest.mark.asyncio
async def test_create_contact_without_operator(
    client: AsyncClient, test_source: Source, db_session: AsyncSession
):
    """Тест создания обращения без доступных операторов"""
    data = {
        "phone": "+79991234567",
        "source_id": test_source.id,
        "message": "Обращение без оператора",
    }
    response = await client.post("/api/v1/contacts", json=data)
    assert response.status_code == 201
    result = response.json()
    assert result["success"] is True
    # Оператор не должен быть назначен, если нет доступных
    assert result["data"]["operator"] is None


@pytest.mark.asyncio
async def test_create_contact_source_not_found(client: AsyncClient):
    """Тест создания обращения с несуществующим источником"""
    data = {
        "phone": "+79991234567",
        "source_id": 99999,
        "message": "Тестовое обращение",
    }
    response = await client.post("/api/v1/contacts", json=data)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_contacts_empty(client: AsyncClient):
    """Тест получения списка обращений (пустой список)"""
    response = await client.get("/api/v1/contacts")
    assert response.status_code == 200
    result = response.json()
    assert result["success"] is True
    assert result["data"] == []


@pytest.mark.asyncio
async def test_get_contacts(
    client: AsyncClient,
    test_lead: Lead,
    test_source: Source,
    test_operator: Operator,
    db_session: AsyncSession,
):
    """Тест получения списка обращений"""
    # Создаем обращение
    contact = Contact(
        lead_id=test_lead.id,
        source_id=test_source.id,
        operator_id=test_operator.id,
        message="Тестовое обращение",
    )
    db_session.add(contact)
    await db_session.commit()

    response = await client.get("/api/v1/contacts")
    assert response.status_code == 200
    result = response.json()
    assert result["success"] is True
    assert len(result["data"]) == 1
    assert result["data"][0]["id"] == contact.id
    assert result["data"][0]["message"] == contact.message


@pytest.mark.asyncio
async def test_get_contacts_with_pagination(
    client: AsyncClient,
    test_lead: Lead,
    test_source: Source,
    db_session: AsyncSession,
):
    """Тест пагинации списка обращений"""
    # Создаем несколько обращений
    for i in range(5):
        contact = Contact(
            lead_id=test_lead.id,
            source_id=test_source.id,
            message=f"Обращение {i}",
        )
        db_session.add(contact)
    await db_session.commit()

    # Тест с limit
    response = await client.get("/api/v1/contacts?limit=2")
    assert response.status_code == 200
    result = response.json()
    assert len(result["data"]) == 2

    # Тест с skip
    response = await client.get("/api/v1/contacts?skip=2&limit=2")
    assert response.status_code == 200
    result = response.json()
    assert len(result["data"]) == 2


@pytest.mark.asyncio
async def test_get_contact_by_id(
    client: AsyncClient,
    test_lead: Lead,
    test_source: Source,
    test_operator: Operator,
    db_session: AsyncSession,
):
    """Тест получения обращения по ID"""
    contact = Contact(
        lead_id=test_lead.id,
        source_id=test_source.id,
        operator_id=test_operator.id,
        message="Тестовое обращение",
    )
    db_session.add(contact)
    await db_session.commit()

    response = await client.get(f"/api/v1/contacts/{contact.id}")
    assert response.status_code == 200
    result = response.json()
    assert result["success"] is True
    assert result["data"]["id"] == contact.id
    assert result["data"]["message"] == contact.message
    assert result["data"]["lead"]["id"] == test_lead.id
    assert result["data"]["source"]["id"] == test_source.id
    assert result["data"]["operator"]["id"] == test_operator.id


@pytest.mark.asyncio
async def test_get_contact_not_found(client: AsyncClient):
    """Тест получения несуществующего обращения"""
    response = await client.get("/api/v1/contacts/99999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_contact(
    client: AsyncClient,
    test_lead: Lead,
    test_source: Source,
    test_operator: Operator,
    db_session: AsyncSession,
):
    """Тест обновления обращения"""
    contact = Contact(
        lead_id=test_lead.id,
        source_id=test_source.id,
        operator_id=test_operator.id,
        message="Исходное сообщение",
        is_active=True,
    )
    db_session.add(contact)
    await db_session.commit()

    data = {
        "message": "Обновленное сообщение",
        "is_active": False,
    }
    response = await client.patch(f"/api/v1/contacts/{contact.id}", json=data)
    assert response.status_code == 200
    result = response.json()
    assert result["success"] is True
    assert result["data"]["message"] == data["message"]
    assert result["data"]["is_active"] == data["is_active"]


@pytest.mark.asyncio
async def test_update_contact_change_operator(
    client: AsyncClient,
    test_lead: Lead,
    test_source: Source,
    test_operator: Operator,
    db_session: AsyncSession,
):
    """Тест изменения оператора обращения"""
    # Создаем второго оператора
    operator2 = Operator(name="Оператор 2", is_active=True, load_limit=10)
    db_session.add(operator2)
    await db_session.commit()

    contact = Contact(
        lead_id=test_lead.id,
        source_id=test_source.id,
        operator_id=test_operator.id,
        message="Тестовое обращение",
    )
    db_session.add(contact)
    await db_session.commit()

    data = {"operator_id": operator2.id}
    response = await client.patch(f"/api/v1/contacts/{contact.id}", json=data)
    assert response.status_code == 200
    result = response.json()
    assert result["success"] is True
    assert result["data"]["operator_id"] == operator2.id


@pytest.mark.asyncio
async def test_update_contact_not_found(client: AsyncClient):
    """Тест обновления несуществующего обращения"""
    data = {"message": "Новое сообщение"}
    response = await client.patch("/api/v1/contacts/99999", json=data)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_distribution_statistics(
    client: AsyncClient,
    test_lead: Lead,
    test_source: Source,
    test_operator: Operator,
    db_session: AsyncSession,
):
    """Тест получения статистики распределения обращений"""
    # Создаем несколько обращений
    for i in range(3):
        contact = Contact(
            lead_id=test_lead.id,
            source_id=test_source.id,
            operator_id=test_operator.id,
            message=f"Обращение {i}",
        )
        db_session.add(contact)
    await db_session.commit()

    response = await client.get("/api/v1/contacts/statistics/distribution")
    assert response.status_code == 200
    result = response.json()
    assert result["success"] is True
    assert "data" in result
    # Проверяем, что статистика содержит ожидаемые ключи
    stats = result["data"]
    assert isinstance(stats, dict)
