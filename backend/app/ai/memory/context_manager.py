"""Conversation context manager — manages short and long-term memory."""
from __future__ import annotations
from app.ai.providers.base_provider import Message

class ContextManager:
    """Manages per-conversation message history using Redis."""

    MAX_HISTORY = 20  # Rolling window

    async def get_history(self, conversation_id: str) -> list[Message]:
        """Retrieve recent conversation history from Redis."""
        # TODO: implement Redis-backed history retrieval
        return []

    async def save_turn(
        self,
        conversation_id: str,
        user_message: str,
        assistant_message: str,
    ) -> None:
        """Append a user+assistant turn to conversation history."""
        # TODO: implement Redis LPUSH with LTRIM
        pass

    async def clear(self, conversation_id: str) -> None:
        """Clear conversation history."""
        pass
