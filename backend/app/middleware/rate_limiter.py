"""
Rate limiter middleware — configures Flask-Limiter for request throttling.
"""
from __future__ import annotations

import logging

from app.core.config.settings import get_settings
from app.extensions import limiter

logger = logging.getLogger(__name__)


def setup_rate_limiter(app) -> None:
    """Configure and register rate limiting on *app*."""
    settings = get_settings()

    # Set storage backend (falling back to memory if Redis is unavailable or in test mode)
    storage_uri = settings.REDIS_URL
    if app.config.get("TESTING") or not storage_uri:
        storage_uri = "memory://"

    limiter.storage_uri = storage_uri

    limit_minute = f"{settings.RATE_LIMIT_PER_MINUTE} per minute"
    limit_hour = f"{settings.RATE_LIMIT_PER_HOUR} per hour"

    limiter._default_limits = [limit_minute, limit_hour]
    logger.info("Rate limiter registered with storage %s and limits: %s, %s", storage_uri, limit_minute, limit_hour)
