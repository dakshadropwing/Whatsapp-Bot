"""
PromptTemplate model — reusable prompt templates for AI agents.
"""
from __future__ import annotations

import uuid

from sqlalchemy import ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDMixin


class PromptTemplate(Base, UUIDMixin, TimestampMixin):
    """A versioned prompt template that agents can reference."""

    __tablename__ = "prompt_templates"

    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False, default="general")
    system_prompt: Mapped[str | None] = mapped_column(Text, nullable=True)
    user_prompt: Mapped[str] = mapped_column(Text, nullable=False)
    variables: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    is_active: Mapped[bool] = mapped_column(nullable=False, default=True)

    __table_args__ = (
        Index("ix_prompt_templates_org_category", "organization_id", "category"),
        Index("ix_prompt_templates_org_name", "organization_id", "name", unique=True),
    )

    def __repr__(self) -> str:
        return f"<PromptTemplate id={self.id} name={self.name!r}>"
