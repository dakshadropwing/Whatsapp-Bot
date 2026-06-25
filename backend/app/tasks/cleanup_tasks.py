"""
Cleanup background tasks — daily maintenance, expiring inactive sessions, key rotation logs.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import logging

from app.extensions import db
from app.models.ai_session import AISession
from app.models.encryption_metadata import EncryptionMetadata
from app.tasks.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(
    name="app.tasks.cleanup_tasks.cleanup_expired_ai_sessions",
    queue="default",
)
def cleanup_expired_ai_sessions() -> dict:
    """
    Expire AI sessions that have been inactive for more than 24 hours.
    Runs daily at 2 AM UTC.
    """
    try:
        now = datetime.now(timezone.utc)
        threshold = now - timedelta(hours=24)

        # Query all active sessions older than threshold
        expired_sessions = db.session.execute(
            db.select(AISession).where(
                AISession.status == "active",
                AISession.updated_at < threshold,
            )
        ).scalars().all()

        count = 0
        for session in expired_sessions:
            session.status = "expired"
            count += 1

        db.session.commit()
        logger.info("Successfully marked %d inactive AI sessions as expired", count)
        return {
            "status": "success",
            "expired_count": count,
        }
    except Exception as exc:
        logger.exception("Failed to clean up expired sessions")
        db.session.rollback()
        raise


@celery_app.task(
    name="app.tasks.cleanup_tasks.check_key_rotation",
    queue="default",
)
def check_key_rotation() -> dict:
    """
    Check if encryption keys need rotation (rotation period: 90 days).
    Runs daily at midnight.
    """
    try:
        now = datetime.now(timezone.utc)
        threshold = now - timedelta(days=90)

        # Retrieve last key rotation metadata
        latest_meta = db.session.execute(
            db.select(EncryptionMetadata).order_by(EncryptionMetadata.created_at.desc())
        ).scalars().first()

        rotation_required = False
        if not latest_meta:
            rotation_required = True
            logger.warning("No encryption metadata records found. Key initialization or rotation is required.")
        elif latest_meta.last_rotated_at and latest_meta.last_rotated_at < threshold:
            rotation_required = True
            logger.warning(
                "Current encryption key (key_id: %s) is older than 90 days (last rotated: %s). Rotation is recommended.",
                latest_meta.key_id,
                latest_meta.last_rotated_at,
            )
        else:
            logger.info("Encryption key is healthy (last rotated: %s)", latest_meta.last_rotated_at if latest_meta else "never")

        return {
            "status": "success",
            "rotation_recommended": rotation_required,
            "key_id": latest_meta.key_id if latest_meta else None,
        }
    except Exception as exc:
        logger.exception("Failed to run key rotation check")
        raise
