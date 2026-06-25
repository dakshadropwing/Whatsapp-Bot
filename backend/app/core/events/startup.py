"""
Startup lifecycle events.
"""
from __future__ import annotations

import logging

from app.extensions import db

logger = logging.getLogger(__name__)


def register_startup_events(app) -> None:
    """Register tasks executed on application start."""
    with app.app_context():
        try:
            db.session.execute(db.select(1))
            logger.info("Database connection verified successfully on startup.")
        except Exception as exc:
            logger.critical("Database connection failed on startup: %s", exc)
