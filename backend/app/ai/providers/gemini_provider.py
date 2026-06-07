"""
Gemini provider implementation using the google-genai library.
"""
from __future__ import annotations

import json
import logging
from typing import Any, AsyncIterator, Optional

from google import genai
from google.genai import types

from app.ai.providers.base_provider import (
    BaseAIProvider,
    CompletionRequest,
    CompletionResponse,
    ToolCall,
)

logger = logging.getLogger(__name__)


class GeminiProvider(BaseAIProvider):
    provider_name = "gemini"

    def _configure(self, **kwargs: Any) -> None:
        self.default_model = kwargs.get("model", "gemini-2.5-flash")
        # Initialize the Google GenAI client
        self._client = genai.Client(api_key=self.api_key)

    def _build_gemini_contents_and_config(
        self, request: CompletionRequest
    ) -> tuple[list[types.Content], types.GenerateContentConfig]:
        """
        Helper to construct Gemini-specific contents and configuration
        from a standardized CompletionRequest.
        """
        # Extract system prompt(s)
        system_instructions = [m.content for m in request.messages if m.role == "system"]
        system_instruction = "\n".join(system_instructions) if system_instructions else None

        # Filter out system messages for the main contents list
        gemini_messages = [m for m in request.messages if m.role != "system"]

        contents: list[types.Content] = []
        for msg in gemini_messages:
            if msg.role == "tool":
                response_dict = None
                if msg.content:
                    try:
                        parsed = json.loads(msg.content)
                        if isinstance(parsed, dict):
                            response_dict = parsed
                    except Exception:
                        pass
                if response_dict is None:
                    response_dict = {"result": msg.content or ""}

                contents.append(
                    types.Content(
                        role="tool",
                        parts=[
                            types.Part(
                                function_response=types.FunctionResponse(
                                    name=msg.name,
                                    response=response_dict,
                                )
                            )
                        ],
                    )
                )
            elif msg.role == "assistant":
                contents.append(
                    types.Content(
                        role="model",
                        parts=[types.Part.from_text(text=msg.content or "")],
                    )
                )
            else:  # role="user" or custom roles
                contents.append(
                    types.Content(
                        role="user",
                        parts=[types.Part.from_text(text=msg.content or "")],
                    )
                )

        # Build configuration parameters
        config_kwargs: dict[str, Any] = {
            "temperature": request.temperature,
            "max_output_tokens": request.max_tokens,
            "top_p": request.top_p,
        }

        if system_instruction:
            config_kwargs["system_instruction"] = system_instruction

        if request.tools:
            declarations = []
            for open_ai_tool in request.tools:
                if open_ai_tool.get("type") == "function":
                    func_def = open_ai_tool.get("function", {})
                    declarations.append(
                        types.FunctionDeclaration(
                            name=func_def.get("name"),
                            description=func_def.get("description"),
                            parameters_json_schema=func_def.get("parameters"),
                        )
                    )
            if declarations:
                config_kwargs["tools"] = [types.Tool(function_declarations=declarations)]

            if request.tool_choice:
                mode = "AUTO"
                if request.tool_choice == "none":
                    mode = "NONE"
                elif request.tool_choice in ("required", "any"):
                    mode = "ANY"
                config_kwargs["tool_config"] = types.ToolConfig(
                    function_calling_config=types.FunctionCallingConfig(
                        mode=mode
                    )
                )

        config = types.GenerateContentConfig(**config_kwargs)
        return contents, config

    async def complete(self, request: CompletionRequest) -> CompletionResponse:
        contents, config = self._build_gemini_contents_and_config(request)

        response = await self._client.aio.models.generate_content(
            model=request.model or self.default_model,
            contents=contents,
            config=config,
        )

        # Map tool calls
        tool_calls: list[ToolCall] = []
        if response.function_calls:
            for fc in response.function_calls:
                tool_calls.append(
                    ToolCall(
                        id=fc.id or f"call_{fc.name}",
                        name=fc.name,
                        arguments=fc.args or {},
                    )
                )

        # Get response content text safely
        response_text = ""
        try:
            response_text = response.text or ""
        except ValueError:
            pass

        # Extract token usage
        input_tokens = 0
        output_tokens = 0
        total_tokens = 0
        if response.usage_metadata:
            input_tokens = response.usage_metadata.prompt_token_count or 0
            output_tokens = response.usage_metadata.candidates_token_count or 0
            total_tokens = response.usage_metadata.total_token_count or 0

        # Extract finish reason
        finish_reason = "stop"
        if response.candidates and response.candidates[0].finish_reason:
            raw_reason = response.candidates[0].finish_reason
            if hasattr(raw_reason, "value"):
                finish_reason = str(raw_reason.value).lower()
            elif hasattr(raw_reason, "name"):
                finish_reason = str(raw_reason.name).lower()
            else:
                finish_reason = str(raw_reason).lower()

        return CompletionResponse(
            content=response_text,
            model=request.model or self.default_model,
            provider=self.provider_name,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=total_tokens,
            tool_calls=tool_calls,
            finish_reason=finish_reason,
            raw_response=response,
        )

    async def stream(self, request: CompletionRequest) -> AsyncIterator[str]:
        contents, config = self._build_gemini_contents_and_config(request)

        response_stream = await self._client.aio.models.generate_content_stream(
            model=request.model or self.default_model,
            contents=contents,
            config=config,
        )

        async for chunk in response_stream:
            if chunk.text:
                yield chunk.text

    async def embed(self, text: str) -> list[float]:
        response = await self._client.aio.models.embed_content(
            model="gemini-embedding-2",
            contents=text,
        )
        if response.embeddings and len(response.embeddings) > 0:
            return response.embeddings[0].values
        return []

    async def health_check(self) -> bool:
        try:
            models = await self._client.aio.models.list()
            for _ in models:
                return True
            return False
        except Exception:
            return False