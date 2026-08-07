import pytest
from fastapi.testclient import TestClient
from main import app
from unittest.mock import patch

client = TestClient(app)

def test_health():
    with patch("routers.health.get_settings") as mock_settings:
        mock_settings.return_value.ANTHROPIC_API_KEY = "test"
        response = client.get("/health")
        assert response.status_code != 404

def test_admin_api_auth_me():
    response = client.get("/api/auth/me")
    assert response.status_code in [200, 401, 307]

def test_oauth_authorize():
    response = client.get("/oauth/authorize")
    assert response.status_code in [200, 401, 307, 400, 422]

def test_oauth_protected_resource():
    response = client.get("/.well-known/oauth-protected-resource")
    assert response.status_code in [200, 401, 307, 400]

def test_oauth_auth_server():
    response = client.get("/.well-known/oauth-authorization-server")
    assert response.status_code in [200, 401, 307, 400]
