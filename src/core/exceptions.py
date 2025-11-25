"""Обработчики исключений"""

import re
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError, OperationalError, DatabaseError
from src.utils.logger import logger


class BaseAppException(Exception):
    """Базовое исключение приложения"""

    def __init__(self, message: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class NotFoundError(BaseAppException):
    """Ошибка - ресурс не найден"""

    def __init__(self, resource: str = "Resource"):
        super().__init__(f"{resource} not found", status.HTTP_404_NOT_FOUND)


class ValidationError(BaseAppException):
    """Ошибка валидации"""

    def __init__(self, message: str):
        super().__init__(message, status.HTTP_422_UNPROCESSABLE_ENTITY)


def _extract_integrity_error_message(exc: IntegrityError) -> str:
    """Извлечь понятное сообщение из ошибки целостности БД"""
    error_message = str(exc.orig) if exc.orig else str(exc)

    # Проверка на нарушение уникальности
    if "unique" in error_message.lower() or "duplicate" in error_message.lower():
        # Попытка извлечь название поля из сообщения
        match = re.search(r"\(([^)]+)\)", error_message)
        if match:
            field = match.group(1)
            return f"Значение для поля '{field}' уже существует"
        return "Нарушение уникальности данных"

    # Проверка на нарушение внешнего ключа
    if "foreign key" in error_message.lower() or "references" in error_message.lower():
        return "Нарушение ссылочной целостности данных"

    # Проверка на NOT NULL
    if "not null" in error_message.lower():
        return "Обязательное поле не может быть пустым"

    # Общее сообщение
    return "Ошибка целостности данных"


async def app_exception_handler(
    request: Request, exc: BaseAppException
) -> JSONResponse:
    """Обработчик исключений приложения"""
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "message": exc.message, "data": None},
    )


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Обработчик ошибок валидации"""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"success": False, "message": "Validation error", "data": exc.errors()},
    )


async def integrity_error_handler(
    request: Request, exc: IntegrityError
) -> JSONResponse:
    """Обработчик ошибок целостности БД"""
    message = _extract_integrity_error_message(exc)
    logger.warning(
        f"Database integrity error: {str(exc.orig) if exc.orig else str(exc)}"
    )
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"success": False, "message": message, "data": None},
    )


async def database_error_handler(request: Request, exc: DatabaseError) -> JSONResponse:
    """Обработчик общих ошибок БД"""
    logger.error(f"Database error: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={
            "success": False,
            "message": "Ошибка подключения к базе данных",
            "data": None,
        },
    )


async def operational_error_handler(
    request: Request, exc: OperationalError
) -> JSONResponse:
    """Обработчик операционных ошибок БД"""
    logger.error(f"Database operational error: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={
            "success": False,
            "message": "Ошибка выполнения операции с базой данных",
            "data": None,
        },
    )


async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Глобальный обработчик всех необработанных исключений"""
    logger.error(
        f"Unhandled exception: {type(exc).__name__}: {str(exc)}",
        exc_info=True,
        extra={"path": request.url.path, "method": request.method},
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "message": "Внутренняя ошибка сервера",
            "data": None,
        },
    )
