"""Pydantic схемы для лидов"""

from __future__ import annotations

from typing import Optional, List, TYPE_CHECKING

from pydantic import BaseModel, Field

from src.core.schemas import TimestampMixin

if TYPE_CHECKING:
    from src.domains.contacts.schemas import ContactResponse


class LeadBase(BaseModel):
    """Базовая схема лида"""

    external_id: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    name: Optional[str] = None


class LeadCreate(LeadBase):
    """Схема создания лида"""

    pass


class LeadUpdate(BaseModel):
    """Схема обновления лида"""

    external_id: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    name: Optional[str] = None


class LeadResponse(LeadBase, TimestampMixin):
    """Схема ответа с лидом"""

    id: int

    model_config = {"from_attributes": True}


class LeadWithContactsResponse(LeadResponse):
    """Схема лида с обращениями"""

    contacts: List["ContactResponse"] = Field(default_factory=list)

    model_config = {"from_attributes": True}
