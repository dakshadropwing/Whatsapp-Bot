"""
Shutdown lifecycle events.
"""
from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


def register_shutdown_events(app) -> None:
    """Register tasks executed when the application teardown context finishes."""

    @app.teardown_appcontext
    def cleanup_resources(exception=None):
        try:
            # Cleanup operations if required
            pass
        except Exception as exc:
            logger.error("Error during teardown cleanup: %s", exc)
