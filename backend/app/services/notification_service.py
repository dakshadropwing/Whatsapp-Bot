"""
Notification Service — create and manage in-app/email notifications.
"""
from __future__ import annotations

import logging
import uuid
from typing import Optional

from sqlalchemy import func, select

from app.extensions import db
from app.models.notification import Notification

logger = logging.getLogger(__name__)


class NotificationService:
    """Creates, queries, and marks notifications as read."""

    @staticmethod
    def create_notification(
        org_id: str,
        title: str,
        body: Optional[str] = None,
        user_id: Optional[str] = None,
        channel: str = "in_app",
        metadata: Optional[dict] = None,
    ) -> Notification:
        n = Notification(
            organization_id=uuid.UUID(org_id),
            title=title, body=body,
            user_id=uuid.UUID(user_id) if user_id else None,
            channel=channel, metadata_=metadata or {},
        )
        db.session.add(n)
        db.session.commit()
        logger.info("Created notification %s: %s", n.id, title)
        return n

    @staticmethod
    def list_notifications(
        org_id: str,
        user_id: Optional[str] = None,
        unread_only: bool = False,
        page: int = 1,
        per_page: int = 20,
    ) -> dict:
        query = select(Notification).where(Notification.organization_id == uuid.UUID(org_id))
        if user_id:
            query = query.where(Notification.user_id == uuid.UUID(user_id))
        if unread_only:
            query = query.where(Notification.is_read.is_(False))

        total = db.session.execute(select(func.count()).select_from(query.subquery())).scalar() or 0
        notifications = db.session.execute(
            query.order_by(Notification.created_at.desc()).offset((page - 1) * per_page).limit(per_page)
        ).scalars().all()

        return {
            "data": [
                {
                    "id": str(n.id), "title": n.title, "body": n.body,
                    "channel": n.channel, "is_read": n.is_read,
                    "created_at": n.created_at.isoformat() if n.created_at else None,
                }
                for n in notifications
            ],
            "total": total, "page": page, "per_page": per_page,
            "total_pages": (total + per_page - 1) // per_page,
        }

    @staticmethod
    def mark_read(notification_id: str) -> Optional[Notification]:
        n = db.session.get(Notification, uuid.UUID(notification_id))
        if not n:
            return None
        n.is_read = True
        db.session.commit()
        return n

    @staticmethod
    def mark_all_read(user_id: str) -> int:
        """Mark all notifications as read for a user. Returns count updated."""
        result = db.session.execute(
            select(Notification).where(
                Notification.user_id == uuid.UUID(user_id),
                Notification.is_read.is_(False),
            )
        ).scalars().all()
        for n in result:
            n.is_read = True
        db.session.commit()
        return len(result)

    @staticmethod
    def get_unread_count(user_id: str) -> int:
        return db.session.execute(
            select(func.count()).select_from(Notification).where(
                Notification.user_id == uuid.UUID(user_id),
                Notification.is_read.is_(False),
            )
        ).scalar() or 0
