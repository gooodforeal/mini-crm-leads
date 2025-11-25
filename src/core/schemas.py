"""Общие Pydantic схемы"""

from datetime import datetime
from typing import Generic, TypeVar, Optional

from pydantic import BaseModel, ConfigDict

T = TypeVar("T")


class StandardResponse(BaseModel, Generic[T]):
    """Стандартный ответ API"""

    success: bool = True
    data: Optional[T] = None
    message: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class TimestampMixin(BaseModel):
    """Миксин с временными метками"""

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
