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
def generate_embedding(document_id: str, text: str, provider: str = "ollama"):
    """Generate and store a vector embedding for a document chunk."""
    import asyncio
    import uuid
    from app.extensions import db
    from app.models.embedding import DocumentChunk
    from app.models.document import Document
    try:
        from app.ai.providers.provider_factory import ProviderFactory
        provider_instance = ProviderFactory.get_provider(provider)
        embedding = asyncio.run(provider_instance.embed(text))
        logger.info(f"Generated embedding for document {document_id}: {len(embedding)} dims")
        
        doc_uuid = uuid.UUID(document_id)
        doc = db.session.get(Document, doc_uuid)
        if not doc:
            raise ValueError(f"Document {document_id} not found")
        
        chunk_index = db.session.query(db.func.count(DocumentChunk.id)).filter(DocumentChunk.document_id == doc_uuid).scalar() or 0
        chunk = DocumentChunk(
            document_id=doc_uuid,
            chunk_index=chunk_index,
            content=text,
            token_count=len(text.split()),
            embedding=embedding
        )
        db.session.add(chunk)
        
        doc.chunk_count = chunk_index + 1
        db.session.commit()
        
        return {
            "document_id": document_id,
            "chunk_id": str(chunk.id),
            "chunk_index": chunk_index,
            "dimensions": len(embedding)
        }
    except Exception as exc:
        logger.exception(f"Embedding generation failed for {document_id}")
        db.session.rollback()
        raise
