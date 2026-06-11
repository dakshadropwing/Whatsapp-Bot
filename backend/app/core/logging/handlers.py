"""
Custom logging handlers.
"""
from __future__ import annotations

import logging


class CeleryNotificationLogHandler(logging.Handler):
    """
    Log handler that triggers a Celery critical notification task for errors.
    """
    def __init__(self, level=logging.ERROR) -> None:
        super().__init__(level)

    def emit(self, record: logging.LogRecord) -> None:
        try:
            # Avoid circular imports
            from app.tasks.notification_tasks import send_critical_alert
            msg = self.format(record)
            # Dispatch asynchronously in Celery
            send_critical_alert.delay(
                org_id="00000000-0000-0000-0000-000000000000",
                title=f"Log Error: {record.levelname}",
                body=msg,
            )
        except Exception:
            # Avoid infinite loops during log emission
            pass