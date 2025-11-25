"""Тесты для эндпоинтов операторов"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.domains.operators.model import Operator


@pytest.mark.asyncio
async def test_create_operator(client: AsyncClient):
    """Тест создания оператора"""
    data = {
        "name": "Новый оператор",
        "is_active": True,
        "load_limit": 15,
    }
    response = await client.post("/api/v1/operators", json=data)
    assert response.status_code == 201
    result = response.json()
    assert result["success"] is True
    assert result["data"]["name"] == data["name"]
    assert result["data"]["is_active"] == data["is_active"]
    assert result["data"]["load_limit"] == data["load_limit"]
    assert "id" in result["data"]
    assert "created_at" in result["data"]


@pytest.mark.asyncio
async def test_create_operator_validation_error(client: AsyncClient):
    """Тест валидации при создании оператора"""
    # Пустое имя
    data = {"name": "", "is_active": True, "load_limit": 10}
    response = await client.post("/api/v1/operators", json=data)
    assert response.status_code == 422

    # Отрицательный load_limit
    data = {"name": "Оператор", "is_active": True, "load_limit": -1}
    response = await client.post("/api/v1/operators", json=data)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_operators_empty(client: AsyncClient):
    """Тест получения списка операторов (пустой список)"""
    response = await client.get("/api/v1/operators")
    assert response.status_code == 200
    result = response.json()
    assert result["success"] is True
    assert result["data"] == []


@pytest.mark.asyncio
async def test_get_operators(client: AsyncClient, test_operator: Operator):
    """Тест получения списка операторов"""
    response = await client.get("/api/v1/operators")
    assert response.status_code == 200
    result = response.json()
    assert result["success"] is True
    assert len(result["data"]) == 1
    assert result["data"][0]["id"] == test_operator.id
    assert result["data"][0]["name"] == test_operator.name


@pytest.mark.asyncio
async def test_get_operators_with_pagination(
    client: AsyncClient, db_session: AsyncSession
):
    """Тест пагинации списка операторов"""
    # Создаем несколько операторов
    for i in range(5):
        operator = Operator(name=f"Оператор {i}", is_active=True, load_limit=10)
        db_session.add(operator)
    await db_session.commit()

    # Тест с limit
    response = await client.get("/api/v1/operators?limit=2")
    assert response.status_code == 200
    result = response.json()
    assert len(result["data"]) == 2

    # Тест с skip
    response = await client.get("/api/v1/operators?skip=2&limit=2")
    assert response.status_code == 200
    result = response.json()
    assert len(result["data"]) == 2


@pytest.mark.asyncio
async def test_get_operator_by_id(client: AsyncClient, test_operator: Operator):
    """Тест получения оператора по ID"""
    response = await client.get(f"/api/v1/operators/{test_operator.id}")
    assert response.status_code == 200
    result = response.json()
    assert result["success"] is True
    assert result["data"]["id"] == test_operator.id
    assert result["data"]["name"] == test_operator.name


@pytest.mark.asyncio
async def test_get_operator_not_found(client: AsyncClient):
    """Тест получения несуществующего оператора"""
    response = await client.get("/api/v1/operators/99999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_operator(client: AsyncClient, test_operator: Operator):
    """Тест обновления оператора"""
    data = {
        "name": "Обновленное имя",
        "is_active": False,
        "load_limit": 20,
    }
    response = await client.patch(f"/api/v1/operators/{test_operator.id}", json=data)
    assert response.status_code == 200
    result = response.json()
    assert result["success"] is True
    assert result["data"]["name"] == data["name"]
    assert result["data"]["is_active"] == data["is_active"]
    assert result["data"]["load_limit"] == data["load_limit"]


@pytest.mark.asyncio
async def test_update_operator_partial(client: AsyncClient, test_operator: Operator):
    """Тест частичного обновления оператора"""
    data = {"name": "Только имя"}
    response = await client.patch(f"/api/v1/operators/{test_operator.id}", json=data)
    assert response.status_code == 200
    result = response.json()
    assert result["success"] is True
    assert result["data"]["name"] == data["name"]
    # Остальные поля не должны измениться
    assert result["data"]["is_active"] == test_operator.is_active


@pytest.mark.asyncio
async def test_update_operator_not_found(client: AsyncClient):
    """Тест обновления несуществующего оператора"""
    data = {"name": "Новое имя"}
    response = await client.patch("/api/v1/operators/99999", json=data)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_operator(client: AsyncClient, test_operator: Operator):
    """Тест удаления оператора"""
    response = await client.delete(f"/api/v1/operators/{test_operator.id}")
    assert response.status_code == 200
    result = response.json()
    assert result["success"] is True
    assert result["data"]["deleted"] is True

    # Проверяем, что оператор удален
    response = await client.get(f"/api/v1/operators/{test_operator.id}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_operator_not_found(client: AsyncClient):
    """Тест удаления несуществующего оператора"""
    response = await client.delete("/api/v1/operators/99999")
    assert response.status_code == 404
