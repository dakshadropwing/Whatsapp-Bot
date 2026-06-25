"""
Central Settings using Pydantic BaseSettings.
Reads from environment variables / .env file.
"""
from __future__ import annotations

import os
from functools import lru_cache
from typing import Any, List, Optional

from pydantic import AnyHttpUrl, Field, validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # ── App ──────────────────────────────────────────────────
    APP_ENV: str = Field(default="development")
    APP_NAME: str = Field(default="AI WhatsApp Automation Platform")
    APP_SECRET_KEY: str = Field(...)
    APP_DEBUG: bool = Field(default=False)
    APP_HOST: str = Field(default="0.0.0.0")
    APP_PORT: int = Field(default=5000)
    APP_WORKERS: int = Field(default=4)
    APP_LOG_LEVEL: str = Field(default="INFO")

    # Flask compat
    @property
    def SECRET_KEY(self) -> str:
        return self.APP_SECRET_KEY

    @property
    def DEBUG(self) -> bool:
        return self.APP_DEBUG

    # ── Database ─────────────────────────────────────────────
    DATABASE_URL: str = Field(...)
    DATABASE_POOL_SIZE: int = Field(default=20)
    DATABASE_MAX_OVERFLOW: int = Field(default=40)
    DATABASE_POOL_TIMEOUT: int = Field(default=30)
    DATABASE_ECHO: bool = Field(default=False)

    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        # Replace asyncpg with psycopg2 for sync Flask/SQLAlchemy
        return self.DATABASE_URL.replace("asyncpg", "psycopg2")

    @property
    def SQLALCHEMY_TRACK_MODIFICATIONS(self) -> bool:
        return False

    @property
    def SQLALCHEMY_ENGINE_OPTIONS(self) -> dict:
        return {
            "pool_size": self.DATABASE_POOL_SIZE,
            "max_overflow": self.DATABASE_MAX_OVERFLOW,
            "pool_timeout": self.DATABASE_POOL_TIMEOUT,
            "pool_pre_ping": True,
        }

    # ── Redis ─────────────────────────────────────────────────
    REDIS_URL: str = Field(default="redis://localhost:6379/0")
    CELERY_BROKER_URL: str = Field(default="redis://localhost:6379/1")
    CELERY_RESULT_BACKEND: str = Field(default="redis://localhost:6379/2")

    @property
    def CACHE_TYPE(self) -> str:
        return "RedisCache"

    @property
    def CACHE_REDIS_URL(self) -> str:
        return self.REDIS_URL

    # ── WhatsApp ──────────────────────────────────────────────
    WHATSAPP_ACCESS_TOKEN: str = Field(...)
    WHATSAPP_PHONE_NUMBER_ID: str = Field(...)
    WHATSAPP_BUSINESS_ACCOUNT_ID: str = Field(...)
    WHATSAPP_WEBHOOK_VERIFY_TOKEN: str = Field(...)
    WHATSAPP_API_VERSION: str = Field(default="v19.0")
    WHATSAPP_API_BASE_URL: str = Field(default="https://graph.facebook.com")

    # ── AI Providers ──────────────────────────────────────────
    GOOGLE_AI_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    GOOGLE_AI_MODEL: str = Field(default="gemini-2.5-flash")
    OLLAMA_BASE_URL: str = Field(default="http://localhost:11434")
    OLLAMA_MODEL: str = Field(default="llama3.2:1b")
    OLLAMA_EMBED_MODEL: str = Field(default="nomic-embed-text")
    DEFAULT_AI_PROVIDER: str = Field(default="ollama")

    # ── JWT ───────────────────────────────────────────────────
    JWT_SECRET_KEY: str = Field(...)
    JWT_ALGORITHM: str = Field(default="HS256")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=60)
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=30)

    # ── Encryption ───────────────────────────────────────────
    ENCRYPTION_MASTER_KEY: str = Field(...)
    ENCRYPTION_KEY_ROTATION_DAYS: int = Field(default=90)

    # ── Storage ───────────────────────────────────────────────
    STORAGE_BACKEND: str = Field(default="s3")
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_S3_BUCKET: Optional[str] = None
    AWS_REGION: str = Field(default="ap-south-1")
    LOCAL_UPLOAD_PATH: str = Field(default="/app/uploads")

    # ── CORS ──────────────────────────────────────────────────
    CORS_ORIGINS: Any = Field(default=["http://localhost:3000"])

    @validator("CORS_ORIGINS", pre=True)
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    # ── Rate Limiting ─────────────────────────────────────────
    RATE_LIMIT_PER_MINUTE: int = Field(default=100)
    RATE_LIMIT_PER_HOUR: int = Field(default=3000)

    # ── Monitoring ────────────────────────────────────────────
    SENTRY_DSN: Optional[str] = None
    SENTRY_ENVIRONMENT: str = Field(default="development")
    PROMETHEUS_METRICS_ENABLED: bool = Field(default=True)

    # ── Multi-Tenancy ─────────────────────────────────────────
    DEFAULT_ORG_SLUG: str = Field(default="default")
    MAX_TENANTS: int = Field(default=100)

    @property
    def is_production(self) -> bool:
        return self.APP_ENV == "production"

    @property
    def is_development(self) -> bool:
        return self.APP_ENV == "development"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached settings singleton."""
    return Settings()
