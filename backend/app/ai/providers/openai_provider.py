import json
from typing import Any, AsyncGenerator, Optional

from openai import AsyncOpenAI
from openai.types.chat import ChatCompletion

from app.ai.providers.base_provider import (
    BaseAIProvider,
    CompletionRequest,
    CompletionResponse,
    ToolCall,
)


class OpenAIProvider(BaseAIProvider):
    """
    OpenAI provider using the official `openai` SDK.
    """

    provider_name = "openai"

    def _configure(self, **kwargs: Any) -> None:
        self._client = AsyncOpenAI(api_key=self.api_key)

    async def complete(self, request: CompletionRequest) -> CompletionResponse:
        # Map our agnostic message structure to OpenAI's dict structure
        openai_messages = []
        for msg in request.messages:
            m = {"role": msg.role, "content": msg.content}
            if msg.name:
                m["name"] = msg.name
            openai_messages.append(m)

        kwargs = {
            "model": request.model or "gpt-4o",
            "messages": openai_messages,
            "temperature": request.temperature,
            "max_tokens": request.max_tokens,
            "top_p": request.top_p,
        }

        if request.tools:
            kwargs["tools"] = request.tools
            if request.tool_choice:
                kwargs["tool_choice"] = request.tool_choice

        # Call the OpenAI API
        response: ChatCompletion = await self._client.chat.completions.create(**kwargs)
        
        choice = response.choices[0]
        content = choice.message.content or ""
        
        # Parse Tool Calls
        tool_calls = []
        if choice.message.tool_calls:
            for tc in choice.message.tool_calls:
                tool_calls.append(
                    ToolCall(
                        id=tc.id,
                        name=tc.function.name,
                        arguments=json.loads(tc.function.arguments)
                    )
                )

        return CompletionResponse(
            content=content,
            model=response.model,
            provider=self.provider_name,
            input_tokens=response.usage.prompt_tokens if response.usage else 0,
            output_tokens=response.usage.completion_tokens if response.usage else 0,
            total_tokens=response.usage.total_tokens if response.usage else 0,
            tool_calls=tool_calls,
            finish_reason=choice.finish_reason,
            raw_response=response.model_dump()
        )

    async def stream(
        self, request: CompletionRequest
    ) -> AsyncGenerator[str, None]:
        openai_messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]

        stream = await self._client.chat.completions.create(
            model=request.model or "gpt-4o",
            messages=openai_messages,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            top_p=request.top_p,
            stream=True,
        )
        
        async for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    async def embed(self, text: str) -> list[float]:
        response = await self._client.embeddings.create(
            input=[text],
            model="text-embedding-3-small"
        )
        return response.data[0].embedding

    async def health_check(self) -> bool:
        try:
            await self._client.models.list()
            return True
        except Exception:
            return False
