"""
Indexer — document ingestion pipeline.

Flow:
    Document (raw_text set, status=PENDING)
        → Chunker.chunk()         → list[Chunk]
        → Embedder.embed_batch()  → list[list[float]]
        → DocumentChunk rows written to PostgreSQL
        → document.status = INDEXED

This class is designed to be called from:
    - A Celery background task (most common)
    - A Flask route handler (for small documents)
    - A standalone CLI script

Usage:
    indexer = Indexer()
    n_chunks = await indexer.index_document(db_session, document)

Re-indexing:
    Calling index_document() on an already-indexed Document deletes all
    existing chunks and re-creates them from the current raw_text.
"""
from __future__ import annotations

import logging
import uuid
from typing import Optional

from sqlalchemy.orm import Session

from app.ai.rag.chunker import Chunker
from app.ai.embeddings.embedder import Embedder
from app.models.document import Document, DocumentStatus
from app.models.embedding import DocumentChunk

logger = logging.getLogger(__name__)


class Indexer:
    """
    Orchestrates the full document → chunk → embed → persist pipeline.

    Args:
        chunk_size:      tokens per chunk (default: 512)
        chunk_overlap:   overlap tokens between chunks (default: 64)
        embed_batch_size: concurrent embed calls per batch (default: 20)
        provider_type:   override AI provider ("gemini" | "ollama" | None)
    """

    def __init__(
        self,
        chunk_size: int = 512,
        chunk_overlap: int = 64,
        embed_batch_size: int = 20,
        provider_type: Optional[str] = None,
    ) -> None:
        self._chunker = Chunker(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )
        self._embedder = Embedder(provider_type=provider_type)
        self._embed_batch_size = embed_batch_size

    # ── Main entry point ───────────────────────────────────────────────────

    async def index_document(
        self,
        db: Session,
        document: Document,
    ) -> int:
        """
        Index a single Document: chunk it, embed the chunks, save to DB.

        Preconditions:
            - document.raw_text is populated
            - document is attached to an active db session

        Args:
            db:       active SQLAlchemy session (method will flush + commit)
            document: Document ORM instance

        Returns:
            Number of chunks created and indexed

        Raises:
            ValueError: if document has no raw_text
            Exception:  any embedding API error (document is marked FAILED)
        """
        logger.info(
            "Indexer: starting document=%s (%s, %d chars)",
            document.id,
            document.name,
            len(document.raw_text or ""),
        )

        # ── Step 0: Mark as in-progress ────────────────────────────────────
        document.status = DocumentStatus.INDEXING
        document.error_message = None
        db.add(document)
        db.flush()

        try:
            return await self._run_pipeline(db, document)

        except Exception as exc:
            # Roll back chunk writes but keep document row so we can record error
            db.rollback()
            logger.error(
                "Indexer: ❌ failed for document=%s: %s", document.id, exc,
                exc_info=True,
            )
            # Re-open a fresh write to persist the failure status
            document.status = DocumentStatus.FAILED
            document.error_message = str(exc)[:2000]   # cap to column size
            db.add(document)
            db.commit()
            raise

    # ── Internal pipeline ──────────────────────────────────────────────────

    async def _run_pipeline(self, db: Session, document: Document) -> int:
        raw_text = document.raw_text or ""
        if not raw_text.strip():
            raise ValueError(
                f"Document {document.id!r} ({document.name!r}) has no raw_text to index."
            )

        # ── Step 1: Chunk ──────────────────────────────────────────────────
        chunks = self._chunker.chunk(
            raw_text,
            metadata={
                "document_id":   str(document.id),
                "document_name": document.name,
                "source_type":   document.source_type,
            },
        )
        if not chunks:
            raise ValueError(
                f"Chunker returned 0 chunks for document {document.id!r}. "
                "Check that raw_text is non-empty."
            )
        logger.info(
            "Indexer: %d chunks produced for document=%s",
            len(chunks), document.id,
        )

        # ── Step 2: Delete existing chunks (supports re-indexing) ──────────
        deleted = (
            db.query(DocumentChunk)
            .filter(DocumentChunk.document_id == document.id)
            .delete(synchronize_session=False)
        )
        if deleted:
            logger.debug(
                "Indexer: deleted %d stale chunks for document=%s",
                deleted, document.id,
            )
        db.flush()

        # ── Step 3: Insert chunk rows (without embeddings yet) ─────────────
        chunk_objs: list[DocumentChunk] = []
        for ch in chunks:
            obj = DocumentChunk(
                id=uuid.uuid4(),
                document_id=document.id,
                chunk_index=ch.index,
                content=ch.content,
                token_count=ch.token_count,
                embedding=None,
            )
            db.add(obj)
            chunk_objs.append(obj)
        db.flush()   # assign DB-side defaults (created_at, etc.)

        # ── Step 4: Generate embeddings ────────────────────────────────────
        texts = [ch.content for ch in chunks]
        embeddings = await self._embedder.embed_batch(
            texts,
            batch_size=self._embed_batch_size,
        )

        # ── Step 5: Write embeddings to chunk rows ─────────────────────────
        from app.ai.embeddings.vector_store import VectorStore
        store = VectorStore()
        for obj, embedding in zip(chunk_objs, embeddings):
            store.upsert_chunk_embedding(db, obj.id, embedding)

        # ── Step 6: Update document status ────────────────────────────────
        document.status      = DocumentStatus.INDEXED
        document.chunk_count = len(chunk_objs)
        document.error_message = None
        db.add(document)
        db.commit()

        logger.info(
            "Indexer: ✅ document=%s indexed — %d chunks",
            document.id, len(chunk_objs),
        )
        return len(chunk_objs)

    # ── Convenience: index by ID ───────────────────────────────────────────

    async def index_by_id(
        self,
        db: Session,
        document_id: uuid.UUID,
    ) -> int:
        """
        Load a Document by ID and index it.

        Raises:
            LookupError: if document_id is not found
        """
        doc = db.query(Document).filter_by(id=document_id).first()
        if not doc:
            raise LookupError(f"Document {document_id} not found")
        return await self.index_document(db, doc)
