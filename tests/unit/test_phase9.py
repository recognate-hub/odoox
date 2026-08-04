import pytest
import os
import ssl
from unittest.mock import patch

from config.settings import get_settings
from core.secrets import SecretsManager
from odoo.xmlrpc import TimeoutSafeTransport
from core.encryption import _get_active_fernet, _get_retired_fernets

def test_secrets_manager():
    # Test that secrets manager fetches the key correctly
    settings = get_settings()
    settings.ENCRYPTION_KEY = "dummy_active_key_123456789012345"
    settings.OLD_ENCRYPTION_KEYS = "dummy_retired_key_123456789012345"
    
    with patch("core.secrets.get_settings", return_value=settings):
        assert SecretsManager.get_active_key() == "dummy_active_key_123456789012345"
        assert SecretsManager.get_retired_keys() == ["dummy_retired_key_123456789012345"]

def test_encryption_uses_secrets_manager():
    # Mock secrets manager and test encryption wrapper
    import base64
    valid_key = base64.urlsafe_b64encode(b"12345678901234567890123456789012").decode()
    with patch("core.secrets.SecretsManager.get_active_key", return_value=valid_key):
        active = _get_active_fernet()
        assert active is not None
        
    with patch("core.secrets.SecretsManager.get_retired_keys", return_value=[valid_key]):
        retired = _get_retired_fernets()
        assert len(retired) == 1

def test_timeout_safe_transport_mtls_fallback():
    # Without certs, it should just initialize normally
    transport = TimeoutSafeTransport(timeout=5)
    assert transport.timeout == 5
    
def test_timeout_safe_transport_mtls_loading(tmp_path):
    cert_path = tmp_path / "cert.pem"
    key_path = tmp_path / "key.pem"
    cert_path.write_text("mock cert")
    key_path.write_text("mock key")
    
    settings = get_settings()
    settings.ODOO_CLIENT_CERT_PATH = str(cert_path)
    settings.ODOO_CLIENT_KEY_PATH = str(key_path)
    
    # It will fail to load mock certs because they aren't real X509, 
    # but we can patch ssl.SSLContext.load_cert_chain to verify it gets called
    with patch("odoo.xmlrpc.get_settings", return_value=settings):
        with patch("ssl.SSLContext.load_cert_chain") as mock_load:
            transport = TimeoutSafeTransport(timeout=5)
            mock_load.assert_called_once_with(certfile=str(cert_path), keyfile=str(key_path))
