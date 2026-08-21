from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException

from core.context import (
    CACHE_TTL_SEC,
    WorkspaceContext,
    _credentials_cache,
    current_token,
    get_current_token,
    get_workspace_credentials,
)


@pytest.fixture(autouse=True)
def clear_caches():
    _credentials_cache.clear()
    current_token.set(None)
    yield


def test_get_current_token_missing():
    with pytest.raises(RuntimeError, match="No auth token"):
        get_current_token()


def test_get_current_token_success():
    current_token.set("mytoken")
    assert get_current_token() == "mytoken"


@patch("core.context.get_cached_workspace")
def test_get_workspace_credentials_from_redis(mock_get_cached):
    mock_ws = WorkspaceContext(
        odoo_url="url",
        odoo_db="db",
        odoo_username="user",
        odoo_password="pwd",
        user_id="u1",
    )
    mock_get_cached.return_value = mock_ws

    result = get_workspace_credentials("token", "ws1")
    assert result == mock_ws
    mock_get_cached.assert_called_once_with("token:ws1", WorkspaceContext)


@patch("core.context.get_cached_workspace")
def test_get_workspace_credentials_from_memory(mock_get_cached):
    mock_get_cached.return_value = None
    mock_ws = WorkspaceContext(
        odoo_url="url",
        odoo_db="db",
        odoo_username="user",
        odoo_password="pwd",
        user_id="u1",
    )
    import time

    _credentials_cache[("token", "ws1")] = (mock_ws, time.time())

    result = get_workspace_credentials("token", "ws1")
    assert result == mock_ws


@patch("core.context.get_cached_workspace")
@patch("core.context.get_supabase")
@patch("core.context.set_cached_workspace")
def test_get_workspace_credentials_from_supabase_success(
    mock_set, mock_get_supa, mock_get_cached
):
    mock_get_cached.return_value = None

    mock_supa = MagicMock()
    mock_get_supa.return_value = mock_supa

    # Mock user response
    mock_user_resp = MagicMock()
    mock_user_resp.user.id = "user123"
    mock_supa.auth.get_user.return_value = mock_user_resp

    # Mock db response
    mock_db_resp = MagicMock()
    mock_db_resp.data = [
        {
            "odoo_url": "http://odoo",
            "odoo_db": "mydb",
            "odoo_username": "admin",
            "odoo_password": "pwd",
            "role": "Manager",
        }
    ]
    mock_supa.table().select().eq().eq().limit().execute.return_value = mock_db_resp

    result = get_workspace_credentials("token", "ws1")

    assert result.odoo_url == "http://odoo"
    assert result.user_id == "user123"
    assert result.role == "Manager"
    assert ("token", "ws1") in _credentials_cache
    mock_set.assert_called_once_with("token:ws1", result, ttl=CACHE_TTL_SEC)


@patch("core.context.get_cached_workspace")
@patch("core.context.get_supabase")
def test_get_workspace_credentials_supabase_invalid_token(
    mock_get_supa, mock_get_cached
):
    mock_get_cached.return_value = None
    mock_supa = MagicMock()
    mock_get_supa.return_value = mock_supa
    mock_supa.auth.get_user.return_value = None

    from fastapi import HTTPException

    with pytest.raises(HTTPException) as excinfo:
        get_workspace_credentials("token")
    assert excinfo.value.status_code == 401
    assert "Invalid token" in str(excinfo.value.detail)


@patch("core.context.get_cached_workspace")
@patch("core.context.get_supabase")
def test_get_workspace_credentials_supabase_no_workspace(
    mock_get_supa, mock_get_cached
):
    mock_get_cached.return_value = None
    mock_supa = MagicMock()
    mock_get_supa.return_value = mock_supa

    mock_user_resp = MagicMock()
    mock_user_resp.user.id = "user123"
    mock_supa.auth.get_user.return_value = mock_user_resp

    mock_db_resp = MagicMock()
    mock_db_resp.data = []
    mock_supa.table().select().eq().execute.return_value = mock_db_resp

    with pytest.raises(HTTPException) as exc_info:
        get_workspace_credentials("test-token")
    assert exc_info.value.status_code == 404


@patch("core.cache.get_cached_value")
def test_redis_cached_api_key_revocation_revoked(mock_get_cached_value):
    # If redis says it's revoked, it should fail immediately
    mock_get_cached_value.return_value = "1"

    from fastapi import HTTPException

    from core.context import get_workspace_credentials

    with pytest.raises(HTTPException, match="API Key has been revoked"):
        # We need to pass an odx_ token to trigger this branch
        get_workspace_credentials("odx_testkey", force_refresh=True)
