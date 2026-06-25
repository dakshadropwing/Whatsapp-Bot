"""
CORS middleware — cross-origin resource sharing configuration.
"""
from __future__ import annotations

from flask_cors import CORS

from app.core.config.settings import get_settings


def setup_cors_middleware(app) -> None:
    """Register CORS headers and configuration on *app*."""
    settings = get_settings()
    CORS(
        app,
        origins=settings.CORS_ORIGINS,
        supports_credentials=True,
        allow_headers=["Content-Type", "Authorization", "X-Tenant-ID", "X-Request-ID"],
        methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    )
