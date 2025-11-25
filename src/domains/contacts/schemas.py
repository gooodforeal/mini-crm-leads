"""Pydantic схемы для обращений"""

from typing import Optional

from pydantic import BaseModel

from src.core.schemas import TimestampMixin
from src.domains.leads.schemas import LeadResponse
from src.domains.sources.schemas import SourceResponse
from src.domains.operators.schemas import OperatorResponse


class ContactBase(BaseModel):
    """Базовая схема обращения"""

    lead_id: int
    source_id: int
    message: Optional[str] = None


class ContactCreate(BaseModel):
    """Схема создания обращения"""

    # Данные для поиска/создания лида
    external_id: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    name: Optional[str] = None

    # Источник
    source_id: int

    # Дополнительные данные
    message: Optional[str] = None


class ContactUpdate(BaseModel):
    """Схема обновления обращения"""

    is_active: Optional[bool] = None
    message: Optional[str] = None
    operator_id: Optional[int] = None


class ContactResponse(ContactBase, TimestampMixin):
    """Схема ответа с обращением"""

    id: int
    operator_id: Optional[int] = None
    is_active: bool

    model_config = {"from_attributes": True}


class ContactDetailResponse(ContactResponse):
    """Схема обращения с деталями"""

    lead: LeadResponse
    source: SourceResponse
    operator: Optional[OperatorResponse] = None
