"""
Authentication Service — JWT issuance, registration, password verification.
"""
from __future__ import annotations

import logging
from typing import Optional

from flask_jwt_extended import create_access_token, create_refresh_token
from sqlalchemy import select
from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db
from app.models.user import User

logger = logging.getLogger(__name__)


class AuthService:
    """Handles user authentication, password hashing, and JWT token creation."""

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a plaintext password using Werkzeug's PBKDF2."""
        return generate_password_hash(password)

    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        """Verify a plaintext password against a stored hash."""
        return check_password_hash(password_hash, password)

    @classmethod
    def authenticate_user(cls, email: str, password: str) -> Optional[dict]:
        """
        Authenticate a user by email + password.

        Returns:
            A dict with access_token, refresh_token, and user payload on success.
            None if credentials are invalid.
        """
        user = db.session.execute(
            select(User).where(User.email == email.strip().lower())
        ).scalar_one_or_none()

        if not user or not cls.verify_password(password, user.password_hash):
            return None

        if not user.is_active:
            logger.warning("Login attempt on deactivated account: %s", email)
            return None

        # Build JWT tokens with org + role claims
        identity = str(user.id)
        claims = {
            "org_id": str(user.organization_id),
            "role": str(user.role_id or ""),
        }

        access_token = create_access_token(
            identity=identity, additional_claims=claims
        )
        refresh_token = create_refresh_token(
            identity=identity, additional_claims=claims
        )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": {
                "id": str(user.id),
                "email": user.email,
                "username": user.username,
                "full_name": user.full_name,
                "organization_id": str(user.organization_id),
                "org_id": str(user.organization_id),
                "role": str(user.role_id or "member"),
            },
        }

    @classmethod
    def register_user(
        cls,
        email: str,
        username: str,
        full_name: str,
        password: str,
        organization_id: str,
        role_id: str | None = None,
    ) -> User:
        """
        Register a new platform user.

        Raises:
            ValueError: If a user with the given email already exists.
        """
        existing = db.session.execute(
            select(User).where(User.email == email.strip().lower())
        ).scalar_one_or_none()

        if existing:
            raise ValueError(f"User with email '{email}' already exists.")

        user = User(
            email=email.strip().lower(),
            username=username,
            full_name=full_name,
            password_hash=cls.hash_password(password),
            organization_id=organization_id,
            role_id=role_id,
        )
        db.session.add(user)
        db.session.commit()
        logger.info("Registered new user: %s (%s)", user.email, user.id)
        return user
