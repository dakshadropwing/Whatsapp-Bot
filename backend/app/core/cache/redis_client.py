"""
Redis async client with in-memory fallback.

When Redis is unavailable (e.g. local dev without Redis running),
all operations fall through to a simple Python dict so the rest of
the codebase keeps working without crashing.

Usage:
    from app.core.cache.redis_client import get_redis
    redis = await get_redis()
    await redis.set("key", "value", ex=300)
    val = await redis.get("key")
"""
from __future__ import annotations

import json
import logging
import time
from typing import Any, Optional

logger = logging.getLogger(__name__)

# ── In-Memory Fallback ────────────────────────────────────────────────────────
# A minimal dict-backed store used when Redis is unreachable.
# Not thread-safe for production — only meant for local dev / testing.

class _InMemoryRedis:
    """
    Lightweight Redis-compatible interface backed by a plain Python dict.
    Supports: get, set, delete, lpush, lrange, ltrim, expire, exists, rpush.
    """

    def __init__(self) -> None:
        self._store: dict[str, Any] = {}
        self._expiry: dict[str, float] = {}  # key → expiry unix timestamp

    def _is_expired(self, key: str) -> bool:
        exp = self._expiry.get(key)
        if exp is None:
            return False
        if time.time() > exp:
            self._store.pop(key, None)
            self._expiry.pop(key, None)
            return True
        return False

    async def get(self, key: str) -> Optional[bytes]:
        if self._is_expired(key):
            return None
        val = self._store.get(key)
        if val is None:
            return None
        return val.encode() if isinstance(val, str) else val

    async def set(self, key: str, value: Any, ex: Optional[int] = None) -> bool:
        self._store[key] = value
        if ex:
            self._expiry[key] = time.time() + ex
        return True

    async def delete(self, *keys: str) -> int:
        count = 0
        for key in keys:
            if key in self._store:
                self._store.pop(key)
                self._expiry.pop(key, None)
                count += 1
        return count

    async def exists(self, key: str) -> int:
        if self._is_expired(key):
            return 0
        return 1 if key in self._store else 0

    async def expire(self, key: str, seconds: int) -> bool:
        if key in self._store:
            self._expiry[key] = time.time() + seconds
            return True
        return False

    async def lpush(self, key: str, *values: Any) -> int:
        """Prepend values to a list (Redis LPUSH).
        Redis processes each value left-to-right, prepending each one,
        so the LAST value in the call ends up at index 0.
        """
        lst = self._store.setdefault(key, [])
        for v in values:
            lst.insert(0, v)
        return len(lst)

    async def rpush(self, key: str, *values: Any) -> int:
        """Append values to a list (Redis RPUSH)."""
        lst = self._store.setdefault(key, [])
        lst.extend(values)
        return len(lst)

    async def lrange(self, key: str, start: int, stop: int) -> list:
        """Return a slice of a list (Redis LRANGE)."""
        if self._is_expired(key):
            return []
        lst = self._store.get(key, [])
        # Redis LRANGE stop is inclusive; Python stop is exclusive
        end = stop + 1 if stop != -1 else None
        return lst[start:end]

    async def ltrim(self, key: str, start: int, stop: int) -> bool:
        """Trim a list to the specified range (Redis LTRIM)."""
        lst = self._store.get(key, [])
        end = stop + 1 if stop != -1 else None
        self._store[key] = lst[start:end]
        return True

    async def llen(self, key: str) -> int:
        if self._is_expired(key):
            return 0
        return len(self._store.get(key, []))

    async def close(self) -> None:
        pass  # nothing to close


# ── Real Redis Client ─────────────────────────────────────────────────────────

_redis_instance: Optional[Any] = None   # real redis.asyncio.Redis
_fallback_instance = _InMemoryRedis()   # always available
_using_fallback: bool = False


async def get_redis() -> Any:
    """
    Return an async Redis client.

    On first call, attempts to connect to Redis using the REDIS_URL from
    settings. If the connection fails (Redis not running), silently falls
    back to the in-memory implementation and logs a warning.

    Subsequent calls return the cached client (real or fallback).
    """
    global _redis_instance, _using_fallback

    if _redis_instance is not None:
        return _redis_instance

    try:
        import redis.asyncio as aioredis
        from app.core.config.settings import get_settings

        settings = get_settings()
        client = aioredis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=False,  # we handle encoding ourselves
            socket_connect_timeout=2,
            socket_timeout=2,
        )
        # Test the connection
        await client.ping()
        _redis_instance = client
        logger.info("Redis connected at %s", settings.REDIS_URL)
        return _redis_instance

    except Exception as exc:
        logger.warning(
            "Redis unavailable (%s) — using in-memory fallback. "
            "Memory will NOT persist across restarts.",
            exc,
        )
        _using_fallback = True
        _redis_instance = _fallback_instance
        return _redis_instance


def is_using_fallback() -> bool:
    """Returns True if running with the in-memory fallback (no real Redis)."""
    return _using_fallback


async def close_redis() -> None:
    """Gracefully close the Redis connection on app shutdown."""
    global _redis_instance
    if _redis_instance and not _using_fallback:
        await _redis_instance.close()
        _redis_instance = None
