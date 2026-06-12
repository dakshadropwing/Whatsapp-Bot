"""
Application Factory — creates and configures the Flask app.
"""
from __future__ import annotations

import os
from typing import Optional

from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_migrate import Migrate

from app.core.config.settings import Settings, get_settings
from app.core.logging.logger import configure_logging
from app.core.exceptions.handlers import register_error_handlers
from app.core.events.startup import register_startup_events
from app.core.events.shutdown import register_shutdown_events
from app.extensions import db, migrate, jwt, limiter, cache


def create_app(settings: Optional[Settings] = None) -> Flask:
    """
    Application factory pattern.

    Args:
        settings: Optional Settings override (useful for testing).

    Returns:
        Configured Flask application instance.
    """
    if settings is None:
        settings = get_settings()

    app = Flask(__name__)
    app.config.from_object(settings)
    app.url_map.strict_slashes = False

    # ── Logging ──────────────────────────────────────────────
    configure_logging(settings)

    # ── Extensions ───────────────────────────────────────────
    _register_extensions(app, settings)

    # ── CORS ─────────────────────────────────────────────────
    from app.middleware.cors_middleware import setup_cors_middleware
    setup_cors_middleware(app)

    # ── Blueprints ───────────────────────────────────────────
    _register_blueprints(app)

    # ── Error Handlers ───────────────────────────────────────
    register_error_handlers(app)

    # ── Middleware ─────────────────────────────────────────────
    from app.middleware.logging_middleware import setup_logging_middleware
    from app.middleware.rate_limiter import setup_rate_limiter
    from app.middleware.auth_middleware import setup_auth_middleware
    from app.middleware.tenant_middleware import setup_tenant_middleware

    setup_logging_middleware(app)
    setup_rate_limiter(app)
    setup_auth_middleware(app)
    setup_tenant_middleware(app)

    # ── App Events ───────────────────────────────────────────
    register_startup_events(app)
    register_shutdown_events(app)

    return app


def _register_extensions(app: Flask, settings: Settings) -> None:
    """Bind Flask extensions to the app."""
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    limiter.init_app(app)
    cache.init_app(app)


def _register_blueprints(app: Flask) -> None:
    """Register all API blueprints."""
    from app.api.v1.auth.routes import auth_bp
    from app.api.v1.whatsapp.routes import whatsapp_bp
    from app.api.v1.conversations.routes import conversations_bp
    from app.api.v1.messages.routes import messages_bp
    from app.api.v1.agents.routes import agents_bp
    from app.api.v1.workflows.routes import workflows_bp
    from app.api.v1.tickets.routes import tickets_bp
    from app.api.v1.clients.routes import clients_bp
    from app.api.v1.employees.routes import employees_bp
    from app.api.v1.users.routes import users_bp
    from app.api.v1.knowledge_base.routes import kb_bp
    from app.api.v1.analytics.routes import analytics_bp
    from app.api.v1.settings.routes import settings_bp
    from app.api.v1.webhooks.routes import webhooks_bp
    from app.api.v1.endpoints.routes import endpoints_bp
    from app.api.v1.prompts.routes import prompts_bp
    from app.api.v1.audit.routes import audit_bp

    API_PREFIX = "/api/v1"

    blueprints = [
        (auth_bp,          f"{API_PREFIX}/auth"),
        (whatsapp_bp,      f"{API_PREFIX}/whatsapp"),
        (conversations_bp, f"{API_PREFIX}/conversations"),
        (messages_bp,      f"{API_PREFIX}/messages"),
        (agents_bp,        f"{API_PREFIX}/agents"),
        (workflows_bp,     f"{API_PREFIX}/workflows"),
        (tickets_bp,       f"{API_PREFIX}/tickets"),
        (clients_bp,       f"{API_PREFIX}/clients"),
        (employees_bp,     f"{API_PREFIX}/employees"),
        (users_bp,         f"{API_PREFIX}/users"),
        (kb_bp,            f"{API_PREFIX}/knowledge-base"),
        (analytics_bp,     f"{API_PREFIX}/analytics"),
        (settings_bp,      f"{API_PREFIX}/settings"),
        (webhooks_bp,      f"{API_PREFIX}/webhooks"),
        (endpoints_bp,     f"{API_PREFIX}/endpoints"),
        (prompts_bp,       f"{API_PREFIX}/prompts"),
        (audit_bp,         f"{API_PREFIX}/audit"),
    ]

    for blueprint, url_prefix in blueprints:
        app.register_blueprint(blueprint, url_prefix=url_prefix)
