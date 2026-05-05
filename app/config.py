from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration, loaded from the environment / .env file."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/urlshortener"
    redis_url: str = "redis://localhost:6379/0"
    base_url: str = "http://localhost:8000"

    cache_ttl: int = 3600

    rate_limit_max: int = 20
    rate_limit_window: int = 60

    id_offset: int = 1_000_000


@lru_cache
def get_settings() -> Settings:
    return Settings()
