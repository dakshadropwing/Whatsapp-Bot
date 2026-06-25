"""
Media Service — handle media uploads, downloads, and URL management.
"""
from __future__ import annotations

import logging
import uuid
from typing import Optional

from app.extensions import db
from app.models.message import Message

logger = logging.getLogger(__name__)

# Supported media types and max sizes (bytes)
ALLOWED_TYPES = {
    "image": {"extensions": [".jpg", ".jpeg", ".png", ".gif", ".webp"], "max_size": 16 * 1024 * 1024},
    "audio": {"extensions": [".mp3", ".ogg", ".wav", ".m4a"], "max_size": 16 * 1024 * 1024},
    "video": {"extensions": [".mp4", ".mov", ".avi"], "max_size": 16 * 1024 * 1024},
    "document": {"extensions": [".pdf", ".doc", ".docx", ".xls", ".xlsx", ".csv", ".txt"], "max_size": 100 * 1024 * 1024},
}


class MediaService:
    """Handles media file validation and metadata storage for WhatsApp messages."""

    @staticmethod
    def validate_media(filename: str, file_size: int) -> tuple[bool, Optional[str]]:
        """Validate a media file against type and size constraints.
        Returns (is_valid, media_type_or_error).
        """
        ext = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
        for media_type, config in ALLOWED_TYPES.items():
            if ext in config["extensions"]:
                if file_size > config["max_size"]:
                    return False, f"File too large. Max {config['max_size'] // (1024*1024)}MB for {media_type}"
                return True, media_type
        return False, f"Unsupported file type: {ext}"

    @staticmethod
    def get_media_messages(conversation_id: str, media_type: Optional[str] = None) -> list[dict]:
        """Return media messages for a conversation."""
        from sqlalchemy import select
        query = select(Message).where(
            Message.conversation_id == uuid.UUID(conversation_id),
            Message.media_url.isnot(None),
        )
        if media_type:
            query = query.where(Message.media_type == media_type)
        messages = db.session.execute(query.order_by(Message.created_at.desc())).scalars().all()
        return [
            {
                "id": str(m.id), "media_url": m.media_url,
                "media_type": m.media_type, "media_size": m.media_size,
                "created_at": m.created_at.isoformat() if m.created_at else None,
            }
            for m in messages
        ]

    @staticmethod
    def get_storage_stats(org_id: str) -> dict:
        """Return media storage statistics for an organization."""
        from sqlalchemy import func, select
        total_size = db.session.execute(
            select(func.coalesce(func.sum(Message.media_size), 0)).where(
                Message.organization_id == uuid.UUID(org_id),
                Message.media_url.isnot(None),
            )
        ).scalar() or 0
        total_count = db.session.execute(
            select(func.count()).select_from(Message).where(
                Message.organization_id == uuid.UUID(org_id),
                Message.media_url.isnot(None),
            )
        ).scalar() or 0
        return {"total_size_bytes": total_size, "total_files": total_count}
