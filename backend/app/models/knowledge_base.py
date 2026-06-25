"""
KnowledgeBase — a named collection of documents (e.g. "Product FAQs", "HR Policy").
Each organisation can have multiple knowledge bases.

Table: knowledge_bases
"""
from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db
from app.models.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.document import Document


class KnowledgeBase(Base, UUIDMixin, TimestampMixin):
    """
    A scoped collection of documents for one organisation.

    One org → many KnowledgeBases (e.g. "Support FAQ", "Sales Playbook").
    Each KnowledgeBase → many Documents.
    """

    __tablename__ = "knowledge_bases"

    # ── Tenant ───────────────────────────────────────────────
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
    )

    # ── Identity ─────────────────────────────────────────────
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # ── Status ───────────────────────────────────────────────
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    # ── Relationships ────────────────────────────────────────
    documents: Mapped[list["Document"]] = relationship(
        "Document",
        back_populates="knowledge_base",
        cascade="all, delete-orphan",
        lazy="dynamic",
    )

    # ── Indexes ───────────────────────────────────────────────
    __table_args__ = (
        Index("ix_kb_org_id", "organization_id"),
        Index("ix_kb_org_name", "organization_id", "name", unique=True),
        Index("ix_kb_is_active", "is_active"),
    )

    def __repr__(self) -> str:
        return f"<KnowledgeBase id={self.id} name={self.name!r}>"
