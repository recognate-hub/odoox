import pytest
import base64
from unittest.mock import patch
from cryptography.fernet import Fernet
from core.kms import KMSClient

@patch("core.kms.SecretsManager.get_active_key")
def test_get_kek_long(mock_get_key):
    long_key = base64.urlsafe_b64encode(b"a" * 32).decode('utf-8')
    mock_get_key.return_value = long_key
    assert KMSClient._get_kek() == long_key.encode('utf-8')

@patch("core.kms.SecretsManager.get_active_key")
def test_get_kek_short(mock_get_key):
    mock_get_key.return_value = "short"
    expected = base64.urlsafe_b64encode(b"short".ljust(32, b' '))
    assert KMSClient._get_kek() == expected

@patch("core.kms.KMSClient._get_kek")
def test_generate_data_key(mock_get_kek):
    kek = Fernet.generate_key()
    mock_get_kek.return_value = kek
    
    plaintext_dek, encrypted_dek = KMSClient.generate_data_key()
    
    assert len(plaintext_dek) == 44
    assert isinstance(encrypted_dek, str)
    
    # Verify it can be decrypted with the kek
    kek_cipher = Fernet(kek)
    assert kek_cipher.decrypt(encrypted_dek.encode('utf-8')) == plaintext_dek

@patch("core.kms.KMSClient._get_kek")
def test_decrypt_data_key(mock_get_kek):
    kek = Fernet.generate_key()
    mock_get_kek.return_value = kek
    
    kek_cipher = Fernet(kek)
    plaintext_dek = Fernet.generate_key()
    encrypted_dek = kek_cipher.encrypt(plaintext_dek).decode('utf-8')
    
    decrypted = KMSClient.decrypt_data_key(encrypted_dek)
    assert decrypted == plaintext_dek
