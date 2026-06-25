"""
Document — a single uploaded file or URL ingested into a KnowledgeBase.

Raw text is stored here; the chunked + embedded pieces live in DocumentChunk.

Table: documents
"""
from __future__ import annotations

import enum
import uuid
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Enum, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db
from app.models.base import Base, TimestampMixin, UUIDMixin, SoftDeleteMixin

if TYPE_CHECKING:
    from app.models.knowledge_base import KnowledgeBase
    from app.models.embedding import DocumentChunk


class DocumentStatus(str, enum.Enum):
    PENDING  = "pending"    # uploaded, not yet indexed
    INDEXING = "indexing"   # chunking + embedding in progress
    INDEXED  = "indexed"    # ready for retrieval
    FAILED   = "failed"     # indexing errored out


class SourceType(str, enum.Enum):
    TEXT = "text"
    PDF  = "pdf"
    URL  = "url"
    CSV  = "csv"
    DOCX = "docx"


class Document(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    """
    A single knowledge document (text, PDF, URL, etc.) belonging to a KnowledgeBase.

    Lifecycle:
        PENDING  → Indexer picks it up
        INDEXING → Chunker + Embedder running
        INDEXED  → Chunks available for retrieval
        FAILED   → error_message has the reason
    """

    __tablename__ = "documents"

    # ── Ownership ─────────────────────────────────────────────
    knowledge_base_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("knowledge_bases.id", ondelete="CASCADE"),
        nullable=False,
    )

    # ── Identity ──────────────────────────────────────────────
    name: Mapped[str] = mapped_column(String(512), nullable=False)
    source_type: Mapped[str] = mapped_column(
        String(50), nullable=False, default=SourceType.TEXT
    )
    source_url: Mapped[str | None] = mapped_column(Text, nullable=True)

    # ── Content ───────────────────────────────────────────────
    raw_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    file_size_bytes: Mapped[int | None] = mapped_column(BigInteger, nullable=True)

    # ── Indexing State ────────────────────────────────────────
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default=DocumentStatus.PENDING
    )
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    chunk_count: Mapped[int] = mapped_column(
        # populated by Indexer after successful indexing
        __import__("sqlalchemy").Integer, nullable=False, default=0
    )

    # ── Extra Metadata (flexible) ─────────────────────────────
    doc_metadata: Mapped[dict] = mapped_column(
        "doc_metadata", JSONB, nullable=False, default=dict
    )

    # ── Relationships ─────────────────────────────────────────
    knowledge_base: Mapped["KnowledgeBase"] = relationship(
        "KnowledgeBase", back_populates="documents"
    )
    chunks: Mapped[list["DocumentChunk"]] = relationship(
        "DocumentChunk",
        back_populates="document",
        cascade="all, delete-orphan",
        lazy="dynamic",
    )

    # ── Indexes ───────────────────────────────────────────────
    __table_args__ = (
        Index("ix_doc_kb_id", "knowledge_base_id"),
        Index("ix_doc_status", "status"),
        Index("ix_doc_kb_status", "knowledge_base_id", "status"),
        Index("ix_doc_deleted_at", "deleted_at"),
    )

    def __repr__(self) -> str:
        return (
            f"<Document id={self.id} name={self.name!r} status={self.status}>"
        )
