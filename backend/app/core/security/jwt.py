"""
JWT helper functions for token creation and claims configuration.
"""
from __future__ import annotations

from datetime import timedelta

from flask_jwt_extended import create_access_token, create_refresh_token


def create_user_tokens(user_id: str, org_id: str, role: str | None = None) -> dict[str, str]:
    """
    Generate access and refresh tokens with custom claims (org_id, role).
    """
    additional_claims = {
        "org_id": org_id,
        "role": role or "user",
    }

    # 1 hour access token, 30 days refresh token
    access = create_access_token(
        identity=user_id,
        additional_claims=additional_claims,
        expires_delta=timedelta(hours=1),
    )
    refresh = create_refresh_token(
        identity=user_id,
        additional_claims=additional_claims,
        expires_delta=timedelta(days=30),
    )
    return {
        "access_token": access,
        "refresh_token": refresh,
    }
