"""Root-level conftest for shared test fixtures and environment setup."""
import os
import pytest
from unittest.mock import MagicMock

# Ensure required environment variables are set for all tests.
# This runs before any test module import, preventing ValidationErrors
# from Pydantic settings during import-time initialization.
os.environ.setdefault("ODOO_URL", "https://odoo.example.com")
os.environ.setdefault("ODOO_DB", "test_db")
os.environ.setdefault("ODOO_USERNAME", "test_user")
os.environ.setdefault("ODOO_PASSWORD", "test_pass")
os.environ.setdefault("ANTHROPIC_API_KEY", "sk-ant-test")
os.environ.setdefault("COMPANY_NAME", "Test Co")
os.environ.setdefault("COMPANY_EMAIL", "test@example.com")


@pytest.fixture
def mock_settings():
    """Create a mock Settings object with all required fields."""
    from config.settings import Settings

    settings = MagicMock(spec=Settings)
    settings.ODOO_URL = "https://odoo.example.com"
    settings.ODOO_DB = "test_db"
    settings.ODOO_USERNAME = "test_user"

    mock_password = MagicMock()
    mock_password.get_secret_value.return_value = "test_pass"
    settings.ODOO_PASSWORD = mock_password

    mock_api_key = MagicMock()
    mock_api_key.get_secret_value.return_value = "sk-ant-test-key"
    settings.ANTHROPIC_API_KEY = mock_api_key

    settings.CLAUDE_MODEL = "claude-3-5-sonnet-20240620"
    settings.CLAUDE_TEMPERATURE = 0.0
    settings.CLAUDE_TIMEOUT = 30
    settings.COMPANY_NAME = "Test Co"
    settings.COMPANY_EMAIL = "test@example.com"
    settings.COMPANY_PHONE = ""
    settings.SERVER_HOST = "0.0.0.0"
    settings.SERVER_PORT = 8000
    settings.LOG_LEVEL = "INFO"

    return settings
