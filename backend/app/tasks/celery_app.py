"""
Celery application — task queue for background jobs.
"""
from __future__ import annotations

from celery import Celery
from celery.schedules import crontab

from app.core.config.settings import get_settings

settings = get_settings()

celery_app = Celery(
    "whatsapp_platform",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.tasks.ai_tasks",
        "app.tasks.workflow_tasks",
        "app.tasks.notification_tasks",
        "app.tasks.followup_tasks",
        "app.tasks.analytics_tasks",
        "app.tasks.cleanup_tasks",
        "app.tasks.sync_tasks",
    ],
)

celery_app.conf.update(
    # ── Serialization ─────────────────────────────────────────
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    # ── Timezone ──────────────────────────────────────────────
    timezone="UTC",
    enable_utc=True,
    # ── Task behavior ─────────────────────────────────────────
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    task_track_started=True,
    task_time_limit=300,          # 5 min hard limit
    task_soft_time_limit=240,     # 4 min soft limit
    worker_prefetch_multiplier=1,  # Fair distribution
    # ── Queues ───────────────────────────────────────────────
    task_default_queue="default",
    task_queues={
        "default":   {"exchange": "default",   "routing_key": "default"},
        "ai":        {"exchange": "ai",        "routing_key": "ai"},
        "workflows": {"exchange": "workflows", "routing_key": "workflows"},
        "critical":  {"exchange": "critical",  "routing_key": "critical"},
    },
    task_routes={
        "app.tasks.ai_tasks.*":       {"queue": "ai"},
        "app.tasks.workflow_tasks.*": {"queue": "workflows"},
        "app.tasks.notification_tasks.send_critical_*": {"queue": "critical"},
    },
    # ── Beat schedule (periodic tasks) ───────────────────────
    beat_schedule={
        "process-followups": {
            "task": "app.tasks.followup_tasks.process_due_followups",
            "schedule": crontab(minute="*/5"),  # Every 5 minutes
        },
        "cleanup-expired-sessions": {
            "task": "app.tasks.cleanup_tasks.cleanup_expired_ai_sessions",
            "schedule": crontab(hour="2", minute="0"),  # Daily at 2 AM UTC
        },
        "compute-daily-analytics": {
            "task": "app.tasks.analytics_tasks.compute_daily_metrics",
            "schedule": crontab(hour="1", minute="0"),  # Daily at 1 AM UTC
        },
        "rotate-encryption-keys": {
            "task": "app.tasks.cleanup_tasks.check_key_rotation",
            "schedule": crontab(hour="0", minute="0"),  # Daily at midnight
        },
    },
)
