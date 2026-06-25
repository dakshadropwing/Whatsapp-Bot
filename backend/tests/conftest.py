import pytest
from flask import Flask, jsonify, g
import uuid
from flask_jwt_extended import create_access_token
from unittest.mock import MagicMock, patch
from app.core.config.settings import Settings

@pytest.fixture
def test_app():
    app = Flask("test_middleware_app")
    app.config["TESTING"] = True
    app.config["JWT_SECRET_KEY"] = "super-secret"
    app.config["CORS_ORIGINS"] = ["*"]
    app.config["RATE_LIMIT_PER_MINUTE"] = 60
    app.config["RATE_LIMIT_PER_HOUR"] = 3600
    app.config["REDIS_URL"] = "redis://localhost:6379/0"

    # Setup dummy routes
    @app.route("/api/v1/auth/login")
    def login():
        return jsonify({"status": "exempt"})

    @app.route("/api/v1/resource")
    def resource():
        return jsonify({
            "org_id": str(g.get("org_id")),
            "user": str(g.get("current_user")) if g.get("current_user") else None
        })

    return app


class ApiTestSettings(Settings):
    TESTING: bool = True
    SQLALCHEMY_DATABASE_URI: str = "sqlite://"
    JWT_SECRET_KEY: str = "test-secret-key"
    WHATSAPP_ACCESS_TOKEN: str = "fake-token"
    WHATSAPP_PHONE_NUMBER_ID: str = "fake-phone"
    WHATSAPP_API_VERSION: str = "v18.0"
    WHATSAPP_API_BASE_URL: str = "https://graph.facebook.com"
    WHATSAPP_WEBHOOK_VERIFY_TOKEN: str = "verify-token"
    APP_SECRET_KEY: str = "app-secret"


@pytest.fixture
def real_app():
    from app.factory import create_app
    settings = ApiTestSettings()
    app = create_app(settings)
    return app


@pytest.fixture
def test_org_id():
    return "00000000-0000-0000-0000-000000000001"


@pytest.fixture
def test_token(real_app, test_org_id):
    with real_app.app_context():
        return create_access_token(
            identity="test-user",
            additional_claims={"org_id": test_org_id, "role": "admin"}
        )


@pytest.fixture
def test_headers(test_token):
    return {"Authorization": f"Bearer {test_token}"}


@pytest.fixture
def mock_db_session():
    with patch("app.extensions.db.session") as mock_session:
        yield mock_session
