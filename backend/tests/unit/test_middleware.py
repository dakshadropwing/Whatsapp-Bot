"""
Unit tests for all backend middleware classes and functions.
"""
import pytest
from unittest.mock import MagicMock, patch
from flask import Flask, g, jsonify

from app.middleware.cors_middleware import setup_cors_middleware
from app.middleware.logging_middleware import setup_logging_middleware
from app.middleware.rate_limiter import setup_rate_limiter
from app.middleware.auth_middleware import setup_auth_middleware
from app.middleware.tenant_middleware import setup_tenant_middleware




# --- CORS Middleware Test ---

def test_cors_middleware(test_app):
    from app.core.config.settings import get_settings
    settings = get_settings()
    setup_cors_middleware(test_app)
    client = test_app.test_client()
    
    # Test preflight options check
    resp = client.options("/api/v1/resource")
    assert resp.status_code == 200
    assert resp.headers.get("Access-Control-Allow-Origin") in settings.CORS_ORIGINS


# --- Logging Middleware Test ---

def test_logging_middleware(test_app):
    setup_logging_middleware(test_app)
    client = test_app.test_client()

    with patch("app.middleware.logging_middleware.logger") as mock_logger:
        resp = client.get("/api/v1/auth/login")
        assert resp.status_code == 200
        mock_logger.info.assert_called_once()


# --- Rate Limiter Test ---

def test_rate_limiter(test_app):
    from app.core.config.settings import get_settings
    settings = get_settings()
    setup_rate_limiter(test_app)
    from app.extensions import limiter
    assert len(limiter._default_limits) == 2
    assert f"{settings.RATE_LIMIT_PER_MINUTE} per minute" in limiter._default_limits[0]
    assert limiter.storage_uri == "memory://"  # testing fallback


# --- Auth Middleware Test ---

def test_auth_middleware_exempt(test_app):
    setup_auth_middleware(test_app)
    client = test_app.test_client()
    
    # Exempt route should pass without check
    resp = client.get("/api/v1/auth/login")
    assert resp.status_code == 200


def test_auth_middleware_inactive_user(test_app):
    setup_auth_middleware(test_app)
    client = test_app.test_client()

    # If auth header is invalid bearer token, verify_jwt_in_request raises or aborts
    headers = {"Authorization": "Bearer invalid-token"}
    resp = client.get("/api/v1/resource", headers=headers)
    assert resp.status_code == 401


# --- Tenant Middleware Test ---

def test_tenant_middleware_exempt(test_app):
    setup_tenant_middleware(test_app)
    client = test_app.test_client()

    resp = client.get("/api/v1/auth/login")
    assert resp.status_code == 200


def test_tenant_middleware_header(test_app):
    setup_tenant_middleware(test_app)
    client = test_app.test_client()

    headers = {"X-Tenant-ID": "tenant-uuid-123"}
    resp = client.get("/api/v1/resource", headers=headers)
    assert resp.status_code == 200
    assert resp.json["org_id"] == "tenant-uuid-123"


def test_tenant_middleware_missing(test_app):
    setup_tenant_middleware(test_app)
    client = test_app.test_client()

    resp = client.get("/api/v1/resource")
    assert resp.status_code == 401
