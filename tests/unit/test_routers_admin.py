import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from main import app

client = TestClient(app)

@patch("routers.admin.get_supabase")
def test_post_login_otp_success(mock_get_supabase):
    mock_supabase = MagicMock()
    mock_get_supabase.return_value = mock_supabase
    
    response = client.post("/login/otp", data={"email": "test@test.com"})
    assert response.status_code == 200
    assert response.json() == {"status": "success", "message": "OTP sent successfully."}
    mock_supabase.auth.sign_in_with_otp.assert_called_once()

@patch("routers.admin.get_supabase")
def test_post_login_otp_failure(mock_get_supabase):
    mock_supabase = MagicMock()
    mock_supabase.auth.sign_in_with_otp.side_effect = Exception("error")
    mock_get_supabase.return_value = mock_supabase
    
    response = client.post("/login/otp", data={"email": "test@test.com"})
    assert response.status_code == 200
    assert response.json()["status"] == "error"

@patch("routers.admin.get_supabase")
def test_post_verify_otp_success(mock_get_supabase):
    mock_supabase = MagicMock()
    mock_res = MagicMock()
    mock_res.session.access_token = "acc"
    mock_res.session.refresh_token = "ref"
    mock_supabase.auth.verify_otp.return_value = mock_res
    mock_get_supabase.return_value = mock_supabase
    
    response = client.post("/login/verify", data={"email": "t@t.com", "token": "123456"})
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert "access_token" in response.headers.get("set-cookie", "")

@patch("routers.admin.get_supabase")
def test_post_verify_otp_failure(mock_get_supabase):
    mock_supabase = MagicMock()
    mock_supabase.auth.verify_otp.return_value = None
    mock_get_supabase.return_value = mock_supabase
    
    response = client.post("/login/verify", data={"email": "t@t.com", "token": "123456"})
    assert response.status_code == 200
    assert response.json()["status"] == "error"

def test_logout():
    response = client.get("/logout", follow_redirects=False)
    assert response.status_code == 303
    assert "set-cookie" in response.headers
    assert response.headers["location"] == "/login"

@patch("routers.admin.get_supabase")
def test_get_current_user_success(mock_get_supabase):
    mock_supabase = MagicMock()
    mock_user = MagicMock()
    mock_user.id = "user1"
    mock_user.email = "test@test.com"
    mock_res = MagicMock()
    mock_res.user = mock_user
    mock_supabase.auth.get_user.return_value = mock_res
    mock_get_supabase.return_value = mock_supabase
    
    response = client.get("/api/auth/me", cookies={"access_token": "acc"})
    assert response.status_code == 200
    assert response.json()["user"]["id"] == "user1"

@patch("routers.admin.get_supabase")
def test_get_current_user_failure(mock_get_supabase):
    mock_supabase = MagicMock()
    mock_supabase.auth.get_user.side_effect = Exception("error")
    mock_get_supabase.return_value = mock_supabase
    
    response = client.get("/api/auth/me", cookies={"access_token": "acc"})
    assert response.status_code == 401

def test_get_current_user_no_token():
    response = client.get("/api/auth/me")
    assert response.status_code == 401

@patch("routers.admin.get_supabase")
def test_get_workspace_success(mock_get_supabase):
    mock_supabase = MagicMock()
    mock_res = MagicMock()
    mock_res.user.id = "u1"
    mock_supabase.auth.get_user.return_value = mock_res
    
    mock_db_res = MagicMock()
    mock_db_res.data = [{"odoo_url": "u", "odoo_db": "d", "odoo_username": "n", "odoo_password": "p"}]
    mock_supabase.table().select().eq().execute.return_value = mock_db_res
    
    mock_get_supabase.return_value = mock_supabase
    
    response = client.get("/api/workspace", cookies={"access_token": "acc"})
    assert response.status_code == 200
    assert response.json()["workspace"]["odoo_url"] == "u"

@patch("routers.admin.get_supabase")
def test_api_save_config_success(mock_get_supabase):
    mock_supabase = MagicMock()
    mock_res = MagicMock()
    mock_res.user.id = "u1"
    mock_supabase.auth.get_user.return_value = mock_res
    
    mock_db_res = MagicMock()
    mock_db_res.data = [] # No existing workspaces
    mock_supabase.table().select().eq().execute.return_value = mock_db_res
    
    mock_get_supabase.return_value = mock_supabase
    
    data = {
        "odoo_url": "u", "odoo_db": "d", "odoo_username": "n", "odoo_password": "p"
    }
    response = client.post("/api/workspace/save", data=data, cookies={"access_token": "acc"})
    assert response.status_code == 200
    assert response.json()["status"] == "success"

@patch("routers.admin.get_supabase")
def test_api_delete_config(mock_get_supabase):
    mock_supabase = MagicMock()
    mock_res = MagicMock()
    mock_res.user.id = "u1"
    mock_supabase.auth.get_user.return_value = mock_res
    
    mock_get_supabase.return_value = mock_supabase
    
    response = client.post("/api/workspace/delete", json={"workspace_id": "ws1"}, cookies={"access_token": "acc"})
    assert response.status_code == 200
    assert response.json()["status"] == "success"

def test_api_logout():
    response = client.post("/api/logout")
    assert response.status_code == 200

@patch("routers.admin.get_supabase")
def test_legacy_save_config(mock_get_supabase):
    mock_supabase = MagicMock()
    mock_res = MagicMock()
    mock_res.user.id = "u1"
    mock_supabase.auth.get_user.return_value = mock_res
    
    mock_db_res = MagicMock()
    mock_db_res.data = []
    mock_supabase.table().select().eq().execute.return_value = mock_db_res
    
    mock_get_supabase.return_value = mock_supabase
    
    data = {
        "odoo_url": "u", "odoo_db": "d", "odoo_username": "n", "odoo_password": "p"
    }
    response = client.post("/admin/save", data=data, cookies={"access_token": "acc"})
    assert response.status_code == 200
