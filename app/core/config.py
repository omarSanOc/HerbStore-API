from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "HerbStore API"
    database_url: str = "postgresql+psycopg://herbstore:herbstore@localhost:5432/herbstore"
    host: str = "0.0.0.0"
    port: int = 3001
    catalog_latency_ms: int = Field(default=0, ge=0)
    order_processing_ms: int = Field(default=1000, ge=0)
    order_active_hours: int = Field(default=24, gt=0)
    max_body_bytes: int = Field(default=100 * 1024, gt=0)


@lru_cache
def get_settings() -> Settings:
    return Settings()
