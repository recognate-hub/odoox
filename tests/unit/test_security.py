import os

import pytest

# Set required environment variables before importing anything from mcp_app
os.environ["ODOO_URL"] = "https://odoo.example.com"
os.environ["ODOO_DB"] = "test_db"
os.environ["ODOO_USERNAME"] = "test_user"
os.environ["ODOO_PASSWORD"] = "test_pass"
os.environ["ANTHROPIC_API_KEY"] = "sk-ant-test"
os.environ["COMPANY_NAME"] = "Test Co"
os.environ["COMPANY_EMAIL"] = "test@example.com"

from unittest.mock import patch

from core.exceptions import PermissionDeniedError, RateLimitExceededError
from mcp_app.security import UserContext, _rate_limit_state, secure_tool


@pytest.fixture(autouse=True)
def reset_rate_limit():
    _rate_limit_state.clear()
    yield

@patch("mcp_app.security.get_current_user_context", return_value=UserContext(user_id="test_admin", role="Admin"))
@patch("core.policy.PolicyEngine.is_allowed", return_value=True)
def test_secure_tool_admin_access(mock_policy, mock_context):
    @secure_tool()
    def dummy_tool():
        return "Success"
        
    assert dummy_tool() == "Success"
    mock_policy.assert_called_once_with("Admin", "dummy_tool")

@patch("mcp_app.security.get_current_user_context", return_value=UserContext(user_id="test_sales", role="Sales"))
@patch("core.policy.PolicyEngine.is_allowed", return_value=False)
def test_secure_tool_permission_denied(mock_policy, mock_context):
    @secure_tool()
    def dummy_tool():
        return "Success"
        
    with pytest.raises(PermissionDeniedError):
        dummy_tool()
    mock_policy.assert_called_once_with("Sales", "dummy_tool")

@patch("mcp_app.security.get_current_user_context", return_value=UserContext(user_id="test_user", role="Manager"))
@patch("core.policy.PolicyEngine.is_allowed", return_value=True)
def test_secure_tool_rate_limit(mock_policy, mock_context, monkeypatch):
    monkeypatch.setattr("mcp_app.security.RATE_LIMIT_MAX_CALLS", 2)
    
    @secure_tool()
    def dummy_tool():
        return "Success"
        
    # First call - should succeed
    dummy_tool()
    # Second call - should succeed
    dummy_tool()
    
    # Third call - should raise RateLimitExceededError
    with pytest.raises(RateLimitExceededError):
        dummy_tool()
