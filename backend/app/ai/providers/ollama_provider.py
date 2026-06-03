"""
Ollama provider — TODO: implement.
"""
from app.ai.providers.base_provider import BaseAIProvider, CompletionRequest, CompletionResponse
from typing import Any, AsyncIterator


class OllamaProvider(BaseAIProvider):
    provider_name = "ollama"

    def _configure(self, **kwargs: Any) -> None:
        pass  # TODO: initialise SDK client

    async def complete(self, request: CompletionRequest) -> CompletionResponse:
        raise NotImplementedError("OllamaProvider.complete not implemented")

    async def stream(self, request: CompletionRequest) -> AsyncIterator[str]:
        raise NotImplementedError("OllamaProvider.stream not implemented")
        # Required to make it a generator
        yield ""

    async def embed(self, text: str) -> list[float]:
        raise NotImplementedError("OllamaProvider.embed not implemented")

    async def health_check(self) -> bool:
        return False
