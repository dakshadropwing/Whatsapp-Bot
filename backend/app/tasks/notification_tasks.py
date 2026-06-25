"""
Notification background tasks — asynchronous notification creation.
"""
from __future__ import annotations

import logging

from app.services.notification_service import NotificationService
from app.tasks.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(
    name="app.tasks.notification_tasks.send_critical_alert",
    queue="critical",
)
def send_critical_alert(
    org_id: str,
    title: str,
    body: str,
    user_id: str | None = None,
    metadata: dict | None = None,
) -> str:
    """
    Asynchronously create a high-priority/critical notification event.
    """
    try:
        notification = NotificationService.create_notification(
            org_id=org_id,
            title=f"[CRITICAL] {title}",
            body=body,
            user_id=user_id,
            channel="email" if user_id else "in_app",
            metadata=metadata or {},
        )
        logger.info("Critical alert dispatched asynchronously: %s", notification.id)
        return str(notification.id)
    except Exception as exc:
        logger.exception("Failed to dispatch critical alert")
        raise


@celery_app.task(
    name="app.tasks.notification_tasks.send_notification",
    queue="default",
)
def send_notification(
    org_id: str,
    title: str,
    body: str | None = None,
    user_id: str | None = None,
    channel: str = "in_app",
    metadata: dict | None = None,
) -> str:
    """
    Asynchronously create a standard user-facing notification.
    """
    try:
        notification = NotificationService.create_notification(
            org_id=org_id,
            title=title,
            body=body,
            user_id=user_id,
            channel=channel,
            metadata=metadata or {},
        )
        return str(notification.id)
    except Exception as exc:
        logger.exception("Failed to send notification")
        raise
