"""
Audit Service — immutable logging of platform actions.
"""
from __future__ import annotations

import logging
import uuid
from typing import Optional

from sqlalchemy import func, select

from app.extensions import db
from app.models.audit_log import AuditLog

logger = logging.getLogger(__name__)


class AuditService:
    """Records and queries audit trail entries for compliance."""

    @staticmethod
    def log_action(
        org_id: str,
        action: str,
        resource_type: str,
        resource_id: Optional[str] = None,
        user_id: Optional[str] = None,
        details: Optional[dict] = None,
        ip_address: Optional[str] = None,
    ) -> AuditLog:
        """Create an immutable audit log entry."""
        entry = AuditLog(
            organization_id=uuid.UUID(org_id),
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            user_id=uuid.UUID(user_id) if user_id else None,
            details=details or {},
            ip_address=ip_address,
        )
        db.session.add(entry)
        db.session.commit()
        return entry

    @staticmethod
    def list_logs(
        org_id: str,
        page: int = 1,
        per_page: int = 50,
        action: Optional[str] = None,
        resource_type: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> dict:
        """Return paginated audit logs with optional filters."""
        query = select(AuditLog).where(AuditLog.organization_id == uuid.UUID(org_id))
        if action:
            query = query.where(AuditLog.action == action)
        if resource_type:
            query = query.where(AuditLog.resource_type == resource_type)
        if user_id:
            query = query.where(AuditLog.user_id == uuid.UUID(user_id))

        total = db.session.execute(select(func.count()).select_from(query.subquery())).scalar() or 0
        logs = db.session.execute(
            query.order_by(AuditLog.created_at.desc()).offset((page - 1) * per_page).limit(per_page)
        ).scalars().all()

        return {
            "data": [
                {
                    "id": str(l.id), "organization_id": str(l.organization_id),
                    "user_id": str(l.user_id) if l.user_id else None,
                    "action": l.action, "resource_type": l.resource_type,
                    "resource_id": l.resource_id, "details": l.details,
                    "ip_address": l.ip_address,
                    "created_at": l.created_at.isoformat() if l.created_at else None,
                }
                for l in logs
            ],
            "total": total, "page": page, "per_page": per_page,
            "total_pages": (total + per_page - 1) // per_page,
        }

    @staticmethod
    def get_log(log_id: str) -> Optional[AuditLog]:
        return db.session.get(AuditLog, uuid.UUID(log_id))
