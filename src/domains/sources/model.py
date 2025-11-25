"""Модель источника"""

from sqlalchemy import Column, String, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from src.core.base_model import BaseModel


class Source(BaseModel):
    """Модель источника (бота)"""

    __tablename__ = "sources"

    name = Column(String, nullable=False, unique=True, index=True)
    description = Column(String, nullable=True)

    # Связи
    contacts = relationship("Contact", back_populates="source", lazy="selectin")
    operator_weights = relationship(
        "SourceOperatorWeight", back_populates="source", lazy="selectin"
    )


class SourceOperatorWeight(BaseModel):
    """Модель связи источника и оператора с весом"""

    __tablename__ = "source_operator_weights"

    source_id = Column(
        Integer, ForeignKey("sources.id", ondelete="CASCADE"), nullable=False
    )
    operator_id = Column(
        Integer, ForeignKey("operators.id", ondelete="CASCADE"), nullable=False
    )
    weight = Column(
        Integer, default=10, nullable=False
    )  # Вес оператора для этого источника

    # Связи
    source = relationship("Source", back_populates="operator_weights", lazy="selectin")
    operator = relationship(
        "Operator", back_populates="source_weights", lazy="selectin"
    )

    __table_args__ = (
        UniqueConstraint("source_id", "operator_id", name="uq_source_operator"),
    )
