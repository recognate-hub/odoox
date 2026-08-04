import pytest
from core.exceptions import (
    BaseAppError,
    OdooConnectorError,
    ClaudeAPIError,
    PermissionDeniedError
)


def test_exception_hierarchy():
    """Test that the exception hierarchy is correctly set up."""
    # Odoo exceptions should inherit from BaseAppError
    with pytest.raises(BaseAppError):
        raise OdooConnectorError("Test Odoo Error")

    # Claude exceptions should inherit from BaseAppError
    with pytest.raises(BaseAppError):
        raise ClaudeAPIError("Test Claude Error")

    # Security exceptions should inherit from BaseAppError
    with pytest.raises(BaseAppError):
        raise PermissionDeniedError("Test Permission Error")
