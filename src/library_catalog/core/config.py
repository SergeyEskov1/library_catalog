"""
Конфигурация приложения через pydantic-settings.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Any, Literal

from pydantic import PostgresDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """"""

    environment: Literal["production", "development"] = "production"
    # Основные настройки
    app_name: str = "Library Catalog API"
    environment: Literal["development", "staging", "production"] = "development"
    debug: bool = False

    # База данных
    database_url: PostgresDsn
    database_pool_size: int = 20

    # API
    api_v1_prefix: str = "/api/v1"
    docs_url: str = "/docs"
    redoc_url: str = "/redoc"

    # Логирование
    log_level: str = "INFO"

    # CORS — обязательно задать явно, дефолт намеренно отсутствует.
    # В продакшне "*" запрещён — сервис не запустится.
    # Пример для .env: CORS_ORIGINS='["https://example.com"]'
    cors_origins: list[str]

    @field_validator("cors_origins")
    @classmethod
    def cors_origins_must_be_explicit_in_production(
        cls, v: list[str], info: Any
    ) -> list[str]:
        values = info.data
        if values.get("environment") == "production" and "*" in v:
            raise ValueError(
                'cors_origins cannot contain "*" in production. '
                "Set explicit origins in CORS_ORIGINS env variable."
            )
        return v

    # OpenLibrary
    openlibrary_base_url: str = "https://openlibrary.org"
    openlibrary_timeout: float = 10.0

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
    )

    @property
    def is_production(self) -> bool:
        return self.environment == "production"

    @property
    def database_url_str(self) -> str:
        return str(self.database_url)


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()