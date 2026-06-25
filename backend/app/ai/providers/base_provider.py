"""
Abstract base class for all AI provider implementations.
Every provider MUST implement this interface.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, AsyncGenerator, AsyncIterator, Optional


@dataclass
class Message:
    role: str        # "system" | "user" | "assistant"
    content: str
    name: Optional[str] = None


@dataclass
class CompletionRequest:
    messages: list[Message]
    model: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 2048
    top_p: float = 1.0
    tools: list[dict] = field(default_factory=list)
    tool_choice: str = "auto"
    stream: bool = False
    metadata: dict = field(default_factory=dict)


@dataclass
class ToolCall:
    id: str
    name: str
    arguments: dict


@dataclass
class CompletionResponse:
    content: str
    model: str
    provider: str
    input_tokens: int
    output_tokens: int
    total_tokens: int
    tool_calls: list[ToolCall] = field(default_factory=list)
    finish_reason: str = "stop"
    raw_response: Any = None


class BaseAIProvider(ABC):
    """
    Abstract AI provider.
    All concrete implementations (Gemini, Ollama)
    must inherit from this class.
    """

    provider_name: str = "base"

    def __init__(self, api_key: Optional[str] = None, **kwargs: Any) -> None:
        self.api_key = api_key
        self._client: Any = None
        self._configure(**kwargs)

    @abstractmethod
    def _configure(self, **kwargs: Any) -> None:
        """Initialize the underlying SDK client."""
        ...

    @abstractmethod
    async def complete(self, request: CompletionRequest) -> CompletionResponse:
        """Generate a completion for the given request."""
        ...

    @abstractmethod
    async def stream(
        self, request: CompletionRequest
    ) -> AsyncGenerator[str, None]:
        """Async-generator that streams tokens from the model."""
        ...

    @abstractmethod
    async def embed(self, text: str) -> list[float]:
        """Generate a text embedding."""
        ...

    @abstractmethod
    async def health_check(self) -> bool:
        """Return True if the provider is reachable and healthy."""
        ...

    def _build_messages(
        self, system_prompt: str, history: list[Message], user_message: str
    ) -> list[Message]:
        """Utility: build a standardised message list."""
        messages: list[Message] = []
        if system_prompt:
            messages.append(Message(role="system", content=system_prompt))
        messages.extend(history)
        messages.append(Message(role="user", content=user_message))
        return messages

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} provider={self.provider_name}>"
