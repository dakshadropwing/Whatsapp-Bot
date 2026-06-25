"""
Workflow Service — CRUD for automated workflow definitions.
"""
from __future__ import annotations

import logging
import uuid
from typing import Optional

from sqlalchemy import func, select

from app.extensions import db
from app.models.workflow import Workflow

logger = logging.getLogger(__name__)


class WorkflowService:
    """Manages workflow definitions — creation, toggle, step editing."""

    @staticmethod
    def list_workflows(org_id: str, page: int = 1, per_page: int = 20) -> dict:
        query = select(Workflow).where(Workflow.organization_id == uuid.UUID(org_id))
        total = db.session.execute(select(func.count()).select_from(query.subquery())).scalar() or 0
        workflows = db.session.execute(
            query.order_by(Workflow.created_at.desc()).offset((page - 1) * per_page).limit(per_page)
        ).scalars().all()
        return {
            "data": [
                {
                    "id": str(w.id), "name": w.name, "description": w.description,
                    "trigger": w.trigger, "steps": w.steps or [],
                    "is_active": w.is_active, "organization_id": str(w.organization_id),
                    "run_count": w.run_count, "last_run_at": w.last_run_at,
                    "created_at": w.created_at.isoformat() if w.created_at else None,
                }
                for w in workflows
            ],
            "total": total, "page": page, "per_page": per_page,
            "total_pages": (total + per_page - 1) // per_page,
        }

    @staticmethod
    def get_workflow(workflow_id: str) -> Optional[Workflow]:
        return db.session.get(Workflow, uuid.UUID(workflow_id))

    @staticmethod
    def create_workflow(org_id: str, **kwargs) -> Workflow:
        wf = Workflow(organization_id=uuid.UUID(org_id), **kwargs)
        db.session.add(wf)
        db.session.commit()
        logger.info("Created workflow %s (%s)", wf.name, wf.id)
        return wf

    @staticmethod
    def update_workflow(workflow_id: str, **kwargs) -> Optional[Workflow]:
        wf = db.session.get(Workflow, uuid.UUID(workflow_id))
        if not wf:
            return None
        for key, value in kwargs.items():
            if hasattr(wf, key) and key not in ("id", "organization_id"):
                setattr(wf, key, value)
        db.session.commit()
        return wf

    @staticmethod
    def toggle_workflow(workflow_id: str) -> Optional[Workflow]:
        wf = db.session.get(Workflow, uuid.UUID(workflow_id))
        if not wf:
            return None
        wf.is_active = not wf.is_active
        db.session.commit()
        logger.info("Toggled workflow %s → %s", wf.name, wf.is_active)
        return wf

    @staticmethod
    def delete_workflow(workflow_id: str) -> bool:
        wf = db.session.get(Workflow, uuid.UUID(workflow_id))
        if not wf:
            return False
        wf.soft_delete()
        db.session.commit()
        return True
