"""
Auth middleware — global JWT verification and user status checks.
"""
from __future__ import annotations

import logging

from flask import abort, g, request
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request

logger = logging.getLogger(__name__)

EXEMPT_PATHS: list[str] = [
    "/api/v1/auth/login",
    "/api/v1/auth/refresh",
    "/api/v1/webhooks/whatsapp",
    "/api/v1/whatsapp/webhook",
]


def setup_auth_middleware(app) -> None:
    """Register auth verification hooks on the application."""

    @app.before_request
    def check_user_auth():
        # Exempt public endpoints
        if request.path in EXEMPT_PATHS or request.method == "OPTIONS":
            return

        # Attempt to verify JWT in request
        try:
            auth_header = request.headers.get("Authorization", "")
            if auth_header.startswith("Bearer "):
                # verify_jwt_in_request extracts and decodes JWT from headers
                jwt_data = verify_jwt_in_request(optional=True)
                if jwt_data:
                    from app.repositories.user_repo import UserRepository
                    user_id = get_jwt_identity()
                    if user_id:
                        user_repo = UserRepository()
                        user = user_repo.find_active_by_id(user_id)
                        if not user:
                            logger.warning("Authenticated user %s is inactive or deleted", user_id)
                            abort(403, description="User account is deactivated or deleted")
                        g.current_user = user
        except Exception as exc:
            logger.exception("Auth middleware check failed: %s", str(exc))
            abort(401, description="Invalid authentication credentials")
