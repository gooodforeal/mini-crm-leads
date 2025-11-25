"""Управление жизненным циклом приложения"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI

from src.core.database import engine

# Импорт всех моделей для регистрации в Base.metadata
from src.domains.operators.model import Operator  # noqa: F401
from src.domains.sources.model import Source, SourceOperatorWeight  # noqa: F401
from src.domains.leads.model import Lead  # noqa: F401
from src.domains.contacts.model import Contact  # noqa: F401


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Управление жизненным циклом приложения"""
    yield
    # При остановке: закрытие соединений
    await engine.dispose()
