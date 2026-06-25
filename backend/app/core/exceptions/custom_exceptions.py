"""
Custom API exceptions.
"""
from __future__ import annotations


class APIException(Exception):
    """Base API Exception."""
    status_code: int = 500
    message: str = "An internal error occurred."

    def __init__(self, message: str | None = None, status_code: int | None = None) -> None:
        super().__init__()
        if message:
            self.message = message
        if status_code is not None:
            self.status_code = status_code

    def to_dict(self) -> dict:
        return {"error": self.message}


class ValidationError(APIException):
    status_code = 400
    message = "Validation failed for input data."


class AuthenticationError(APIException):
    status_code = 401
    message = "Authentication credentials missing or invalid."


class PermissionDeniedError(APIException):
    status_code = 403
    message = "You do not have permission to perform this action."


class NotFoundError(APIException):
    status_code = 404
    message = "Requested resource not found."


class RateLimitExceededError(APIException):
    status_code = 429
    message = "Too many requests. Please try again later."
