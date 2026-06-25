"""
API Key generation and validation helpers.
"""
from __future__ import annotations

import hashlib
import secrets


def generate_api_key(prefix: str = "waba_") -> tuple[str, str]:
    """
    Generate a secure API key and its SHA-256 hash.

    Returns:
        tuple[str, str]: (raw_api_key, hashed_api_key)
    """
    token = secrets.token_urlsafe(32)
    raw_key = f"{prefix}{token}"
    hashed_key = hash_api_key(raw_key)
    return raw_key, hashed_key


def hash_api_key(key: str) -> str:
    """Hash the API key using SHA-256."""
    return hashlib.sha256(key.encode()).hexdigest()


def verify_api_key(raw_key: str, hashed_key: str) -> bool:
    """Verify that a raw API key matches its hash securely."""
    return secrets.compare_digest(hash_api_key(raw_key), hashed_key)
