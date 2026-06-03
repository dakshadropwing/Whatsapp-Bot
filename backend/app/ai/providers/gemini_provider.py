"""
Gemini provider — TODO: implement.
"""
from app.ai.providers.base_provider import BaseAIProvider, CompletionRequest, CompletionResponse
from typing import Any, AsyncIterator


class GeminiProvider(BaseAIProvider):
    provider_name = "gemini"

    def _configure(self, **kwargs: Any) -> None:
        pass  # TODO: initialise SDK client

    async def complete(self, request: CompletionRequest) -> CompletionResponse:
        raise NotImplementedError("GeminiProvider.complete not implemented")

    async def stream(self, request: CompletionRequest) -> AsyncIterator[str]:
        raise NotImplementedError("GeminiProvider.stream not implemented")
        # Required to make it a generator
        yield ""

    async def embed(self, text: str) -> list[float]:
        raise NotImplementedError("GeminiProvider.embed not implemented")

    async def health_check(self) -> bool:
        return False
