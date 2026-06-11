"""
User Service — CRUD management for platform users.
"""
from __future__ import annotations

import logging
import uuid
from typing import Optional

from sqlalchemy import func, select
from werkzeug.security import generate_password_hash

from app.extensions import db
from app.models.user import User

logger = logging.getLogger(__name__)


class UserService:
    """Manages platform user accounts — listing, creation, updates, deactivation."""

    @staticmethod
    def list_users(
        org_id: str,
        page: int = 1,
        per_page: int = 20,
        search: Optional[str] = None,
    ) -> dict:
        """Return a paginated list of users for an organization."""
        query = select(User).where(User.organization_id == uuid.UUID(org_id))

        if search:
            term = f"%{search.lower()}%"
            query = query.where(
                db.or_(
                    func.lower(User.full_name).like(term),
                    func.lower(User.email).like(term),
                )
            )

        total = db.session.execute(
            select(func.count()).select_from(query.subquery())
        ).scalar() or 0

        users = (
            db.session.execute(
                query.order_by(User.created_at.desc())
                .offset((page - 1) * per_page)
                .limit(per_page)
            )
            .scalars()
            .all()
        )

        return {
            "data": [
                {
                    "id": str(u.id),
                    "email": u.email,
                    "username": u.username,
                    "full_name": u.full_name,
                    "role_id": str(u.role_id) if u.role_id else None,
                    "is_active": u.is_active,
                    "last_login_at": u.last_login_at,
                    "created_at": u.created_at.isoformat() if u.created_at else None,
                }
                for u in users
            ],
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": (total + per_page - 1) // per_page,
        }

    @staticmethod
    def get_user(user_id: str) -> Optional[User]:
        """Fetch a single user by ID."""
        return db.session.get(User, uuid.UUID(user_id))

    @classmethod
    def create_user(
        cls,
        org_id: str,
        email: str,
        username: str,
        full_name: str,
        password: str,
        role_id: Optional[str] = None,
    ) -> User:
        """Create a new platform user."""
        existing = db.session.execute(
            select(User).where(User.email == email.strip().lower())
        ).scalar_one_or_none()
        if existing:
            raise ValueError(f"User with email '{email}' already exists.")

        user = User(
            email=email.strip().lower(),
            username=username,
            full_name=full_name,
            password_hash=generate_password_hash(password),
            organization_id=uuid.UUID(org_id),
            role_id=uuid.UUID(role_id) if role_id else None,
        )
        db.session.add(user)
        db.session.commit()
        logger.info("Created user %s (%s)", user.email, user.id)
        return user

    @staticmethod
    def update_user(user_id: str, **kwargs) -> Optional[User]:
        """Update user fields."""
        user = db.session.get(User, uuid.UUID(user_id))
        if not user:
            return None
        for key, value in kwargs.items():
            if hasattr(user, key) and key not in ("id", "password_hash", "organization_id"):
                setattr(user, key, value)
        db.session.commit()
        logger.info("Updated user %s", user.id)
        return user

    @staticmethod
    def deactivate_user(user_id: str) -> Optional[User]:
        """Soft-deactivate a user (set is_active=False)."""
        user = db.session.get(User, uuid.UUID(user_id))
        if not user:
            return None
        user.is_active = False
        db.session.commit()
        logger.info("Deactivated user %s", user.id)
        return user

    @staticmethod
    def reset_password(user_id: str, new_password: str) -> Optional[User]:
        """Reset a user's password."""
        user = db.session.get(User, uuid.UUID(user_id))
        if not user:
            return None
        user.password_hash = generate_password_hash(new_password)
        db.session.commit()
        logger.info("Password reset for user %s", user.id)
        return user
