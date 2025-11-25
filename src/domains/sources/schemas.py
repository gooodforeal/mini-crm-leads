"""Pydantic схемы для источников"""

from typing import Optional, List

from pydantic import BaseModel, Field

from src.core.schemas import TimestampMixin


class SourceBase(BaseModel):
    """Базовая схема источника"""

    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None


class SourceCreate(SourceBase):
    """Схема создания источника"""

    pass


class SourceUpdate(BaseModel):
    """Схема обновления источника"""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None


class SourceResponse(SourceBase, TimestampMixin):
    """Схема ответа с источником"""

    id: int

    model_config = {"from_attributes": True}


class SourceOperatorWeightBase(BaseModel):
    """Базовая схема веса оператора для источника"""

    operator_id: int
    weight: int = Field(default=10, ge=1)


class SourceOperatorWeightCreate(SourceOperatorWeightBase):
    """Схема создания веса"""

    pass


class SourceOperatorWeightResponse(SourceOperatorWeightBase, TimestampMixin):
    """Схема ответа с весом"""

    id: int
    source_id: int

    model_config = {"from_attributes": True}


class SourceWithWeightsResponse(SourceResponse):
    """Схема источника с весами операторов"""

    operator_weights: List[SourceOperatorWeightResponse] = []
