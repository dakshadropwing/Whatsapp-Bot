"""
Unit tests for backend core features (config, security, cache, logging, exceptions).
"""
import pytest
from unittest.mock import MagicMock, patch
import logging

from app.core.config.constants import TICKET_STATUS_OPEN
from app.core.security.api_keys import generate_api_key, verify_api_key
from app.core.security.jwt import create_user_tokens
from app.core.security.oauth import exchange_meta_token
from app.core.security.pii import mask_pii
from app.core.cache.cache_manager import generate_cache_key
from app.core.logging.formatters import StructuredFormatter
from app.core.logging.handlers import CeleryNotificationLogHandler
from app.core.exceptions.custom_exceptions import ValidationError, APIException
from app.core.exceptions.handlers import register_error_handlers


# --- Constants Test ---

def test_constants():
    assert TICKET_STATUS_OPEN == "OPEN"


# --- API Key Test ---

def test_api_keys():
    raw_key, hashed_key = generate_api_key(prefix="test_")
    assert raw_key.startswith("test_")
    assert verify_api_key(raw_key, hashed_key) is True
    assert verify_api_key("wrong-key", hashed_key) is False


# --- JWT Helper Test ---

def test_jwt_helpers(test_app):
    from flask_jwt_extended import JWTManager
    JWTManager(test_app)
    with test_app.app_context():
        tokens = create_user_tokens("user-123", "org-456", "admin")
        assert "access_token" in tokens
        assert "refresh_token" in tokens


# --- OAuth Test ---

def test_oauth():
    with patch("requests.get") as mock_get:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"access_token": "meta-tok"}
        mock_get.return_value = mock_resp

        res = exchange_meta_token("code-123", "https://redirect")
        assert res == {"access_token": "meta-tok"}


# --- PII Masking Test ---

def test_pii_masking():
    text = "My email is test@example.com and phone is 123-456-7890."
    masked = mask_pii(text)
    assert "test@example.com" not in masked
    assert "123-456-7890" not in masked
    assert "[REDACTED_EMAIL]" in masked
    assert "[REDACTED_PHONE]" in masked


# --- Cache Key Test ---

def test_cache_keys():
    key = generate_cache_key("users", "123", active=True)
    assert key == "users:123:active=True"


# --- Log Formatting Test ---

def test_log_formatter():
    formatter = StructuredFormatter(use_colors=False)
    record = logging.LogRecord(
        name="test_logger",
        level=logging.INFO,
        pathname="test.py",
        lineno=10,
        msg="log message example",
        args=(),
        exc_info=None
    )
    formatted = formatter.format(record)
    assert "INFO" in formatted
    assert "log message example" in formatted


# --- Logging Handler Test ---

def test_celery_log_handler():
    handler = CeleryNotificationLogHandler()
    record = logging.LogRecord(
        name="test_logger",
        level=logging.ERROR,
        pathname="test.py",
        lineno=10,
        msg="error log",
        args=(),
        exc_info=None
    )
    with patch("app.tasks.notification_tasks.send_critical_alert.delay") as mock_delay:
        handler.emit(record)
        mock_delay.assert_called_once()


# --- Custom Exception Test ---

def test_custom_exceptions():
    exc = ValidationError("Invalid fields detected")
    assert exc.status_code == 400
    assert exc.to_dict() == {"error": "Invalid fields detected"}
