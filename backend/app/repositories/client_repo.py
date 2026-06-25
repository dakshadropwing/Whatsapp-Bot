"""
Client Repository — external contact/customer queries.
"""
from __future__ import annotations

from typing import Optional

from sqlalchemy import select

from app.extensions import db
from app.models.client import Client
from app.repositories.base_repository import BaseRepository


class ClientRepository(BaseRepository[Client]):
    """Specialised repository for Client entity queries."""

    def __init__(self) -> None:
        super().__init__(Client)

    def find_by_organization(self, org_id: str) -> list[Client]:
        """Return all (non-deleted) clients for an organization, newest first."""
        return (
            db.session.execute(
                select(Client)
                .where(Client.organization_id == org_id, Client.deleted_at.is_(None))
                .order_by(Client.created_at.desc())
            )
            .scalars()
            .all()
        )

    def find_by_phone(self, org_id: str, phone: str) -> Optional[Client]:
        """Look up a client by org + phone number."""
        return db.session.execute(
            select(Client).where(
                Client.organization_id == org_id,
                Client.phone == phone,
                Client.deleted_at.is_(None),
            )
        ).scalar_one_or_none()

    def find_by_email(self, org_id: str, email: str) -> Optional[Client]:
        """Look up a client by org + email (case-insensitive)."""
        return db.session.execute(
            select(Client).where(
                Client.organization_id == org_id,
                Client.email == email.strip().lower(),
                Client.deleted_at.is_(None),
            )
        ).scalar_one_or_none()

    def search(self, org_id: str, term: str) -> list[Client]:
        """Search clients by name, email, phone, or company (ILIKE)."""
        pattern = f"%{term}%"
        return (
            db.session.execute(
                select(Client)
                .where(
                    Client.organization_id == org_id,
                    Client.deleted_at.is_(None),
                    (Client.name.ilike(pattern))
                    | (Client.email.ilike(pattern))
                    | (Client.phone.ilike(pattern))
                    | (Client.company.ilike(pattern)),
                )
                .order_by(Client.created_at.desc())
            )
            .scalars()
            .all()
        )

    def find_by_tag(self, org_id: str, tag: str) -> list[Client]:
        """Return clients that have a specific tag in their JSONB tags array."""
        return (
            db.session.execute(
                select(Client)
                .where(
                    Client.organization_id == org_id,
                    Client.deleted_at.is_(None),
                    Client.tags.contains([tag]),
                )
                .order_by(Client.created_at.desc())
            )
            .scalars()
            .all()
        )
