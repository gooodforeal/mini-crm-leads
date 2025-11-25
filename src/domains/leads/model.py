"""Модель лида"""

from sqlalchemy import Column, String, Index
from sqlalchemy.orm import relationship

from src.core.base_model import BaseModel


class Lead(BaseModel):
    """Модель лида (клиента)"""

    __tablename__ = "leads"

    external_id = Column(String, nullable=True, index=True)  # Внешний идентификатор
    phone = Column(String, nullable=True, index=True)  # Телефон для идентификации
    email = Column(String, nullable=True, index=True)  # Email для идентификации
    name = Column(String, nullable=True)

    # Связи
    contacts = relationship("Contact", back_populates="lead", lazy="selectin")

    __table_args__ = (Index("idx_lead_identifiers", "external_id", "phone", "email"),)
