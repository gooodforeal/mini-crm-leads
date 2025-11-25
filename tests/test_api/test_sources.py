"""Тесты для эндпоинтов источников"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.domains.sources.model import Source, SourceOperatorWeight
from src.domains.operators.model import Operator


@pytest.mark.asyncio
async def test_create_source(client: AsyncClient):
    """Тест создания источника"""
    data = {
        "name": "Новый источник",
        "description": "Описание источника",
    }
    response = await client.post("/api/v1/sources", json=data)
    assert response.status_code == 201
    result = response.json()
    assert result["success"] is True
    assert result["data"]["name"] == data["name"]
    assert result["data"]["description"] == data["description"]
    assert "id" in result["data"]
    assert "created_at" in result["data"]


@pytest.mark.asyncio
async def test_create_source_validation_error(client: AsyncClient):
    """Тест валидации при создании источника"""
    # Пустое имя
    data = {"name": ""}
    response = await client.post("/api/v1/sources", json=data)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_source_duplicate_name(client: AsyncClient, test_source: Source):
    """Тест создания источника с дублирующимся именем"""
    data = {"name": test_source.name}
    response = await client.post("/api/v1/sources", json=data)
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_get_sources_empty(client: AsyncClient):
    """Тест получения списка источников (пустой список)"""
    response = await client.get("/api/v1/sources")
    assert response.status_code == 200
    result = response.json()
    assert result["success"] is True
    assert result["data"] == []


@pytest.mark.asyncio
async def test_get_sources(client: AsyncClient, test_source: Source):
    """Тест получения списка источников"""
    response = await client.get("/api/v1/sources")
    assert response.status_code == 200
    result = response.json()
    assert result["success"] is True
    assert len(result["data"]) == 1
    assert result["data"][0]["id"] == test_source.id
    assert result["data"][0]["name"] == test_source.name


@pytest.mark.asyncio
async def test_get_source_by_id(client: AsyncClient, test_source: Source):
    """Тест получения источника по ID"""
    response = await client.get(f"/api/v1/sources/{test_source.id}")
    assert response.status_code == 200
    result = response.json()
    assert result["success"] is True
    assert result["data"]["id"] == test_source.id
    assert result["data"]["name"] == test_source.name


@pytest.mark.asyncio
async def test_get_source_not_found(client: AsyncClient):
    """Тест получения несуществующего источника"""
    response = await client.get("/api/v1/sources/99999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_source_with_weights(
    client: AsyncClient,
    test_source: Source,
    test_operator: Operator,
    db_session: AsyncSession,
):
    """Тест получения источника с весами операторов"""
    # Создаем вес оператора для источника
    weight = SourceOperatorWeight(
        source_id=test_source.id, operator_id=test_operator.id, weight=15
    )
    db_session.add(weight)
    await db_session.flush()
    await db_session.commit()

    response = await client.get(f"/api/v1/sources/{test_source.id}/with-weights")
    assert response.status_code == 200
    result = response.json()
    assert result["success"] is True
    assert result["data"]["id"] == test_source.id
    assert len(result["data"]["operator_weights"]) == 1
    assert result["data"]["operator_weights"][0]["operator_id"] == test_operator.id
    assert result["data"]["operator_weights"][0]["weight"] == 15


@pytest.mark.asyncio
async def test_update_source(client: AsyncClient, test_source: Source):
    """Тест обновления источника"""
    data = {
        "name": "Обновленное имя",
        "description": "Новое описание",
    }
    response = await client.patch(f"/api/v1/sources/{test_source.id}", json=data)
    assert response.status_code == 200
    result = response.json()
    assert result["success"] is True
    assert result["data"]["name"] == data["name"]
    assert result["data"]["description"] == data["description"]


@pytest.mark.asyncio
async def test_update_source_partial(client: AsyncClient, test_source: Source):
    """Тест частичного обновления источника"""
    data = {"name": "Только имя"}
    response = await client.patch(f"/api/v1/sources/{test_source.id}", json=data)
    assert response.status_code == 200
    result = response.json()
    assert result["success"] is True
    assert result["data"]["name"] == data["name"]


@pytest.mark.asyncio
async def test_update_source_not_found(client: AsyncClient):
    """Тест обновления несуществующего источника"""
    data = {"name": "Новое имя"}
    response = await client.patch("/api/v1/sources/99999", json=data)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_source(client: AsyncClient, test_source: Source):
    """Тест удаления источника"""
    response = await client.delete(f"/api/v1/sources/{test_source.id}")
    assert response.status_code == 200
    result = response.json()
    assert result["success"] is True
    assert result["data"]["deleted"] is True

    # Проверяем, что источник удален
    response = await client.get(f"/api/v1/sources/{test_source.id}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_source_not_found(client: AsyncClient):
    """Тест удаления несуществующего источника"""
    response = await client.delete("/api/v1/sources/99999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_set_operator_weight(
    client: AsyncClient, test_source: Source, test_operator: Operator
):
    """Тест установки веса оператора для источника"""
    data = {"operator_id": test_operator.id, "weight": 20}
    response = await client.post(
        f"/api/v1/sources/{test_source.id}/operator-weights", json=data
    )
    assert response.status_code == 201
    result = response.json()
    assert result["success"] is True
    assert result["data"]["source_id"] == test_source.id
    assert result["data"]["operator_id"] == test_operator.id
    assert result["data"]["weight"] == 20


@pytest.mark.asyncio
async def test_set_operator_weight_update(
    client: AsyncClient,
    test_source: Source,
    test_operator: Operator,
    db_session: AsyncSession,
):
    """Тест обновления существующего веса оператора"""
    # Создаем начальный вес
    weight = SourceOperatorWeight(
        source_id=test_source.id, operator_id=test_operator.id, weight=10
    )
    db_session.add(weight)
    await db_session.commit()

    # Обновляем вес
    data = {"operator_id": test_operator.id, "weight": 25}
    response = await client.post(
        f"/api/v1/sources/{test_source.id}/operator-weights", json=data
    )
    assert response.status_code == 201
    result = response.json()
    assert result["data"]["weight"] == 25


@pytest.mark.asyncio
async def test_remove_operator_weight(
    client: AsyncClient,
    test_source: Source,
    test_operator: Operator,
    db_session: AsyncSession,
):
    """Тест удаления веса оператора"""
    # Создаем вес
    weight = SourceOperatorWeight(
        source_id=test_source.id, operator_id=test_operator.id, weight=10
    )
    db_session.add(weight)
    await db_session.commit()

    # Удаляем вес
    response = await client.delete(
        f"/api/v1/sources/{test_source.id}/operator-weights/{test_operator.id}"
    )
    assert response.status_code == 200
    result = response.json()
    assert result["success"] is True
    assert result["data"]["deleted"] is True


@pytest.mark.asyncio
async def test_remove_operator_weight_not_found(
    client: AsyncClient, test_source: Source
):
    """Тест удаления несуществующего веса оператора"""
    response = await client.delete(
        f"/api/v1/sources/{test_source.id}/operator-weights/99999"
    )
    assert response.status_code == 404
