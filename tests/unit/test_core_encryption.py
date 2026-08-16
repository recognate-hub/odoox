from unittest.mock import patch

from cryptography.fernet import Fernet

from core.encryption import _get_active_fernet, _get_retired_fernets, decrypt, encrypt


def test_encrypt_empty():
    assert encrypt("") == ""
    assert encrypt(None) is None

@patch("core.encryption.KMSClient.generate_data_key")
def test_encrypt_success(mock_generate):
    plaintext_dek = Fernet.generate_key()
    mock_generate.return_value = (plaintext_dek, "encrypted_dek_str")
    
    result = encrypt("my_secret")
    assert result.startswith("ENVELOPE_V1:encrypted_dek_str:")
    
    # Extract ciphertext
    ciphertext = result.split(":", 2)[2]
    cipher = Fernet(plaintext_dek)
    assert cipher.decrypt(ciphertext.encode()).decode() == "my_secret"

def test_decrypt_empty():
    assert decrypt("") == ""
    assert decrypt(None) is None

@patch("core.encryption.KMSClient.decrypt_data_key")
def test_decrypt_envelope_success(mock_decrypt):
    plaintext_dek = Fernet.generate_key()
    mock_decrypt.return_value = plaintext_dek
    
    cipher = Fernet(plaintext_dek)
    ciphertext = cipher.encrypt(b"my_secret").decode()
    token = f"ENVELOPE_V1:encrypted_dek_str:{ciphertext}"
    
    assert decrypt(token) == "my_secret"
    mock_decrypt.assert_called_once_with("encrypted_dek_str")

@patch("core.encryption.KMSClient.decrypt_data_key")
def test_decrypt_envelope_failure(mock_decrypt):
    mock_decrypt.side_effect = Exception("Decryption failed")
    token = "ENVELOPE_V1:enc:cipher"
    assert decrypt(token) == token

@patch("core.encryption.SecretsManager.get_active_key")
def test_get_active_fernet_short_key(mock_get_key):
    mock_get_key.return_value = "short"
    fernet = _get_active_fernet()
    assert fernet is not None

@patch("core.encryption.SecretsManager.get_retired_keys")
def test_get_retired_fernets_invalid_key(mock_get_keys):
    mock_get_keys.return_value = ["invalid_key_that_raises_exception"]
    fernets = _get_retired_fernets()
    assert len(fernets) == 0

@patch("core.encryption._get_active_fernet")
@patch("core.encryption._get_retired_fernets")
def test_decrypt_backwards_compatibility_active_key(mock_retired, mock_active):
    key = Fernet.generate_key()
    cipher = Fernet(key)
    ciphertext = cipher.encrypt(b"my_secret").decode()
    
    mock_active.return_value = cipher
    mock_retired.return_value = []
    
    assert decrypt(ciphertext) == "my_secret"

@patch("core.encryption._get_active_fernet")
@patch("core.encryption._get_retired_fernets")
def test_decrypt_backwards_compatibility_retired_key(mock_retired, mock_active):
    key_active = Fernet.generate_key()
    cipher_active = Fernet(key_active)
    
    key_retired = Fernet.generate_key()
    cipher_retired = Fernet(key_retired)
    ciphertext = cipher_retired.encrypt(b"my_secret").decode()
    
    mock_active.return_value = cipher_active
    mock_retired.return_value = [cipher_retired]
    
    assert decrypt(ciphertext) == "my_secret"

@patch("core.encryption._get_active_fernet")
@patch("core.encryption._get_retired_fernets")
def test_decrypt_backwards_compatibility_failure(mock_retired, mock_active):
    key_active = Fernet.generate_key()
    cipher_active = Fernet(key_active)
    
    # A valid looking Fernet token that fails decryption with the given key
    key_other = Fernet.generate_key()
    ciphertext = Fernet(key_other).encrypt(b"my_secret").decode()
    
    mock_active.return_value = cipher_active
    mock_retired.return_value = []
    
    # Should fallback to returning the original token
    assert decrypt(ciphertext) == ciphertext

def test_decrypt_fallback_unknown_format():
    token = "some_unknown_token_format"
    assert decrypt(token) == token
