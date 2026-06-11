"""
Tenant scope middleware — automatically scopes DB queries by organization.

Extracts org_id from JWT claims or the X-Tenant-ID header and stores it
on Flask's ``g`` context so downstream services can filter by tenant.
"""
from __future__ import annotations

import logging

from flask import abort, g, request

logger = logging.getLogger(__name__)

# Routes that do NOT require a tenant context (public endpoints).
EXEMPT_PATHS: list[str] = [
    "/api/v1/auth/login",
    "/api/v1/auth/refresh",
    "/api/v1/webhooks/whatsapp",
]


def setup_tenant_middleware(app) -> None:
    """Register the tenant-scoping ``before_request`` hook on *app*."""

    @app.before_request
    def scope_tenant():
        # Step 1: Default — no tenant
        g.org_id = None

        # Step 2: Try to extract org_id from JWT in the Authorization header.
        # We decode manually because @jwt_required() hasn't run yet at this point.
        try:
            from flask_jwt_extended import decode_token

            auth_header = request.headers.get("Authorization", "")
            if auth_header.startswith("Bearer "):
                token = auth_header[7:]
                decoded = decode_token(token)
                org_id = decoded.get("org_id") or decoded.get("additional_claims", {}).get("org_id")
                if org_id:
                    g.org_id = org_id
                    return
        except Exception:
            # No valid JWT — fall through to header check
            pass

        # Step 3: Check the X-Tenant-ID header (useful for webhooks / API keys)
        tenant_id = request.headers.get("X-Tenant-ID")
        if tenant_id:
            g.org_id = tenant_id
            return

        # Step 4: Exempt public routes
        if request.path in EXEMPT_PATHS or request.method == "OPTIONS":
            return

        # Step 5: No tenant context found — reject
        logger.warning(
            "Tenant context missing for %s %s", request.method, request.path
        )
        abort(401, description="Tenant context missing or unauthorized")
