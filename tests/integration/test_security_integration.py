"""Integration tests for the security layer (RBAC, rate limiting, audit logging).

Tests exercise the full decorator chain: secure_tool → RBAC → rate limit → audit log → execution.
"""
import pytest
import time
from unittest.mock import patch

from core.exceptions import PermissionDeniedError, RateLimitExceededError
from mcp_app.security import (
    secure_tool, UserContext, _rate_limit_state,
    RATE_LIMIT_MAX_CALLS, RATE_LIMIT_WINDOW_SEC
)
from core.policy import PolicyEngine

@pytest.fixture(autouse=True)
def reset_rate_limit():
    """Clear rate limit state before each test."""
    _rate_limit_state.clear()
    yield
    _rate_limit_state.clear()


@pytest.fixture(autouse=True)
def mock_policy():
    """Inject a test policy into the PolicyEngine."""
    PolicyEngine._policies = {
        "Admin": ["*"],
        "Sales": ["sales_tool", "shared_tool"],
        "Manager": ["manager_tool", "shared_tool"],
        "Support": ["support_tool"]
    }
    PolicyEngine._loaded = True
    yield
    PolicyEngine._policies = {}
    PolicyEngine._loaded = False


# --- Full RBAC Flow ---

class TestRBACIntegration:

    @patch("mcp_app.security.get_current_user_context", return_value=UserContext(user_id="admin_user", role="Admin"))
    def test_admin_bypasses_role_check(self, mock_context):
        """Admin role should access any tool regardless of allowed_roles."""
        @secure_tool()
        def restricted_tool():
            return "admin_accessed"

        assert restricted_tool() == "admin_accessed"

    @patch("mcp_app.security.get_current_user_context", return_value=UserContext(user_id="sales_rep", role="Sales"))
    def test_allowed_role_succeeds(self, mock_context):
        """Sales role should access Sales-allowed tools."""
        @secure_tool()
        def sales_tool():
            return "sales_ok"

        assert sales_tool() == "sales_ok"

    @patch("mcp_app.security.get_current_user_context", return_value=UserContext(user_id="support_agent", role="Support"))
    def test_disallowed_role_denied(self, mock_context):
        """Support role should be denied access to Manager-only tools."""
        @secure_tool()
        def manager_tool():
            return "should_not_reach"

        with pytest.raises(PermissionDeniedError) as exc_info:
            manager_tool()

        assert "Support" in str(exc_info.value)
        assert "manager_tool" in str(exc_info.value)

    @patch("mcp_app.security.get_current_user_context", return_value=UserContext(user_id="intern", role="Viewer"))
    def test_multiple_tools_different_roles(self, mock_context):
        """Test that different tools enforce different role requirements."""
        @secure_tool()
        def sales_tool():
            return "a"

        @secure_tool(action="support_tool") # Manually setting action to bypass func name
        def tool_b():
            return "b"

        # Viewer can't access sales_tool
        with pytest.raises(PermissionDeniedError):
            sales_tool()

        # Viewer can't access support_tool either, since Viewer isn't in policy
        with pytest.raises(PermissionDeniedError):
            tool_b()


# --- Rate Limiting Integration ---

class TestRateLimitIntegration:

    @patch("mcp_app.security.get_current_user_context", return_value=UserContext(user_id="rate_test_user", role="Admin"))
    def test_rate_limit_enforced(self, mock_context, monkeypatch):
        """Test that rate limiting triggers after exceeding max calls."""
        monkeypatch.setattr("mcp_app.security.RATE_LIMIT_MAX_CALLS", 3)

        @secure_tool()
        def rate_limited_tool():
            return "ok"

        # First 3 calls should succeed
        for _ in range(3):
            assert rate_limited_tool() == "ok"

        # 4th call should be rate limited
        with pytest.raises(RateLimitExceededError):
            rate_limited_tool()

    @patch("mcp_app.security.get_current_user_context", return_value=UserContext(user_id="window_user", role="Admin"))
    def test_rate_limit_window_expiry(self, mock_context, monkeypatch):
        """Test that rate limit resets after the window expires."""
        monkeypatch.setattr("mcp_app.security.RATE_LIMIT_MAX_CALLS", 2)
        monkeypatch.setattr("mcp_app.security.RATE_LIMIT_WINDOW_SEC", 1)

        @secure_tool()
        def windowed_tool():
            return "ok"

        # Use up the limit
        windowed_tool()
        windowed_tool()

        with pytest.raises(RateLimitExceededError):
            windowed_tool()

        # Wait for window to expire
        time.sleep(1.1)

        # Should be allowed again
        assert windowed_tool() == "ok"

    @patch("mcp_app.security.get_current_user_context", return_value=UserContext(user_id="user_a", role="Admin"))
    def test_rate_limits_are_per_user(self, mock_context, monkeypatch):
        """Test that rate limits are tracked per user, not globally."""
        monkeypatch.setattr("mcp_app.security.RATE_LIMIT_MAX_CALLS", 1)

        @secure_tool()
        def per_user_tool():
            return "ok"

        # User A uses their limit
        per_user_tool()

        with pytest.raises(RateLimitExceededError):
            per_user_tool()

        # User B should have their own limit
        with patch("mcp_app.security.get_current_user_context", return_value=UserContext(user_id="user_b", role="Admin")):
            assert per_user_tool() == "ok"


# --- Audit Logging Integration ---

class TestAuditLoggingIntegration:

    @patch("mcp_app.security.get_current_user_context", return_value=UserContext(user_id="audit_user", role="Sales"))
    @patch("mcp_app.security.audit_logger")
    def test_successful_invocation_logs(self, mock_audit_logger, mock_context):
        """Test that a successful tool call produces audit log entries."""
        @secure_tool(action="sales_tool")
        def audited_tool(x=1):
            return f"result_{x}"

        result = audited_tool(x=42)

        assert result == "result_42"

        # Should have logged both request and success
        info_calls = mock_audit_logger.info.call_args_list
        assert len(info_calls) >= 2

        # First call: "Tool Invoked"
        assert info_calls[0][0][0] == "Tool Invoked"

        # Second call: "Tool Succeeded"
        assert info_calls[1][0][0] == "Tool Succeeded"

    @patch("mcp_app.security.get_current_user_context", return_value=UserContext(user_id="error_user", role="Admin"))
    @patch("mcp_app.security.audit_logger")
    def test_failed_invocation_logs_error(self, mock_audit_logger, mock_context):
        """Test that a failed tool call produces an error audit log."""
        @secure_tool()
        def failing_tool():
            raise ValueError("Something went wrong")

        with pytest.raises(ValueError):
            failing_tool()

        # Should have logged request and then failure
        mock_audit_logger.error.assert_called_once()
        error_call = mock_audit_logger.error.call_args
        assert error_call[0][0] == "Tool Failed"

    @patch("mcp_app.security.get_current_user_context", return_value=UserContext(user_id="denied_user", role="Viewer"))
    @patch("mcp_app.security.audit_logger")
    def test_permission_denied_logs_warning(self, mock_audit_logger, mock_context):
        """Test that a denied tool call produces a warning audit log."""
        @secure_tool()
        def restricted_tool():
            return "should_not_reach"

        with pytest.raises(PermissionDeniedError):
            restricted_tool()

        # Should have logged the denial
        mock_audit_logger.warning.assert_called_once()
        warning_call = mock_audit_logger.warning.call_args
        assert warning_call[0][0] == "Permission Denied"
