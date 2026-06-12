"""
Celery Background Queue Tasks — async message processing & webhook dispatch.
"""
from __future__ import annotations

import asyncio
import logging

from app.tasks.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(
    name="app.tasks.queue_tasks.process_inbound_message_task",
    queue="ai",
    bind=True,
    max_retries=3,
    default_retry_delay=10,
)
def process_inbound_message_task(self, normalized_message: dict) -> None:
    """
    Run the AgentRouter orchestrator asynchronously inside Celery.

    This task is enqueued by the webhooks route whenever a valid inbound
    WhatsApp message is received.

    Args:
        normalized_message: Flat dict produced by ``WhatsAppService.normalize_inbound``.
    """
    from app.ai.orchestrator.router import AgentRouter

    router = AgentRouter()
    try:
        # Execute the async router wrapper in Celery's sync loop context
        asyncio.run(router.route(normalized_message))
    except Exception as exc:
        logger.exception(
            "Failed to process inbound message from %s",
            normalized_message.get("from", "unknown"),
        )
        raise self.retry(exc=exc)


@celery_app.task(
    name="app.tasks.queue_tasks.dispatch_endpoint_task",
    queue="workflows",
    bind=True,
    max_retries=2,
    default_retry_delay=5,
)
def dispatch_endpoint_task(
    self, org_id: str, endpoint_name: str, payload: dict
) -> dict:
    """
    Dispatch an external webhook call via the EndpointService.

    Args:
        org_id: Organization UUID string.
        endpoint_name: Logical name of the configured endpoint.
        payload: JSON-serialisable request body.

    Returns:
        Dispatch result dict from ``EndpointService.dispatch``.
    """
    from app.services.endpoint_service import EndpointService

    try:
        return EndpointService.dispatch(org_id, endpoint_name, payload)
    except Exception as exc:
        logger.exception(
            "Failed to dispatch endpoint '%s' for org %s", endpoint_name, org_id
        )
        raise self.retry(exc=exc)


@celery_app.task(
    name="app.tasks.queue_tasks.create_ticket_task",
    queue="default",
)
def create_ticket_task(
    org_id: str,
    title: str,
    description: str,
    priority: str = "medium",
    phone: str | None = None,
    name: str | None = None,
    conversation_id: str | None = None,
) -> str:
    """
    Create a support ticket in the background.

    Returns:
        The UUID string of the newly created ticket.
    """
    from app.services.ticket_service import TicketService

    ticket = TicketService.create_support_ticket(
        org_id=org_id,
        title=title,
        description=description,
        priority=priority,
        phone=phone,
        name=name,
        conversation_id=conversation_id,
    )
    return str(ticket.id)


@celery_app.task(
    name="app.tasks.queue_tasks.process_inbound_webhook_task",
    queue="default",
    bind=True,
    max_retries=3,
    default_retry_delay=5,
)
def process_inbound_webhook_task(self, payload: dict) -> None:
    """
    Process raw incoming WhatsApp webhook payload in background.
    """
    import asyncio
    from app.integrations.whatsapp.webhook_handler import WebhookHandler

    try:
        handler = WebhookHandler()
        asyncio.run(handler.dispatch(payload))
    except Exception as exc:
        logger.exception("Failed to process inbound webhook payload background task")
        raise self.retry(exc=exc)
