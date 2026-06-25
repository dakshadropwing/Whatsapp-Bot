"""
VectorStore — pgvector-backed cosine similarity search for DocumentChunks.

All queries run through SQLAlchemy raw SQL so they:
    - Are transaction-safe (use the caller's session)
    - Work with Flask-SQLAlchemy's scoped sessions
    - Support pgvector's <=> cosine distance operator natively

Usage:
    store = VectorStore()
    results = store.search(db.session, query_vec, knowledge_base_id, top_k=5)
    store.upsert_chunk_embedding(db.session, chunk_id, embedding)
"""
from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass

from sqlalchemy import text
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


@dataclass
class SearchResult:
    """One ranked chunk returned by a vector similarity search."""
    chunk_id: uuid.UUID
    document_id: uuid.UUID
    document_name: str
    content: str
    chunk_index: int
    score: float       # cosine similarity [0..1], higher = more relevant


class VectorStore:
    """
    Wraps pgvector cosine-similarity ANN search for DocumentChunk embeddings.

    Relies on the pgvector extension being installed in PostgreSQL:
        CREATE EXTENSION IF NOT EXISTS vector;

    The ANN index (IVFFlat) should be created after the first data load:
        CREATE INDEX ix_chunk_emb_ivfflat
        ON document_chunks USING ivfflat (embedding vector_cosine_ops)
        WITH (lists = 100);
    """

    # ── Search ─────────────────────────────────────────────────────────────

    def search(
        self,
        db: Session,
        query_embedding: list[float],
        knowledge_base_id: uuid.UUID,
        top_k: int = 5,
        min_score: float = 0.50,
    ) -> list[SearchResult]:
        """
        Find the top_k chunks most similar to query_embedding within a KB.

        Args:
            db:                 active SQLAlchemy session
            query_embedding:    768-dim float list from Embedder.embed_one()
            knowledge_base_id:  only search chunks from this KB
            top_k:              maximum number of results to return
            min_score:          discard chunks with cosine similarity < this value

        Returns:
            list[SearchResult] sorted by score descending (best first)
        """
        # Format embedding as pgvector literal string: '[0.1,-0.2,...]'
        emb_str = self._fmt_embedding(query_embedding)

        sql = text("""
            SELECT
                dc.id             AS chunk_id,
                dc.document_id    AS document_id,
                dc.content        AS content,
                dc.chunk_index    AS chunk_index,
                d.name            AS document_name,
                -- pgvector <=> returns cosine *distance* (0=identical, 2=opposite)
                -- Convert to cosine *similarity*: 1 - distance
                (1.0 - (dc.embedding <=> CAST(:emb AS vector))) AS score
            FROM document_chunks dc
            JOIN documents d        ON d.id  = dc.document_id
            JOIN knowledge_bases kb ON kb.id = d.knowledge_base_id
            WHERE
                d.knowledge_base_id = :kb_id
                AND d.status        = 'indexed'
                AND d.deleted_at    IS NULL
                AND kb.is_active    = TRUE
                AND dc.embedding    IS NOT NULL
                -- Filter by minimum similarity in the WHERE clause for efficiency
                AND (1.0 - (dc.embedding <=> CAST(:emb AS vector))) >= :min_score
            ORDER BY
                dc.embedding <=> CAST(:emb AS vector)  -- ASC = closest first
            LIMIT :top_k
        """)

        rows = db.execute(sql, {
            "emb":      emb_str,
            "kb_id":    str(knowledge_base_id),
            "min_score": min_score,
            "top_k":    top_k,
        }).fetchall()

        results = [
            SearchResult(
                chunk_id=uuid.UUID(str(row.chunk_id)),
                document_id=uuid.UUID(str(row.document_id)),
                document_name=row.document_name,
                content=row.content,
                chunk_index=row.chunk_index,
                score=float(row.score),
            )
            for row in rows
        ]

        logger.debug(
            "VectorStore.search: kb=%s top_k=%d min_score=%.2f → returned=%d",
            knowledge_base_id, top_k, min_score, len(results),
        )
        return results

    # ── Write ──────────────────────────────────────────────────────────────

    def upsert_chunk_embedding(
        self,
        db: Session,
        chunk_id: uuid.UUID,
        embedding: list[float],
    ) -> None:
        """
        Write or overwrite the embedding vector for a single DocumentChunk.

        Args:
            db:        active SQLAlchemy session (caller must commit)
            chunk_id:  UUID of the DocumentChunk row
            embedding: 768-dim float list
        """
        emb_str = self._fmt_embedding(embedding)
        db.execute(
            text("""
                UPDATE document_chunks
                   SET embedding = CAST(:emb AS vector),
                       updated_at = NOW()
                 WHERE id = :chunk_id
            """),
            {"emb": emb_str, "chunk_id": str(chunk_id)},
        )
        db.flush()
        logger.debug("VectorStore.upsert: updated embedding for chunk=%s", chunk_id)

    def bulk_upsert_embeddings(
        self,
        db: Session,
        chunk_ids: list[uuid.UUID],
        embeddings: list[list[float]],
    ) -> None:
        """
        Write embeddings for multiple chunks at once (one UPDATE per row).

        Args:
            db:          active SQLAlchemy session
            chunk_ids:   list of DocumentChunk UUIDs (same order as embeddings)
            embeddings:  list of 768-dim float lists
        """
        if len(chunk_ids) != len(embeddings):
            raise ValueError(
                f"chunk_ids length ({len(chunk_ids)}) must match "
                f"embeddings length ({len(embeddings)})"
            )
        for chunk_id, embedding in zip(chunk_ids, embeddings):
            self.upsert_chunk_embedding(db, chunk_id, embedding)
        logger.debug(
            "VectorStore.bulk_upsert: wrote %d embeddings", len(chunk_ids)
        )

    # ── Utility ────────────────────────────────────────────────────────────

    @staticmethod
    def _fmt_embedding(embedding: list[float]) -> str:
        """Format a float list as a pgvector literal: '[0.1,-0.2,...]'"""
        return "[" + ",".join(f"{v:.8f}" for v in embedding) + "]"
