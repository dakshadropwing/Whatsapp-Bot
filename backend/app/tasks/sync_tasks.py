"""
Sync background tasks — synchronising external metadata and accounts.
"""
from __future__ import annotations

import logging

from app.tasks.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(
    name="app.tasks.sync_tasks.sync_external_data",
    queue="default",
)
def sync_external_data(org_id: str, resource_type: str) -> dict:
    """
    Sync account metadata or settings with WhatsApp Business APIs asynchronously.
    """
    logger.info("Syncing external data for org %s, resource: %s", org_id, resource_type)
    # Simulate synchronisation operations
    return {
        "status": "success",
        "organization_id": org_id,
        "resource_type": resource_type,
    }
