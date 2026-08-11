import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from main import app
import time
import json
from core.encryption import encrypt

client = TestClient(app)

def test_authorize_redirect_login():
    response = client.get("/oauth/authorize?client_id=1&redirect_uri=http://l", follow_redirects=False)
    # The redirect status may be 303 (direct) or 307 (via proxy — TestClient follows one hop)
    assert response.status_code in (303, 307)
    assert "/login" in response.headers["location"]

def test_authorize_success():
    response = client.get("/oauth/authorize?client_id=1&redirect_uri=http://l", cookies={"access_token": "acc"}, follow_redirects=False)
    assert response.status_code == 303
    assert "code=" in response.headers["location"]

def test_authorize_success_with_state():
    response = client.get("/oauth/authorize?client_id=1&redirect_uri=http://l&state=xyz", cookies={"access_token": "acc"}, follow_redirects=False)
    assert response.status_code == 303
    assert "state=xyz" in response.headers["location"]

def test_token_unsupported_grant():
    response = client.post("/oauth/token", data={"grant_type": "password"})
    assert response.status_code == 400
    assert response.json()["error"] == "unsupported_grant_type"

def test_token_no_code():
    response = client.post("/oauth/token", data={"grant_type": "authorization_code"})
    assert response.status_code == 400
    assert response.json()["error"] == "invalid_request"

def test_token_auth_code_success():
    payload = {
        "access_token": "acc",
        "refresh_token": "ref",
        "exp": time.time() + 300
    }
    code = encrypt(json.dumps(payload))
    response = client.post("/oauth/token", data={"grant_type": "authorization_code", "code": code})
    assert response.status_code == 200
    assert response.json()["access_token"] == "acc"

def test_token_auth_code_expired():
    payload = {
        "access_token": "acc",
        "refresh_token": "ref",
        "exp": time.time() - 300
    }
    code = encrypt(json.dumps(payload))
    response = client.post("/oauth/token", data={"grant_type": "authorization_code", "code": code})
    assert response.status_code == 400
    assert response.json()["error"] == "invalid_grant"

def test_token_auth_code_invalid_sig():
    response = client.post("/oauth/token", data={"grant_type": "authorization_code", "code": "invalid_code"})
    assert response.status_code == 400

@patch("routers.oauth.create_client")
@patch("routers.oauth.get_settings")
def test_token_refresh_success(mock_get_settings, mock_create_client):
    mock_settings = MagicMock()
    mock_settings.SUPABASE_URL = "https://test.supabase.co"
    mock_settings.SUPABASE_SERVICE_ROLE_KEY = "test_service_key"
    mock_get_settings.return_value = mock_settings

    mock_supabase = MagicMock()
    mock_res = MagicMock()
    mock_res.session.access_token = "new_acc"
    mock_res.session.refresh_token = "new_ref"
    mock_supabase.auth.refresh_session.return_value = mock_res
    mock_create_client.return_value = mock_supabase
    
    enc_ref = encrypt("supa_ref")
    response = client.post("/oauth/token", data={"grant_type": "refresh_token", "refresh_token": enc_ref})
    assert response.status_code == 200
    assert response.json()["access_token"] == "new_acc"

def test_token_refresh_no_token():
    response = client.post("/oauth/token", data={"grant_type": "refresh_token"})
    assert response.status_code == 400
    assert "refresh_token is required" in response.json()["error_description"]

@patch("routers.oauth.create_client")
@patch("routers.oauth.get_settings")
def test_token_refresh_failure(mock_get_settings, mock_create_client):
    mock_settings = MagicMock()
    mock_settings.SUPABASE_URL = "https://test.supabase.co"
    mock_settings.SUPABASE_SERVICE_ROLE_KEY = "test_service_key"
    mock_get_settings.return_value = mock_settings

    mock_supabase = MagicMock()
    mock_supabase.auth.refresh_session.side_effect = Exception("failed")
    mock_create_client.return_value = mock_supabase
    
    enc_ref = encrypt("supa_ref")
    response = client.post("/oauth/token", data={"grant_type": "refresh_token", "refresh_token": enc_ref})
    assert response.status_code == 400

def test_register():
    response = client.post("/oauth/register", json={})
    assert response.status_code == 201
    assert "client_id" in response.json()
    assert "client_secret" in response.json()
