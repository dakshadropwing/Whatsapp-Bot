"""
AuditLog Repository — immutable audit trail queries.
"""
from __future__ import annotations

from typing import Optional

from sqlalchemy import func, select

from app.extensions import db
from app.models.audit_log import AuditLog
from app.repositories.base_repository import BaseRepository


class AuditRepository(BaseRepository[AuditLog]):
    """Specialised repository for AuditLog queries (read-heavy, no updates)."""

    def __init__(self) -> None:
        super().__init__(AuditLog)

    def find_by_organization(
        self,
        org_id: str,
        action: Optional[str] = None,
        resource_type: Optional[str] = None,
        limit: int = 100,
    ) -> list[AuditLog]:
        """Return audit logs for an org with optional filters, newest first."""
        query = select(AuditLog).where(AuditLog.organization_id == org_id)
        if action:
            query = query.where(AuditLog.action == action)
        if resource_type:
            query = query.where(AuditLog.resource_type == resource_type)
        query = query.order_by(AuditLog.created_at.desc()).limit(limit)
        return db.session.execute(query).scalars().all()

    def find_by_user(self, user_id: str, limit: int = 100) -> list[AuditLog]:
        """Return audit logs triggered by a specific user."""
        return (
            db.session.execute(
                select(AuditLog)
                .where(AuditLog.user_id == user_id)
                .order_by(AuditLog.created_at.desc())
                .limit(limit)
            )
            .scalars()
            .all()
        )

    def find_by_resource(
        self, resource_type: str, resource_id: str
    ) -> list[AuditLog]:
        """Return all audit events for a specific resource."""
        return (
            db.session.execute(
                select(AuditLog)
                .where(
                    AuditLog.resource_type == resource_type,
                    AuditLog.resource_id == resource_id,
                )
                .order_by(AuditLog.created_at.desc())
            )
            .scalars()
            .all()
        )

    def count_by_organization(self, org_id: str) -> int:
        """Total audit log count for an org."""
        result = db.session.execute(
            select(func.count()).select_from(AuditLog).where(
                AuditLog.organization_id == org_id
            )
        ).scalar()
        return result or 0
