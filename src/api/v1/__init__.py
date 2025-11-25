"""API версия 1"""

from fastapi import APIRouter

from src.api.v1 import operators, sources, contacts, leads

router = APIRouter(prefix="/api/v1")

router.include_router(operators.router, prefix="/operators", tags=["operators"])
router.include_router(sources.router, prefix="/sources", tags=["sources"])
router.include_router(contacts.router, prefix="/contacts", tags=["contacts"])
router.include_router(leads.router, prefix="/leads", tags=["leads"])
