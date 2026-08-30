from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="",
        extra="ignore",
        case_sensitive=False,
    )

    app_env: str = "dev"

    postgres_user: str = "jugo"
    postgres_password: str = "jugo"
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "jugo"
    postgres_dsn: str = ""
    database_url: str = ""

    redis_url: str = "redis://localhost:6379/0"

    s3_endpoint: str = "http://localhost:9000"
    s3_access_key: str = "minio"
    s3_secret_key: str = "minio123"
    s3_bucket: str = "jugo"
    s3_region: str = "ru-1"

    jwt_secret: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_ttl_minutes: int = 60

    ai_provider: str = "openai"
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    yandex_api_key: str = ""
    yandex_folder_id: str = ""
    yandex_model: str = "yandexgpt-lite"
    yandex_endpoint: str = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"

    tei_url: str = "http://localhost:8080"
    embedding_dim: int = 1024

    @property
    def postgres_url(self) -> str:
        if self.database_url:
            return self.database_url
        if self.postgres_dsn:
            return self.postgres_dsn
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def is_prod(self) -> bool:
        return self.app_env == "prod"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
