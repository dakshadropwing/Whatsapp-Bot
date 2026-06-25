"""
Provider Factory — resolves the correct AI provider at runtime.
"""
from __future__ import annotations

from enum import Enum
from typing import Optional

from app.ai.providers.base_provider import BaseAIProvider
from app.core.config.settings import get_settings


class ProviderType(str, Enum):
    GEMINI = "gemini"
    OLLAMA = "ollama"
    OPENAI = "openai"


class ProviderFactory:
    """
    Singleton factory that instantiates and caches AI providers.
    Supports hot-swap of providers without restarting the server.
    """

    _instances: dict[str, BaseAIProvider] = {}

    @classmethod
    def get_provider(
        cls,
        provider_type: Optional[str] = None,
        force_new: bool = False,
    ) -> BaseAIProvider:
        settings = get_settings()
        ptype = provider_type or settings.DEFAULT_AI_PROVIDER
        cache_key = ptype

        if not force_new and cache_key in cls._instances:
            return cls._instances[cache_key]

        provider = cls._create(ptype, settings)
        cls._instances[cache_key] = provider
        return provider

    @classmethod
    def _create(cls, ptype: str, settings) -> BaseAIProvider:
        if ptype == ProviderType.GEMINI:
            from app.ai.providers.gemini_provider import GeminiProvider
            return GeminiProvider(
                api_key=settings.GOOGLE_AI_API_KEY,
                model=settings.GOOGLE_AI_MODEL,
            )
        elif ptype == ProviderType.OLLAMA:
            from app.ai.providers.ollama_provider import OllamaProvider
            return OllamaProvider(
                base_url=settings.OLLAMA_BASE_URL,
                model=settings.OLLAMA_MODEL,
                embed_model=settings.OLLAMA_EMBED_MODEL,
            )
        elif ptype == ProviderType.OPENAI:
            from app.ai.providers.openai_provider import OpenAIProvider
            return OpenAIProvider(
                api_key=settings.OPENAI_API_KEY,
            )
        else:
            raise ValueError(f"Unknown AI provider: {ptype}")

    @classmethod
    def clear_cache(cls) -> None:
        """Clear cached provider instances (e.g. after key rotation)."""
        cls._instances.clear()

    @classmethod
    def list_available(cls) -> list[str]:
        settings = get_settings()
        available = []
        if settings.GOOGLE_AI_API_KEY:
            available.append(ProviderType.GEMINI)
        if settings.OPENAI_API_KEY:
            available.append(ProviderType.OPENAI)
        available.append(ProviderType.OLLAMA)  # Always available if running locally
        return available
