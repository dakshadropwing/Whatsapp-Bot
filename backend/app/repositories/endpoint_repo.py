"""
EndpointConfig Repository — user-configured webhook endpoint queries.
"""
from __future__ import annotations

from typing import Optional

from sqlalchemy import select

from app.extensions import db
from app.models.endpoint_config import EndpointConfig
from app.repositories.base_repository import BaseRepository


class EndpointRepository(BaseRepository[EndpointConfig]):
    """Specialised repository for EndpointConfig entity queries."""

    def __init__(self) -> None:
        super().__init__(EndpointConfig)

    def find_by_organization(self, org_id: str) -> list[EndpointConfig]:
        """Return all endpoints for an organization, newest first."""
        return (
            db.session.execute(
                select(EndpointConfig)
                .where(EndpointConfig.organization_id == org_id)
                .order_by(EndpointConfig.created_at.desc())
            )
            .scalars()
            .all()
        )

    def find_active_by_organization(self, org_id: str) -> list[EndpointConfig]:
        """Return only active endpoints for an organization."""
        return (
            db.session.execute(
                select(EndpointConfig)
                .where(
                    EndpointConfig.organization_id == org_id,
                    EndpointConfig.is_active.is_(True),
                )
                .order_by(EndpointConfig.created_at.desc())
            )
            .scalars()
            .all()
        )

    def find_by_name(self, org_id: str, name: str) -> Optional[EndpointConfig]:
        """Look up an endpoint by org + name (unique constraint)."""
        return db.session.execute(
            select(EndpointConfig).where(
                EndpointConfig.organization_id == org_id,
                EndpointConfig.name == name,
            )
        ).scalar_one_or_none()

    def find_active_by_method(
        self, org_id: str, method: str
    ) -> list[EndpointConfig]:
        """Return active endpoints matching a specific HTTP method."""
        return (
            db.session.execute(
                select(EndpointConfig)
                .where(
                    EndpointConfig.organization_id == org_id,
                    EndpointConfig.is_active.is_(True),
                    EndpointConfig.method == method,
                )
                .order_by(EndpointConfig.created_at.desc())
            )
            .scalars()
            .all()
        )
