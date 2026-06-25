"""
DocumentChunk — one chunk of a Document, with its pgvector embedding.

Uses pgvector's Vector type for cosine-similarity search directly in PostgreSQL.
No separate vector database needed (Pinecone, Weaviate, etc.).

Table: document_chunks

Prerequisites:
    PostgreSQL extension:  CREATE EXTENSION IF NOT EXISTS vector;
    Python package:        pip install pgvector  (already in requirements.txt)
"""
from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Index, Integer, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

try:
    from pgvector.sqlalchemy import Vector
    _VECTOR_AVAILABLE = True
except ImportError:
    # Graceful degradation: if pgvector is not installed, store as Text
    # and raise a clear error at query time.
    Vector = None
    _VECTOR_AVAILABLE = False

from app.extensions import db
from app.models.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.document import Document


# Must match the output dimension of the embedding model used.
# text-embedding-004 (Gemini) → 768 dimensions.
EMBEDDING_DIM = 768


def _get_vector_col():
    """Return the correct column type for the embedding field."""
    if _VECTOR_AVAILABLE:
        return mapped_column(Vector(EMBEDDING_DIM), nullable=True)
    # Fallback: store as plain text (not searchable via pgvector, but won't crash)
    return mapped_column(Text, nullable=True)


class DocumentChunk(Base, UUIDMixin, TimestampMixin):
    """
    A single text chunk derived from a Document, stored with its embedding vector.

    The `embedding` column uses pgvector's `vector` type, enabling:
        - Cosine similarity:   embedding <=> query_vector
        - L2 distance:         embedding <-> query_vector
        - Inner product:       embedding <#> query_vector

    ANN index (create AFTER loading data):
        CREATE INDEX ix_chunk_emb_ivfflat
        ON document_chunks USING ivfflat (embedding vector_cosine_ops)
        WITH (lists = 100);
    """

    __tablename__ = "document_chunks"

    # ── Ownership ─────────────────────────────────────────────
    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
    )

    # ── Content ───────────────────────────────────────────────
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    token_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # ── Embedding vector (pgvector) ───────────────────────────
    if _VECTOR_AVAILABLE:
        embedding: Mapped[list[float] | None] = mapped_column(
            Vector(EMBEDDING_DIM), nullable=True
        )
    else:
        embedding: Mapped[str | None] = mapped_column(Text, nullable=True)

    # ── Relationships ─────────────────────────────────────────
    document: Mapped["Document"] = relationship(
        "Document", back_populates="chunks"
    )

    # ── Indexes ───────────────────────────────────────────────
    __table_args__ = (
        Index("ix_chunk_doc_id", "document_id"),
        Index("ix_chunk_doc_idx", "document_id", "chunk_index"),
        # NOTE: IVFFlat ANN index is created separately after data load.
        # See: migrations/versions/xxxx_add_ivfflat_index.py
    )

    def __repr__(self) -> str:
        return (
            f"<DocumentChunk id={self.id} "
            f"doc={self.document_id} idx={self.chunk_index}>"
        )
