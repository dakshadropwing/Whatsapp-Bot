"""
Unit tests for Backend Phase 1 (Database Repository & Encryption Service).
"""
import pytest
from unittest.mock import MagicMock, patch
from app.repositories.base_repository import BaseRepository
from app.services.encryption_service import EncryptionService


def test_base_repository_operations():
    """Verify CRUD mappings function correctly on SQLAlchemy models."""
    mock_model = MagicMock()
    repo = BaseRepository(mock_model)
    
    # Assert instantiation properties
    assert repo.model == mock_model

    # Mock DB interactions
    with patch("app.extensions.db.session") as mock_session:
        # 1. Create
        repo.create(name="test_item")
        mock_session.add.assert_called_once()
        
        # 2. Get
        repo.get(1)
        mock_session.get.assert_called_with(mock_model, 1)

        # 3. Delete
        dummy_instance = MagicMock()
        repo.delete(dummy_instance)
        mock_session.delete.assert_called_with(dummy_instance)

        # 4. Save
        repo.save()
        mock_session.commit.assert_called_once()


def test_encryption_loops():
    """Verify encryption and decryption loops preserve integrity."""
    plaintext = "super-secret-whatsapp-access-token"
    
    # Test encryption and decryption loops
    ciphertext = EncryptionService.encrypt(plaintext)
    assert ciphertext != plaintext
    assert len(ciphertext) > 0

    decrypted = EncryptionService.decrypt(ciphertext)
    assert decrypted == plaintext


def test_encrypted_text_decorator():
    """Verify EncryptedText TypeDecorator binds and processes parameters correctly."""
    from app.models.whatsapp_account import EncryptedText
    decorator = EncryptedText()
    
    plaintext = "access-token-123"
    
    # Bind (encrypt)
    encrypted = decorator.process_bind_param(plaintext, None)
    assert encrypted != plaintext
    assert encrypted is not None
    
    # Result (decrypt)
    decrypted = decorator.process_result_value(encrypted, None)
    assert decrypted == plaintext
    
    # Test None handling
    assert decorator.process_bind_param(None, None) is None
    assert decorator.process_result_value(None, None) is None
