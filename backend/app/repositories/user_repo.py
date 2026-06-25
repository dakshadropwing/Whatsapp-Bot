"""
User Repository — query helpers for user accounts & authentication lookups.
"""
from __future__ import annotations

from typing import Optional

from sqlalchemy import select

from app.extensions import db
from app.models.user import User
from app.repositories.base_repository import BaseRepository


class UserRepository(BaseRepository[User]):
    """Specialised repository for User entity queries."""

    def __init__(self) -> None:
        super().__init__(User)

    def find_by_email(self, email: str) -> Optional[User]:
        """Look up a user by email address (case-insensitive)."""
        return db.session.execute(
            select(User).where(User.email == email.strip().lower())
        ).scalar_one_or_none()

    def find_by_organization(self, org_id: str) -> list[User]:
        """Return all active users belonging to a given organization."""
        return (
            db.session.execute(
                select(User)
                .where(User.organization_id == org_id, User.is_active.is_(True))
                .order_by(User.created_at.desc())
            )
            .scalars()
            .all()
        )

    def find_active_by_id(self, user_id: str) -> Optional[User]:
        """Fetch a user by PK only if the account is active."""
        return db.session.execute(
            select(User).where(User.id == user_id, User.is_active.is_(True))
        ).scalar_one_or_none()
