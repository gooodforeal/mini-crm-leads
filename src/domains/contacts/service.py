"""Сервис для бизнес-логики обращений"""

import random
from typing import List, Optional

from src.core.exceptions import NotFoundError
from src.domains.contacts.repository import ContactRepository
from src.domains.contacts.schemas import (
    ContactCreate,
    ContactUpdate,
    ContactResponse,
    ContactDetailResponse,
)
from src.domains.leads.repository import LeadRepository
from src.domains.sources.repository import (
    SourceRepository,
    SourceOperatorWeightRepository,
)
from src.domains.operators.repository import OperatorRepository
from src.utils.logger import logger


class ContactService:
    """Сервис обращений"""

    def __init__(
        self,
        repository: ContactRepository,
        lead_repository: LeadRepository,
        source_repository: SourceRepository,
        operator_repository: OperatorRepository,
        weight_repository: SourceOperatorWeightRepository,
    ):
        self.repository = repository
        self.lead_repository = lead_repository
        self.source_repository = source_repository
        self.operator_repository = operator_repository
        self.weight_repository = weight_repository

    async def create_contact(self, data: ContactCreate) -> ContactDetailResponse:
        """Создать обращение с автоматическим распределением оператора"""
        # Проверяем существование источника
        source = await self.source_repository.get_by_id(data.source_id)
        if not source:
            logger.warning(f"Source not found: source_id={data.source_id}")
            raise NotFoundError("Source")

        # Находим или создаем лида
        lead = await self.lead_repository.find_or_create(
            external_id=data.external_id,
            phone=data.phone,
            email=data.email,
            name=data.name,
        )

        # Выбираем оператора
        operator_id = await self._select_operator(data.source_id)

        # Создаем обращение
        contact = await self.repository.create(
            lead_id=lead.id,
            source_id=data.source_id,
            operator_id=operator_id,
            message=data.message,
            is_active=True,
        )

        # Загружаем связанные данные
        contact = await self.repository.get_by_id_with_relations(contact.id)
        if not contact:
            logger.error(f"Contact created but not found: contact_id={contact.id}")
            raise NotFoundError("Contact")

        return ContactDetailResponse.model_validate(contact)

    async def _select_operator(self, source_id: int) -> Optional[int]:
        """Выбрать оператора для источника по алгоритму распределения"""
        # Получаем доступных операторов
        available_operators = await self.operator_repository.get_available_operators(
            source_id
        )

        if not available_operators:
            logger.warning(f"No available operators for source: source_id={source_id}")
            return None

        # Получаем веса для этих операторов
        weights_data = await self.weight_repository.get_by_source(source_id)
        weights_map = {w.operator_id: w.weight for w in weights_data}

        # Фильтруем только операторов с весами
        operators_with_weights = [
            op for op in available_operators if op.id in weights_map
        ]

        if not operators_with_weights:
            logger.warning(
                f"No operators with weights for source: source_id={source_id}"
            )
            return None

        # Вычисляем суммарный вес
        total_weight = sum(weights_map[op.id] for op in operators_with_weights)

        if total_weight == 0:
            # Если все веса нулевые, выбираем случайно
            selected = random.choice(operators_with_weights)
            return selected.id

        # Случайный выбор с учетом весов
        random_value = random.uniform(0, total_weight)
        current_sum = 0

        for operator in operators_with_weights:
            current_sum += weights_map[operator.id]
            if random_value <= current_sum:
                return operator.id

        # На всякий случай возвращаем первого
        return operators_with_weights[0].id

    async def get_contact(self, contact_id: int) -> ContactDetailResponse:
        """Получить обращение по ID"""
        contact = await self.repository.get_by_id_with_relations(contact_id)
        if not contact:
            logger.warning(f"Contact not found: contact_id={contact_id}")
            raise NotFoundError("Contact")
        return ContactDetailResponse.model_validate(contact)

    async def get_all_contacts(
        self, skip: int = 0, limit: int = 100
    ) -> List[ContactResponse]:
        """Получить все обращения"""
        contacts = await self.repository.get_all(skip=skip, limit=limit)
        return [ContactResponse.model_validate(c) for c in contacts]

    async def get_contacts_by_lead(self, lead_id: int) -> List[ContactDetailResponse]:
        """Получить все обращения лида"""
        contacts = await self.repository.get_by_lead(lead_id)
        return [ContactDetailResponse.model_validate(c) for c in contacts]

    async def update_contact(
        self, contact_id: int, data: ContactUpdate
    ) -> ContactResponse:
        """Обновить обращение"""
        contact = await self.repository.get_by_id(contact_id)
        if not contact:
            logger.warning(f"Contact not found for update: contact_id={contact_id}")
            raise NotFoundError("Contact")

        update_data = data.model_dump(exclude_unset=True)
        updated_contact = await self.repository.update(contact_id, **update_data)
        return ContactResponse.model_validate(updated_contact)

    async def get_statistics(self) -> dict:
        """Получить статистику распределения обращений"""
        return await self.repository.get_statistics()
