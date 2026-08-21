from unittest.mock import MagicMock, patch

import pytest

import core.supabase
from core.supabase import get_supabase


@pytest.fixture(autouse=True)
def clear_supabase_client():
    core.supabase._supabase_client = None
    yield


@patch("core.supabase.get_settings")
def test_get_supabase_missing_settings(mock_get_settings):
    mock_settings = MagicMock()
    mock_settings.SUPABASE_URL = None
    mock_get_settings.return_value = mock_settings

    with pytest.raises(ValueError, match="must be set"):
        get_supabase()


@patch("core.supabase.create_client")
@patch("core.supabase.get_settings")
def test_get_supabase_with_token(mock_get_settings, mock_create):
    mock_settings = MagicMock()
    mock_settings.SUPABASE_URL = "http://localhost"
    mock_settings.SUPABASE_KEY = "key"
    mock_get_settings.return_value = mock_settings

    mock_client = MagicMock()
    mock_create.return_value = mock_client

    client = get_supabase("my_token")

    mock_create.assert_called_once_with("http://localhost", "key")
    mock_client.postgrest.auth.assert_called_once_with("my_token")
    assert client == mock_client


@patch("core.supabase.create_client")
@patch("core.supabase.get_settings")
def test_get_supabase_global_client(mock_get_settings, mock_create):
    mock_settings = MagicMock()
    mock_settings.SUPABASE_URL = "http://localhost"
    mock_settings.SUPABASE_KEY = "key"
    mock_get_settings.return_value = mock_settings

    mock_client = MagicMock()
    mock_create.return_value = mock_client

    client1 = get_supabase()
    client2 = get_supabase()

    # Should only create it once
    mock_create.assert_called_once_with("http://localhost", "key")
    assert client1 == mock_client
    assert client2 == mock_client
