"""Encryption Service."""
from __future__ import annotations

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import os
import base64
from app.core.config.settings import get_settings

class EncryptionService:
    """
    Symmetric AES-256-GCM encryption service to secure credential fields in PostgreSQL.
    """
    @staticmethod
    def _get_cipher() -> AESGCM:
        settings = get_settings()
        if not settings.ENCRYPTION_MASTER_KEY:
            raise ValueError("ENCRYPTION_MASTER_KEY is not configured in settings.")
        # Pad or slice master secret key to be exactly 32 bytes (256 bits)
        raw_key = settings.ENCRYPTION_MASTER_KEY.encode().rjust(32, b"0")[:32]
        return AESGCM(raw_key)

    @classmethod
    def encrypt(cls, plaintext: str) -> str:
        """Encrypt string, returning base64 string containing nonce + cipher."""
        if not plaintext:
            return ""
        cipher = cls._get_cipher()
        nonce = os.urandom(12)  # Standard 12-byte GCM nonce
        encrypted = cipher.encrypt(nonce, plaintext.encode(), None)
        return base64.b64encode(nonce + encrypted).decode()

    @classmethod
    def decrypt(cls, ciphertext: str) -> str:
        """Decrypt base64 string back to plaintext."""
        if not ciphertext:
            return ""
        cipher = cls._get_cipher()
        raw_data = base64.b64decode(ciphertext.encode())
        nonce = raw_data[:12]
        encrypted_payload = raw_data[12:]
        return cipher.decrypt(nonce, encrypted_payload, None).decode()
