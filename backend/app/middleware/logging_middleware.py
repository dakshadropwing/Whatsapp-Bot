"""
Logging middleware — request/response logging with processing time.
"""
from __future__ import annotations

import logging
import time

from flask import request

logger = logging.getLogger(__name__)


def setup_logging_middleware(app) -> None:
    """Register request logging hooks on *app*."""

    @app.before_request
    def record_start_time():
        request.start_time = time.time()

    @app.after_request
    def log_request_response(response):
        # Exempt static files or health checks if necessary
        if request.path.startswith("/static"):
            return response

        duration = 0.0
        if hasattr(request, "start_time"):
            duration = (time.time() - request.start_time) * 1000  # in ms

        logger.info(
            "%s %s - Status: %s - Time: %.2fms - IP: %s",
            request.method,
            request.path,
            response.status_code,
            duration,
            request.remote_addr,
        )
        return response
