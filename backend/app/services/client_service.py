"""
Client Service — CRUD for external customer contacts.
"""
from __future__ import annotations

import logging
import uuid
from typing import Optional

from sqlalchemy import func, select

from app.extensions import db
from app.models.client import Client

logger = logging.getLogger(__name__)


class ClientService:
    """Manages external customer/client records for an organization."""

    @staticmethod
    def list_clients(
        org_id: str,
        page: int = 1,
        per_page: int = 20,
        search: Optional[str] = None,
    ) -> dict:
        query = select(Client).where(Client.organization_id == uuid.UUID(org_id))
        if search:
            term = f"%{search.lower()}%"
            query = query.where(
                db.or_(
                    func.lower(Client.name).like(term),
                    Client.phone.like(term),
                    func.lower(Client.email).like(term),
                )
            )
        total = db.session.execute(
            select(func.count()).select_from(query.subquery())
        ).scalar() or 0
        clients = (
            db.session.execute(query.order_by(Client.created_at.desc()).offset((page - 1) * per_page).limit(per_page))
            .scalars().all()
        )
        return {
            "data": [
                {
                    "id": str(c.id), "organization_id": str(c.organization_id),
                    "name": c.name, "email": c.email, "phone": c.phone,
                    "company": c.company, "tags": c.tags or [],
                    "created_at": c.created_at.isoformat() if c.created_at else None,
                    "updated_at": c.updated_at.isoformat() if c.updated_at else None,
                }
                for c in clients
            ],
            "total": total, "page": page, "per_page": per_page,
            "total_pages": (total + per_page - 1) // per_page,
        }

    @staticmethod
    def get_client(client_id: str) -> Optional[Client]:
        return db.session.get(Client, uuid.UUID(client_id))

    @staticmethod
    def create_client(org_id: str, **kwargs) -> Client:
        client = Client(organization_id=uuid.UUID(org_id), **kwargs)
        db.session.add(client)
        db.session.commit()
        logger.info("Created client %s (%s)", client.name, client.id)
        return client

    @staticmethod
    def update_client(client_id: str, **kwargs) -> Optional[Client]:
        client = db.session.get(Client, uuid.UUID(client_id))
        if not client:
            return None
        for key, value in kwargs.items():
            if hasattr(client, key) and key not in ("id", "organization_id"):
                setattr(client, key, value)
        db.session.commit()
        return client

    @staticmethod
    def delete_client(client_id: str) -> bool:
        client = db.session.get(Client, uuid.UUID(client_id))
        if not client:
            return False
        client.soft_delete()
        db.session.commit()
        return True

    @staticmethod
    def get_by_phone(org_id: str, phone: str) -> Optional[Client]:
        return db.session.execute(
            select(Client).where(
                Client.organization_id == uuid.UUID(org_id),
                Client.phone == phone,
            )
        ).scalar_one_or_none()
