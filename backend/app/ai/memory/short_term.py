"""
Short-Term Memory — Redis-backed rolling conversation window.

Stores the last MAX_TURNS user+assistant message pairs for a conversation.
Each entry is a JSON-serialised dict kept in a Redis List.

Redis key schema:
    memory:short:{conversation_id}

List layout (newest first, LPUSH):
    [
      '{"role": "assistant", "content": "Hi!"}',
      '{"role": "user",      "content": "Hello"}',   ← most recent pair at index 0-1
      '{"role": "assistant", "content": "Sure..."}',
      '{"role": "user",      "content": "Can you..."}',
      ...
    ]

LTRIM keeps the list bounded to MAX_TURNS * 2 entries (each turn = 2 messages).
A Redis TTL of SESSION_TTL_SECONDS auto-expires inactive sessions.
"""
from __future__ import annotations

import json
import logging
from typing import Optional

from app.ai.providers.base_provider import Message
from app.core.cache.redis_client import get_redis

logger = logging.getLogger(__name__)

# ── Constants ─────────────────────────────────────────────────────────────────

MAX_TURNS: int = 20          # Keep last N user+assistant pairs
SESSION_TTL_SECONDS: int = 86_400   # 24 hours — then Redis auto-deletes

_KEY_PREFIX = "memory:short"


def _redis_key(conversation_id: str) -> str:
    return f"{_KEY_PREFIX}:{conversation_id}"


class ShortTermMemory:
    """
    Redis-backed rolling message window for a single conversation.

    Each call to add_turn() pushes 2 new entries (user + assistant) and
    trims the list so it never exceeds MAX_TURNS * 2 items.

    get_history() returns messages in chronological order (oldest → newest)
    ready to be passed directly into CompletionRequest.messages.
    """

    def __init__(
        self,
        max_turns: int = MAX_TURNS,
        ttl_seconds: int = SESSION_TTL_SECONDS,
    ) -> None:
        self.max_turns = max_turns
        self.ttl_seconds = ttl_seconds

    # ── Write ─────────────────────────────────────────────────────────────────

    async def add_turn(
        self,
        conversation_id: str,
        user_message: str,
        assistant_message: str,
    ) -> None:
        """
        Append one user+assistant pair to the conversation history.

        We push the assistant message first, then the user message, because
        Redis LPUSH prepends — so the list is always in reverse-chronological
        order. get_history() reverses it back.
        """
        redis = await get_redis()
        key = _redis_key(conversation_id)

        # LPUSH(user, assistant):
        # In-memory fallback inserts left-to-right → list: [assistant, user, ...older...]
        # Reversal → [...older..., user, assistant] ✓  (user then assistant = correct)
        await redis.lpush(
            key,
            json.dumps({"role": "user", "content": user_message}),
            json.dumps({"role": "assistant", "content": assistant_message}),
        )

        # Trim to keep at most max_turns * 2 individual messages
        max_items = self.max_turns * 2
        await redis.ltrim(key, 0, max_items - 1)

        # Refresh TTL on every write
        await redis.expire(key, self.ttl_seconds)

        logger.debug(
            "ShortTermMemory: saved turn for conversation=%s", conversation_id
        )

    # ── Read ──────────────────────────────────────────────────────────────────

    async def get_history(
        self,
        conversation_id: str,
        limit: Optional[int] = None,
    ) -> list[Message]:
        """
        Return conversation history in chronological order (oldest → newest).

        Args:
            conversation_id: the conversation UUID string
            limit: if set, return only the last `limit` messages
                   (e.g. limit=6 → last 3 turns)

        Returns:
            List of Message objects ready for CompletionRequest.messages
        """
        redis = await get_redis()
        key = _redis_key(conversation_id)

        # Fetch all stored entries (newest-first from Redis)
        raw_items: list = await redis.lrange(key, 0, -1)

        if not raw_items:
            return []

        # Decode bytes if real Redis, strings if fallback
        messages: list[Message] = []
        for item in raw_items:
            if isinstance(item, bytes):
                item = item.decode("utf-8")
            data = json.loads(item)
            messages.append(Message(role=data["role"], content=data["content"]))

        # Reverse to get chronological order (oldest first)
        messages.reverse()

        if limit:
            messages = messages[-limit:]

        return messages

    # ── Stats ─────────────────────────────────────────────────────────────────

    async def get_message_count(self, conversation_id: str) -> int:
        """Return total number of individual messages stored."""
        redis = await get_redis()
        return await redis.llen(_redis_key(conversation_id))

    async def get_turn_count(self, conversation_id: str) -> int:
        """Return number of complete user+assistant turns stored."""
        count = await self.get_message_count(conversation_id)
        return count // 2

    # ── Clear ─────────────────────────────────────────────────────────────────

    async def clear(self, conversation_id: str) -> None:
        """Delete all stored history for this conversation."""
        redis = await get_redis()
        await redis.delete(_redis_key(conversation_id))
        logger.debug(
            "ShortTermMemory: cleared history for conversation=%s", conversation_id
        )

    # ── Exists ────────────────────────────────────────────────────────────────

    async def has_history(self, conversation_id: str) -> bool:
        """Return True if any messages are stored for this conversation."""
        redis = await get_redis()
        return bool(await redis.exists(_redis_key(conversation_id)))
