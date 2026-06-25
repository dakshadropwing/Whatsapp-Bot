"""
FollowUp background tasks — checking waiting threads and prompting action/reminders.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import logging

from app.extensions import db
from app.models.conversation import Conversation, ConversationStatus
from app.tasks.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(
    name="app.tasks.followup_tasks.process_due_followups",
    queue="default",
)
def process_due_followups() -> dict:
    """
    Check conversations waiting on customer replies for too long (e.g., 24 hours).
    Auto-resolve or escalate if necessary. Runs every 5 minutes.
    """
    try:
        now = datetime.now(timezone.utc)
        threshold = now - timedelta(hours=24)

        # Retrieve conversations waiting on customers for over 24h
        due_convs = db.session.execute(
            db.select(Conversation).where(
                Conversation.status == ConversationStatus.WAITING,
                Conversation.updated_at < threshold,
            )
        ).scalars().all()

        processed = 0
        for conv in due_convs:
            # Escalate status to active to prompt bot or agent to follow up
            conv.status = ConversationStatus.ACTIVE
            conv.priority = "high"
            processed += 1

        db.session.commit()
        logger.info("Processed %d due follow-ups; status escalated to active", processed)
        return {
            "status": "success",
            "followups_triggered": processed,
        }
    except Exception as exc:
        logger.exception("Failed to process due follow-ups")
        db.session.rollback()
        raise
