import pytest
import time
import os

# Set required environment variables before importing anything from mcp_app
os.environ["ODOO_URL"] = "https://odoo.example.com"
os.environ["ODOO_DB"] = "test_db"
os.environ["ODOO_USERNAME"] = "test_user"
os.environ["ODOO_PASSWORD"] = "test_pass"
os.environ["ANTHROPIC_API_KEY"] = "sk-ant-test"
os.environ["COMPANY_NAME"] = "Test Co"
os.environ["COMPANY_EMAIL"] = "test@example.com"

from unittest.mock import patch, MagicMock

from core.exceptions import PermissionDeniedError, RateLimitExceededError
from mcp_app.security import secure_tool, UserContext, _rate_limit_state

# Reset rate limit state before each test
@pytest.fixture(autouse=True)
def reset_rate_limit():
    _rate_limit_state.clear()
    yield


@patch("mcp_app.security._mock_context", UserContext(user_id="test_admin", role="Admin"))
def test_secure_tool_admin_access():
    
    @secure_tool(allowed_roles=["Manager"])
    def dummy_tool():
        return "Success"
        
    # Admin should bypass the exact role check if "Admin" is part of the role logic
    # In our implementation: `if user.role not in allowed_roles and "Admin" not in user.role`
    assert dummy_tool() == "Success"


@patch("mcp_app.security._mock_context", UserContext(user_id="test_sales", role="Sales"))
def test_secure_tool_permission_denied():
    
    @secure_tool(allowed_roles=["Manager"])
    def dummy_tool():
        return "Success"
        
    with pytest.raises(PermissionDeniedError):
        dummy_tool()


@patch("mcp_app.security._mock_context", UserContext(user_id="test_user", role="Manager"))
def test_secure_tool_rate_limit(monkeypatch):
    monkeypatch.setattr("mcp_app.security.RATE_LIMIT_MAX_CALLS", 2)
    
    @secure_tool(allowed_roles=["Manager"])
    def dummy_tool():
        return "Success"
        
    # First call - should succeed
    dummy_tool()
    # Second call - should succeed
    dummy_tool()
    
    # Third call - should raise RateLimitExceededError
    with pytest.raises(RateLimitExceededError):
        dummy_tool()
