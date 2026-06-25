"""
EncryptionMetadata model — tracking details for encrypted secrets key rotation.
"""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDMixin


class EncryptionMetadata(Base, UUIDMixin, TimestampMixin):
    """Tracks metadata about keys used for encrypting credentials and sensitive fields."""

    __tablename__ = "encryption_metadata"

    key_id: Mapped[str] = mapped_column(String(255), nullable=False)
    algorithm: Mapped[str] = mapped_column(String(50), nullable=False, default="AES-GCM")
    rotation_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    last_rotated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    def __repr__(self) -> str:
        return f"<EncryptionMetadata key_id={self.key_id!r} algo={self.algorithm}>"
