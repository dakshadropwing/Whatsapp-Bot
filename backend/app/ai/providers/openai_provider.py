"""
OpenAI provider implementation.
"""
from __future__ import annotations

from typing import Any, AsyncIterator, Optional

from openai import AsyncOpenAI

from app.ai.providers.base_provider import (
    BaseAIProvider,
    CompletionRequest,
    CompletionResponse,
    ToolCall,
)


class OpenAIProvider(BaseAIProvider):
    """Wraps the OpenAI AsyncOpenAI client."""

    provider_name = "openai"

    def _configure(self, **kwargs: Any) -> None:
        self._client = AsyncOpenAI(api_key=self.api_key)
        self.default_model = kwargs.get("model", "gpt-4o")

    async def complete(self, request: CompletionRequest) -> CompletionResponse:
        messages = [
            {"role": m.role, "content": m.content} for m in request.messages
        ]
        kwargs: dict[str, Any] = dict(
            model=request.model or self.default_model,
            messages=messages,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            top_p=request.top_p,
        )
        if request.tools:
            kwargs["tools"] = request.tools
            kwargs["tool_choice"] = request.tool_choice

        response = await self._client.chat.completions.create(**kwargs)
        choice = response.choices[0]
        msg = choice.message

        tool_calls: list[ToolCall] = []
        if msg.tool_calls:
            import json
            for tc in msg.tool_calls:
                tool_calls.append(
                    ToolCall(
                        id=tc.id,
                        name=tc.function.name,
                        arguments=json.loads(tc.function.arguments),
                    )
                )

        return CompletionResponse(
            content=msg.content or "",
            model=response.model,
            provider=self.provider_name,
            input_tokens=response.usage.prompt_tokens,
            output_tokens=response.usage.completion_tokens,
            total_tokens=response.usage.total_tokens,
            tool_calls=tool_calls,
            finish_reason=choice.finish_reason or "stop",
            raw_response=response,
        )

    async def stream(self, request: CompletionRequest) -> AsyncIterator[str]:
        messages = [
            {"role": m.role, "content": m.content} for m in request.messages
        ]
        async with self._client.chat.completions.stream(
            model=request.model or self.default_model,
            messages=messages,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
        ) as stream:
            async for chunk in stream:
                delta = chunk.choices[0].delta.content
                if delta:
                    yield delta

    async def embed(self, text: str) -> list[float]:
        response = await self._client.embeddings.create(
            model="text-embedding-3-small",
            input=text,
        )
        return response.data[0].embedding

    async def health_check(self) -> bool:
        try:
            await self._client.models.list()
            return True
        except Exception:
            return False
