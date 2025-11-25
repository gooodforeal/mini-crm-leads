"""Конфигурация приложения"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Настройки приложения"""

    database_url: str = "postgresql+asyncpg://postgres:postgres@db:5432/mini_crm"
    project_name: str = "Mini CRM Leads"
    debug: bool = False

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
