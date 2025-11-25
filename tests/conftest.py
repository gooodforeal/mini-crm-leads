"""Конфигурация и фикстуры для тестов"""

import pytest
import tempfile
import os
from typing import AsyncGenerator
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

from src.main import app
from src.core.database import Base, get_db

# Импорт всех моделей для регистрации в Base.metadata
from src.domains.operators.model import Operator  # noqa: F401
from src.domains.sources.model import Source, SourceOperatorWeight  # noqa: F401
from src.domains.leads.model import Lead  # noqa: F401
from src.domains.contacts.model import Contact  # noqa: F401


@pytest.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Фикстура для создания сессии БД для каждого теста"""
    # Создаем временный файл для базы данных
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(db_fd)

    # URL для тестовой базы данных (файловая SQLite)
    test_database_url = f"sqlite+aiosqlite:///{db_path}"

    # Создаем тестовый движок для этого теста
    test_engine = create_async_engine(
        test_database_url,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False,
    )

    TestSessionLocal = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )

    # Создаем таблицы
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Создаем сессию
    async with TestSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

    # Закрываем движок и удаляем файл базы данных
    await test_engine.dispose()
    try:
        os.unlink(db_path)
    except OSError:
        pass  # Файл может быть уже удален


@pytest.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Фикстура для создания тестового клиента"""

    # Создаем функцию override_get_db, которая использует сессию из фикстуры
    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        # Обновляем сессию перед каждым запросом, чтобы видеть изменения после commit
        db_session.expire_all()
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
async def test_operator(db_session: AsyncSession) -> Operator:
    """Создает тестового оператора"""
    operator = Operator(name="Тестовый оператор", is_active=True, load_limit=10)
    db_session.add(operator)
    await db_session.commit()
    await db_session.refresh(operator)
    return operator


@pytest.fixture
async def test_source(db_session: AsyncSession) -> Source:
    """Создает тестовый источник"""
    source = Source(name="Тестовый источник", description="Описание источника")
    db_session.add(source)
    await db_session.commit()
    await db_session.refresh(source)
    return source


@pytest.fixture
async def test_lead(db_session: AsyncSession) -> Lead:
    """Создает тестового лида"""
    lead = Lead(
        external_id="test_ext_1",
        phone="+79991234567",
        email="test@example.com",
        name="Тестовый лид",
    )
    db_session.add(lead)
    await db_session.commit()
    await db_session.refresh(lead)
    return lead
