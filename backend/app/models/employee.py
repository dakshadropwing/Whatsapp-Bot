"""
Employee model — internal team members (distinct from platform Users).
"""
from __future__ import annotations

import uuid

from sqlalchemy import ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDMixin


class Employee(Base, UUIDMixin, TimestampMixin):
    """An internal team member (agent, manager) belonging to an organization."""

    __tablename__ = "employees"

    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(320), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    department: Mapped[str | None] = mapped_column(String(100), nullable=True)
    role: Mapped[str] = mapped_column(String(50), nullable=False, default="agent")
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="online")

    __table_args__ = (
        Index("ix_employees_org_department", "organization_id", "department"),
        Index("ix_employees_org_email", "organization_id", "email", unique=True),
    )

    def __repr__(self) -> str:
        return f"<Employee id={self.id} name={self.name!r}>"
