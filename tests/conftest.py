"""Root-level conftest for shared test fixtures and environment setup."""
import os
from unittest.mock import MagicMock

import pytest

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

class MockOdooServer:
    def __init__(self):
        self.records = {
            "crm.lead": [
                {"id": 1, "name": "Test Lead 1", "email_from": "test1@example.com", "stage_id": [1, "New"]},
                {"id": 2, "name": "Test Lead 2", "email_from": "test2@example.com", "stage_id": [2, "Qualified"]}
            ]
        }
        
    def execute_kw(self, db, uid, pwd, model, method, args, kwargs=None):
        if method == "search_read":
            domain = args[0] if args else []
            data = self.records.get(model, [])
            # Simple domain filtering mock
            if domain:
                for criterion in domain:
                    if len(criterion) == 3:
                        field, op, val = criterion
                        if op == "=":
                            data = [d for d in data if d.get(field) == val]
                        elif op == "ilike":
                            data = [d for d in data if val.lower() in str(d.get(field, "")).lower()]
            return data
        elif method == "create":
            data = args[0][0] if args and args[0] else {}
            new_id = len(self.records.get(model, [])) + 1
            data["id"] = new_id
            self.records.setdefault(model, []).append(data)
            return new_id
        return True

@pytest.fixture
def mock_odoo_server(monkeypatch):
    server = MockOdooServer()
    mock_server_proxy = MagicMock()
    mock_server_proxy.execute_kw = server.execute_kw
    
    mock_common = MagicMock()
    mock_common.authenticate.return_value = 1
    
    monkeypatch.setattr("odoo.xmlrpc.XmlRpcOdooConnector._get_models", lambda self, ws: mock_server_proxy)
    monkeypatch.setattr("odoo.xmlrpc.XmlRpcOdooConnector._get_common", lambda self, ws: mock_common)
    return server

