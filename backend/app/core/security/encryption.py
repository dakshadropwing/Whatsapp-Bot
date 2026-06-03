"""
AES-256-GCM encryption utilities using Python cryptography (OpenSSL backend).

Usage:
    enc = EncryptionService()
    ciphertext = enc.encrypt("sensitive data")
    plaintext  = enc.decrypt(ciphertext)
"""
from __future__ import annotations

import base64
import os
import struct
from typing import Optional

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from app.core.config.settings import get_settings


class EncryptionService:
    """
    Symmetric encryption using AES-256-GCM (authenticated encryption).
    All ciphertext is base64url-encoded and self-contained
    (includes nonce + salt + version byte).

    Wire format (base64url of):
        [1 byte version] [12 bytes nonce] [32 bytes salt] [ciphertext + 16 byte tag]
    """

    VERSION = b"\x01"
    NONCE_SIZE = 12   # GCM standard
    SALT_SIZE = 32
    KEY_SIZE = 32     # AES-256
    ITERATIONS = 200_000

    def __init__(self) -> None:
        settings = get_settings()
        self._master_key = bytes.fromhex(settings.ENCRYPTION_MASTER_KEY)

    def _derive_key(self, salt: bytes) -> bytes:
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=self.KEY_SIZE,
            salt=salt,
            iterations=self.ITERATIONS,
        )
        return kdf.derive(self._master_key)

    def encrypt(self, plaintext: str) -> str:
        """Encrypt a plaintext string. Returns a base64url-safe token."""
        nonce = os.urandom(self.NONCE_SIZE)
        salt = os.urandom(self.SALT_SIZE)
        key = self._derive_key(salt)
        aesgcm = AESGCM(key)
        ciphertext = aesgcm.encrypt(nonce, plaintext.encode("utf-8"), None)
        raw = self.VERSION + nonce + salt + ciphertext
        return base64.urlsafe_b64encode(raw).decode("ascii")

    def decrypt(self, token: str) -> str:
        """Decrypt a base64url token. Returns the original plaintext."""
        raw = base64.urlsafe_b64decode(token.encode("ascii"))
        version = raw[:1]
        if version != self.VERSION:
            raise ValueError(f"Unsupported encryption version: {version!r}")
        nonce = raw[1:1 + self.NONCE_SIZE]
        salt = raw[1 + self.NONCE_SIZE:1 + self.NONCE_SIZE + self.SALT_SIZE]
        ciphertext = raw[1 + self.NONCE_SIZE + self.SALT_SIZE:]
        key = self._derive_key(salt)
        aesgcm = AESGCM(key)
        plaintext = aesgcm.decrypt(nonce, ciphertext, None)
        return plaintext.decode("utf-8")

    def encrypt_field(self, value: Optional[str]) -> Optional[str]:
        """Encrypt a nullable database field."""
        if value is None:
            return None
        return self.encrypt(value)

    def decrypt_field(self, token: Optional[str]) -> Optional[str]:
        """Decrypt a nullable database field."""
        if token is None:
            return None
        return self.decrypt(token)
