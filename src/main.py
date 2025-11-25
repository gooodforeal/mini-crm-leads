"""Точка входа приложения"""

from fastapi import FastAPI

from src.api.base import router as base_router
from src.api.v1 import router as v1_router
from src.core.exceptions import (
    BaseAppException,
    app_exception_handler,
    validation_exception_handler,
    integrity_error_handler,
    database_error_handler,
    operational_error_handler,
    global_exception_handler,
)
from src.core.lifespan import lifespan
from src.core.middleware import setup_cors
from src.core.config import settings
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError, OperationalError, DatabaseError

# Импорт всех схем для пересборки моделей с forward references
from src.domains.leads.schemas import LeadWithContactsResponse  # noqa: F401
from src.domains.contacts.schemas import ContactResponse  # noqa: F401
from src.core.schemas import StandardResponse  # noqa: F401

# Пересборка моделей с forward references
# Это необходимо для правильной работы Pydantic v2 с Generic типами и forward references
LeadWithContactsResponse.model_rebuild()
ContactResponse.model_rebuild()

app = FastAPI(title=settings.project_name, lifespan=lifespan)

# Настройка CORS
setup_cors(app)

# Регистрация роутеров
app.include_router(base_router)
app.include_router(v1_router)

# Регистрация обработчиков исключений
# Порядок важен: более специфичные обработчики регистрируются первыми
app.add_exception_handler(BaseAppException, app_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(IntegrityError, integrity_error_handler)
app.add_exception_handler(OperationalError, operational_error_handler)
app.add_exception_handler(DatabaseError, database_error_handler)
app.add_exception_handler(Exception, global_exception_handler)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)
