"""Модель оператора"""

from sqlalchemy import Column, Boolean, Integer, String
from sqlalchemy.orm import relationship

from src.core.base_model import BaseModel


class Operator(BaseModel):
    """Модель оператора"""

    __tablename__ = "operators"

    name = Column(String, nullable=False, index=True)
    is_active = Column(Boolean, default=True, nullable=False)
    load_limit = Column(Integer, default=10, nullable=False)  # Лимит активных обращений

    # Связи
    contacts = relationship("Contact", back_populates="operator", lazy="selectin")
    source_weights = relationship(
        "SourceOperatorWeight", back_populates="operator", lazy="selectin"
    )
