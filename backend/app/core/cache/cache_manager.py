"""
Cache manager — decorators and key helpers for Redis caching.
"""
from __future__ import annotations

import functools
from typing import Any, Callable

from app.extensions import cache


def generate_cache_key(namespace: str, *args: Any, **kwargs: Any) -> str:
    """Generate a clean, deterministic cache key namespace:arg1:arg2..."""
    key_parts = [namespace]
    for arg in args:
        key_parts.append(str(arg))
    for k, v in sorted(kwargs.items()):
        key_parts.append(f"{k}={v}")
    return ":".join(key_parts)


def cache_response(namespace: str, timeout: int = 300) -> Callable:
    """
    Decorator to cache route or service returns using custom keys.
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            key = generate_cache_key(namespace, *args, **kwargs)
            cached_data = cache.get(key)
            if cached_data is not None:
                return cached_data

            result = func(*args, **kwargs)
            cache.set(key, result, timeout=timeout)
            return result
        return wrapper
    return decorator
