"""
AI background tasks — long-running LLM calls offloaded to Celery.
"""
from __future__ import annotations

import logging

from app.tasks.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(
    bind=True,
    queue="ai",
    max_retries=3,
    default_retry_delay=5,
    name="app.tasks.ai_tasks.process_ai_message",
)
def process_ai_message(self, conversation_id: str, message_id: str, message_body: str, agent_type: str = "support"):
    """
    Offload AI message processing to a background worker.
    Useful when the webhook must respond in < 5s.
    """
    import asyncio
    try:
        from app.ai.orchestrator.router import AgentRouter
        router = AgentRouter()
        normalized = {
            "from": conversation_id,
            "wa_id": conversation_id,
            "body": message_body,
            "type": "text",
            "wa_message_id": message_id,
        }
        asyncio.run(router.route(normalized))
    except Exception as exc:
        logger.exception(f"AI task failed for conversation {conversation_id}")
        raise self.retry(exc=exc)


@celery_app.task(
    queue="ai",
    name="app.tasks.ai_tasks.generate_embedding",
)
def generate_embedding(document_id: str, text: str, provider: str = "openai"):
    """Generate and store a vector embedding for a document chunk."""
    import asyncio
    try:
        from app.ai.providers.provider_factory import ProviderFactory
        provider_instance = ProviderFactory.get_provider(provider)
        embedding = asyncio.run(provider_instance.embed(text))
        logger.info(f"Generated embedding for document {document_id}: {len(embedding)} dims")
        # TODO: store in pgvector
        return {"document_id": document_id, "dimensions": len(embedding)}
    except Exception as exc:
        logger.exception(f"Embedding generation failed for {document_id}")
        raise
