"""
Global exception and error handlers for Flask routes.
"""
from __future__ import annotations

import logging

from flask import jsonify
from werkzeug.exceptions import HTTPException

from app.core.exceptions.custom_exceptions import APIException

logger = logging.getLogger(__name__)


def register_error_handlers(app) -> None:
    """Register error handler decorators on *app*."""

    @app.errorhandler(APIException)
    def handle_api_exception(error: APIException):
        logger.warning("APIException: %s (Status: %d)", error.message, error.status_code)
        return jsonify(error.to_dict()), error.status_code

    @app.errorhandler(HTTPException)
    def handle_http_exception(error: HTTPException):
        logger.warning("HTTPException: %s (Status: %d)", error.description, error.code)
        return jsonify({"error": error.description or "HTTP Error"}), error.code or 500

    @app.errorhandler(Exception)
    def handle_generic_exception(error: Exception):
        logger.exception("Unexpected system error: %s", str(error))
        return jsonify({"error": "An unexpected server error occurred."}), 500
