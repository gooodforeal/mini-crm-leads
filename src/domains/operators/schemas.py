"""Pydantic схемы для операторов"""

from typing import Optional

from pydantic import BaseModel, Field

from src.core.schemas import TimestampMixin


class OperatorBase(BaseModel):
    """Базовая схема оператора"""

    name: str = Field(..., min_length=1, max_length=255)
    is_active: bool = True
    load_limit: int = Field(default=10, ge=1)


class OperatorCreate(OperatorBase):
    """Схема создания оператора"""

    pass


class OperatorUpdate(BaseModel):
    """Схема обновления оператора"""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    is_active: Optional[bool] = None
    load_limit: Optional[int] = Field(None, ge=1)


class OperatorResponse(OperatorBase, TimestampMixin):
    """Схема ответа с оператором"""

    id: int

    model_config = {"from_attributes": True}
