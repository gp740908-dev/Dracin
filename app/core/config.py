from functools import lru_cache
from pydantic import AnyHttpUrl, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Melolo API Aggregator"
    environment: str = "development"
    database_url: str = "postgresql+asyncpg://melolo:melolo@localhost:5432/melolo"
    redis_url: str | None = None
    signing_secret: str = Field(default="change-me-in-production", min_length=16)
    signed_url_ttl_seconds: int = 600
    video_cdn_base_url: AnyHttpUrl | str = "https://cdn.melolo.com"
    allowed_origins: list[str] = ["https://melolo.com", "https://partner.example.com"]
    default_rate_limit_per_minute: int = 120
    cache_ttl_seconds: int = 60

    model_config = SettingsConfigDict(env_file=".env", env_prefix="MELOLO_", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
