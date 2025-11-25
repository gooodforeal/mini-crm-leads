"""Модель обращения"""

from sqlalchemy import Column, Integer, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship

from src.core.base_model import BaseModel


class Contact(BaseModel):
    """Модель обращения (контакта)"""

    __tablename__ = "contacts"

    lead_id = Column(
        Integer, ForeignKey("leads.id", ondelete="CASCADE"), nullable=False
    )
    source_id = Column(
        Integer, ForeignKey("sources.id", ondelete="SET NULL"), nullable=False
    )
    operator_id = Column(
        Integer, ForeignKey("operators.id", ondelete="SET NULL"), nullable=True
    )
    is_active = Column(Boolean, default=True, nullable=False)  # Активно ли обращение
    message = Column(Text, nullable=True)  # Текст обращения

    # Связи
    lead = relationship("Lead", back_populates="contacts", lazy="selectin")
    source = relationship("Source", back_populates="contacts", lazy="selectin")
    operator = relationship("Operator", back_populates="contacts", lazy="selectin")
