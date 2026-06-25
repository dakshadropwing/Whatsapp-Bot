"""
AgentConfig model — granular configuration parameters for specific AI agents.
"""
from __future__ import annotations

import uuid

from sqlalchemy import ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDMixin


class AgentConfig(Base, UUIDMixin, TimestampMixin):
    """Detailed configurations and setting parameters for AI Agents."""

    __tablename__ = "agent_configs"

    agent_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("ai_agents.id", ondelete="CASCADE"),
        nullable=False,
    )
    config_key: Mapped[str] = mapped_column(String(255), nullable=False)
    config_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    value_type: Mapped[str] = mapped_column(String(50), nullable=False, default="string")

    __table_args__ = (
        Index("ix_agent_configs_agent_key", "agent_id", "config_key", unique=True),
    )

    def __repr__(self) -> str:
        return f"<AgentConfig agent_id={self.agent_id} key={self.config_key!r}>"
