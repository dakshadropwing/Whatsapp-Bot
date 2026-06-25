"""
Analytics background tasks — compiling daily usage stats and metrics.
"""
from __future__ import annotations

import logging

from app.extensions import db
from app.models.organization import Organization
from app.services.analytics_service import AnalyticsService
from app.tasks.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(
    name="app.tasks.analytics_tasks.compute_daily_metrics",
    queue="default",
)
def compute_daily_metrics() -> dict:
    """
    Compute daily KPI analytics for all active organizations.
    Run periodically (typically daily at 1 AM).
    """
    try:
        # Fetch all active organizations
        orgs = db.session.execute(
            db.select(Organization).where(Organization.is_active.is_(True))
        ).scalars().all()

        logger.info("Starting daily metrics computation for %d orgs", len(orgs))
        processed = 0

        for org in orgs:
            # Compiling statistics logs
            stats = AnalyticsService.get_stats(str(org.id))
            logger.info("Successfully computed daily stats for org %s: %s", org.id, stats)
            processed += 1

        return {
            "status": "success",
            "organizations_processed": processed,
        }
    except Exception as exc:
        logger.exception("Failed to compute daily metrics")
        raise
