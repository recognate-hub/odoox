import pytest
from unittest.mock import patch, MagicMock
from mcp_app.security import secure_tool, _check_rate_limit, _rate_limit_state, UserContext
from core.exceptions import PermissionDeniedError, RateLimitExceededError

@pytest.fixture(autouse=True)
def reset_rate_limit():
    _rate_limit_state.clear()
    yield

def test_rate_limit_blocks_excessive_calls():
    user_id = "test_user_123"
    
    # Simulate 100 successful calls
    for _ in range(100):
        _check_rate_limit(user_id)
        
    # The 101st call should raise an error
    with pytest.raises(RateLimitExceededError):
        _check_rate_limit(user_id)

@patch("mcp_app.security.get_current_user_context")
@patch("mcp_app.security.PolicyEngine.is_allowed")
def test_secure_tool_rbac_rejection(mock_is_allowed, mock_get_context):
    mock_get_context.return_value = UserContext(user_id="user1", role="Sales")
    mock_is_allowed.return_value = False
    
    @secure_tool(action="test_action")
    def dummy_tool():
        return "success"
        
    with pytest.raises(PermissionDeniedError, match="Role Sales does not have permission to execute test_action"):
        dummy_tool()

@patch("mcp_app.security.get_current_user_context")
@patch("mcp_app.security.PolicyEngine.is_allowed")
@patch("mcp_app.security.PolicyEngine.is_model_allowed")
def test_secure_tool_model_rbac_rejection(mock_is_model_allowed, mock_is_allowed, mock_get_context):
    mock_get_context.return_value = UserContext(user_id="user1", role="Sales")
    mock_is_allowed.return_value = True
    mock_is_model_allowed.return_value = False
    
    @secure_tool(action="search_read_records")
    def dummy_generic_tool(model=None):
        return "success"
        
    with pytest.raises(PermissionDeniedError, match="Role Sales does not have permission to access model restricted.model"):
        dummy_generic_tool(model="restricted.model")

@patch("mcp_app.security.get_current_user_context")
@patch("mcp_app.security.PolicyEngine.is_allowed")
@patch("mcp_app.security.PolicyEngine.is_model_allowed")
def test_secure_tool_model_rbac_success(mock_is_model_allowed, mock_is_allowed, mock_get_context):
    mock_get_context.return_value = UserContext(user_id="user1", role="Sales")
    mock_is_allowed.return_value = True
    mock_is_model_allowed.return_value = True
    
    @secure_tool(action="search_read_records")
    def dummy_generic_tool(model=None):
        return "success"
        
    assert dummy_generic_tool(model="allowed.model") == "success"
