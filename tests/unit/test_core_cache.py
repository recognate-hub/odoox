from unittest.mock import MagicMock, patch

import pytest
from pydantic import BaseModel

import core.cache
from core.cache import (
    get_cached_value,
    get_cached_workspace,
    set_cached_value,
    set_cached_workspace,
)


class DummyModel(BaseModel):
    name: str


@pytest.fixture(autouse=True)
def setup_redis_client():
    old_client = core.cache.redis_client
    mock_redis = MagicMock()
    core.cache.redis_client = mock_redis
    yield mock_redis
    core.cache.redis_client = old_client


def test_get_cached_workspace_success(setup_redis_client):
    mock_data = '{"name": "test"}'
    setup_redis_client.get.return_value = mock_data

    result = get_cached_workspace("token123", DummyModel)

    setup_redis_client.get.assert_called_once_with("workspace:token123")
    assert isinstance(result, DummyModel)
    assert result.name == "test"


def test_get_cached_workspace_no_client():
    core.cache.redis_client = None
    assert get_cached_workspace("token123", DummyModel) is None


def test_get_cached_workspace_exception(setup_redis_client):
    setup_redis_client.get.side_effect = Exception("Redis error")
    assert get_cached_workspace("token123", DummyModel) is None


def test_get_cached_workspace_no_data(setup_redis_client):
    setup_redis_client.get.return_value = None
    assert get_cached_workspace("token123", DummyModel) is None


def test_set_cached_workspace_success(setup_redis_client):
    model = DummyModel(name="test")
    set_cached_workspace("token123", model, 100)
    setup_redis_client.setex.assert_called_once_with(
        "workspace:token123", 100, '{"name":"test"}'
    )


def test_set_cached_workspace_no_client():
    core.cache.redis_client = None
    # Should not raise exception
    set_cached_workspace("token123", DummyModel(name="test"), 100)


def test_set_cached_workspace_exception(setup_redis_client):
    setup_redis_client.setex.side_effect = Exception("Redis error")
    # Should not raise exception
    set_cached_workspace("token123", DummyModel(name="test"), 100)


def test_get_cached_value_success(setup_redis_client):
    setup_redis_client.get.return_value = "val"
    assert get_cached_value("mykey") == "val"
    setup_redis_client.get.assert_called_once_with("mykey")


def test_get_cached_value_no_client():
    core.cache.redis_client = None
    assert get_cached_value("mykey") is None


def test_get_cached_value_exception(setup_redis_client):
    setup_redis_client.get.side_effect = Exception("Redis error")
    assert get_cached_value("mykey") is None


def test_set_cached_value_success(setup_redis_client):
    set_cached_value("mykey", "myval", 200)
    setup_redis_client.setex.assert_called_once_with("mykey", 200, "myval")


def test_set_cached_value_no_client():
    core.cache.redis_client = None
    set_cached_value("mykey", "myval", 200)


def test_set_cached_value_exception(setup_redis_client):
    setup_redis_client.setex.side_effect = Exception("Redis error")
    set_cached_value("mykey", "myval", 200)


def test_redis_initialization_exception():
    with patch("core.cache.redis.Redis.from_url", side_effect=Exception("Init error")):
        # We need to reload the module to trigger the initialization block
        import importlib

        with patch("core.cache.settings.REDIS_URL", "redis://localhost:6379"):
            importlib.reload(core.cache)
            assert core.cache.redis_client is None
