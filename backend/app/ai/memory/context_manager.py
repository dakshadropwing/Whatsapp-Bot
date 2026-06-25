"""
ContextManager — unified memory interface for AI agents.

This is the ONLY class that agents and the orchestrator should import.
It combines short-term (Redis) and long-term (PostgreSQL) memory into
a single, simple API.

Typical agent usage:

    from app.ai.memory.context_manager import ContextManager

    ctx = ContextManager()

    # Build full message list for the LLM (short-term history + system prompt)
    messages = await ctx.build_messages(
        conversation_id="abc-123",
        system_prompt="You are a helpful WhatsApp support agent.",
        new_user_message="I need help with my order",
    )

    # After getting the AI reply, save the turn
    await ctx.save_turn(
        conversation_id="abc-123",
        user_message="I need help with my order",
        assistant_message="Sure! What is your order number?",
    )
"""
from __future__ import annotations

import logging
from typing import Optional, Any

from app.ai.memory.short_term import ShortTermMemory
from app.ai.memory.long_term import LongTermMemory
from app.ai.providers.base_provider import Message

logger = logging.getLogger(__name__)


class ContextManager:
    """
    Unified memory interface that combines short-term (Redis) and
    long-term (PostgreSQL) memory for a conversation.

    Short-term: last N messages from Redis → fed directly as message history
    Long-term:  contact profile from PostgreSQL → injected into system prompt

    The long-term memory is optional — if no db_session / conversation
    object is provided, only short-term memory is used. This makes the
    class safe to call from async background tasks that may not have a
    database session.
    """

    MAX_HISTORY = 20   # rolling window size (passed to ShortTermMemory)

    def __init__(self) -> None:
        self._short = ShortTermMemory(max_turns=self.MAX_HISTORY)
        self._long = LongTermMemory()

    # ── Main method: used by every agent on every turn ────────────────────────

    async def build_messages(
        self,
        conversation_id: str,
        system_prompt: str,
        new_user_message: str,
        conversation_obj: Optional[Any] = None,     # SQLAlchemy Conversation instance
        history_limit: Optional[int] = None,         # override max messages
        rag_context: Optional[str] = None,           # pre-formatted RAG context block
    ) -> list[Message]:
        """
        Build the complete message list to pass to CompletionRequest.

        Structure returned:
            [
              Message(role="system",    content="<system_prompt + long-term facts + RAG>"),
              Message(role="user",      content="<oldest remembered message>"),
              Message(role="assistant", content="..."),
              ...                           ← recent history from Redis
              Message(role="user",      content="<new_user_message>"),
            ]

        Args:
            conversation_id:   string UUID of the conversation
            system_prompt:     the agent's base system prompt
            new_user_message:  the latest message from the user
            conversation_obj:  optional Conversation ORM object for long-term memory
            history_limit:     optional override for max history messages
            rag_context:       optional pre-formatted RAG context string from
                               Retriever.format_context(). When provided it is
                               appended to the system prompt so the LLM can
                               ground its answer in your Knowledge Base.

        Returns:
            list[Message] ready to pass to CompletionRequest.messages
        """
        messages: list[Message] = []

        # ── 1. Build system prompt (base + long-term memory + RAG context) ────
        enriched_system = system_prompt

        # 1a. Append long-term contact memory (if available)
        if conversation_obj is not None:
            lt_summary = self._long.get_summary(conversation_obj)
            if lt_summary:
                enriched_system = (
                    f"{enriched_system}\n\n"
                    f"--- Contact Memory ---\n{lt_summary}"
                )

        # 1b. Append RAG retrieved knowledge (if provided)
        if rag_context:
            enriched_system = (
                f"{enriched_system}\n\n"
                f"{rag_context}"
            )

        messages.append(Message(role="system", content=enriched_system))

        # ── 2. Inject short-term history ──────────────────────────────────────
        history = await self._short.get_history(
            conversation_id, limit=history_limit
        )
        messages.extend(history)

        # ── 3. Append the new user message ────────────────────────────────────
        messages.append(Message(role="user", content=new_user_message))

        logger.debug(
            "ContextManager.build_messages: conversation=%s total_messages=%d "
            "(system=1, history=%d, new=1)",
            conversation_id,
            len(messages),
            len(history),
        )
        return messages

    # ── Short-term operations ─────────────────────────────────────────────────

    async def get_history(
        self,
        conversation_id: str,
        limit: Optional[int] = None,
    ) -> list[Message]:
        """Return the short-term message history for this conversation."""
        return await self._short.get_history(conversation_id, limit=limit)

    async def save_turn(
        self,
        conversation_id: str,
        user_message: str,
        assistant_message: str,
    ) -> None:
        """
        Save a completed user+assistant turn to short-term memory (Redis).
        Call this AFTER the AI has responded.
        """
        await self._short.add_turn(conversation_id, user_message, assistant_message)
        logger.debug(
            "ContextManager.save_turn: saved for conversation=%s", conversation_id
        )

    async def get_turn_count(self, conversation_id: str) -> int:
        """Return how many turns are currently stored in short-term memory."""
        return await self._short.get_turn_count(conversation_id)

    async def has_history(self, conversation_id: str) -> bool:
        """Return True if any short-term history exists for this conversation."""
        return await self._short.has_history(conversation_id)

    # ── Long-term operations ──────────────────────────────────────────────────

    def get_long_term_summary(self, conversation_obj: Any) -> str:
        """
        Return the long-term profile as a human-readable string.
        Useful for debugging or logging what the AI "knows" about a contact.
        """
        return self._long.get_summary(conversation_obj)

    def update_fact(
        self,
        conversation_obj: Any,
        key: str,
        value: Any,
        db_session: Any,
    ) -> None:
        """
        Save a persistent fact about the contact.

        Example:
            ctx.update_fact(convo, "user_name", "Daksha", db)
            ctx.update_fact(convo, "last_intent", "order_support", db)
            ctx.update_fact(convo, "language", "en", db)
        """
        self._long.update_fact(conversation_obj, key, value, db_session)

    def append_key_fact(
        self,
        conversation_obj: Any,
        fact: str,
        db_session: Any,
    ) -> None:
        """
        Add a free-text fact to the contact's known facts list.

        Example:
            ctx.append_key_fact(convo, "prefers English communication", db)
            ctx.append_key_fact(convo, "has premium subscription", db)
        """
        self._long.append_key_fact(conversation_obj, fact, db_session)

    def increment_turn_count(self, conversation_obj: Any, db_session: Any) -> int:
        """Increment the total conversation turn counter in long-term memory."""
        return self._long.increment_turn_count(conversation_obj, db_session)

    # ── Clear ─────────────────────────────────────────────────────────────────

    async def clear_short_term(self, conversation_id: str) -> None:
        """Clear only the Redis (short-term) history."""
        await self._short.clear(conversation_id)

    def clear_long_term(self, conversation_obj: Any, db_session: Any) -> None:
        """Clear only the PostgreSQL (long-term) profile."""
        self._long.reset(conversation_obj, db_session)

    async def clear_all(
        self,
        conversation_id: str,
        conversation_obj: Optional[Any] = None,
        db_session: Optional[Any] = None,
    ) -> None:
        """Clear both short-term and long-term memory."""
        await self.clear_short_term(conversation_id)
        if conversation_obj and db_session:
            self.clear_long_term(conversation_obj, db_session)
        logger.info(
            "ContextManager.clear_all: cleared memory for conversation=%s",
            conversation_id,
        )
