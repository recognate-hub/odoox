import time
from unittest.mock import MagicMock, patch

import pytest

from mcp_app.security import (
    RATE_LIMIT_MAX_CALLS,
    _check_rate_limit,
)


@pytest.fixture
def mock_redis():
    mock = MagicMock()
    return mock

@patch("core.cache.redis_client")
def test_redis_rate_limit_allowed(mock_redis_client):
    # Setup mock to return 1 (first request)
    mock_redis_client.incr.return_value = 1
    
    # Check limit
    user_id = "test_user"
    allowed = _check_rate_limit(user_id)
    
    # Verify expire was called on first request
    mock_redis_client.expire.assert_called_once()

@patch("core.cache.redis_client")
def test_redis_rate_limit_blocked(mock_redis_client):
    from core.exceptions import RateLimitExceededError
    # Setup mock to return over limit
    mock_redis_client.incr.return_value = RATE_LIMIT_MAX_CALLS + 1
    
    # Check limit
    user_id = "test_user_blocked"
    with pytest.raises(RateLimitExceededError):
        _check_rate_limit(user_id)

@patch("core.cache.redis_client", None)
def test_fallback_rate_limit_allowed():
    # Test fallback to in-memory dictionary
    from mcp_app.security import _rate_limit_state
    
    user_id = "test_fallback_user"
    # Ensure clean state
    if user_id in _rate_limit_state:
        del _rate_limit_state[user_id]
        
    _check_rate_limit(user_id)
    assert len(_rate_limit_state[user_id]) == 1

@patch("core.cache.redis_client", None)
def test_fallback_rate_limit_blocked():
    from core.exceptions import RateLimitExceededError
    from mcp_app.security import _rate_limit_state
    
    user_id = "test_fallback_blocked"
    # Setup state to be at limit
    _rate_limit_state[user_id] = [time.time()] * RATE_LIMIT_MAX_CALLS
    
    with pytest.raises(RateLimitExceededError):
        _check_rate_limit(user_id)

