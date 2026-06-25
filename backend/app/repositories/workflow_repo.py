"""
Workflow Repository — automation workflow definition queries.
"""
from __future__ import annotations

from typing import Optional

from sqlalchemy import select

from app.extensions import db
from app.models.workflow import Workflow
from app.repositories.base_repository import BaseRepository


class WorkflowRepository(BaseRepository[Workflow]):
    """Specialised repository for Workflow entity queries."""

    def __init__(self) -> None:
        super().__init__(Workflow)

    def find_by_organization(self, org_id: str) -> list[Workflow]:
        """Return all workflows for an organization, newest first."""
        return (
            db.session.execute(
                select(Workflow)
                .where(
                    Workflow.organization_id == org_id,
                    Workflow.deleted_at.is_(None),
                )
                .order_by(Workflow.created_at.desc())
            )
            .scalars()
            .all()
        )

    def find_active_by_organization(self, org_id: str) -> list[Workflow]:
        """Return only active workflows for an organization."""
        return (
            db.session.execute(
                select(Workflow)
                .where(
                    Workflow.organization_id == org_id,
                    Workflow.is_active.is_(True),
                    Workflow.deleted_at.is_(None),
                )
                .order_by(Workflow.created_at.desc())
            )
            .scalars()
            .all()
        )

    def find_by_trigger(self, org_id: str, trigger: str) -> list[Workflow]:
        """Return active workflows matching a specific trigger type."""
        return (
            db.session.execute(
                select(Workflow)
                .where(
                    Workflow.organization_id == org_id,
                    Workflow.trigger == trigger,
                    Workflow.is_active.is_(True),
                    Workflow.deleted_at.is_(None),
                )
                .order_by(Workflow.created_at.desc())
            )
            .scalars()
            .all()
        )

    def find_by_name(self, org_id: str, name: str) -> Optional[Workflow]:
        """Look up a workflow by org + name."""
        return db.session.execute(
            select(Workflow).where(
                Workflow.organization_id == org_id,
                Workflow.name == name,
                Workflow.deleted_at.is_(None),
            )
        ).scalar_one_or_none()
