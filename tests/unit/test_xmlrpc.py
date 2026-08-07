import pytest
from unittest.mock import patch, MagicMock
from odoo.xmlrpc import XmlRpcOdooConnector
from core.exceptions import OdooConnectionError, OdooAuthError

@patch("odoo.xmlrpc.get_settings")
@patch("odoo.xmlrpc.get_current_token")
@patch("odoo.xmlrpc.get_workspace_credentials")
def test_xmlrpc_connector_init(mock_get_workspace, mock_get_token, mock_get_settings):
    connector = XmlRpcOdooConnector()
    assert connector is not None

@patch("odoo.xmlrpc.redis_client", None)
@patch("odoo.xmlrpc.get_settings")
@patch("odoo.xmlrpc.get_current_token")
@patch("odoo.xmlrpc.get_workspace_credentials")
@patch("odoo.xmlrpc.XmlRpcOdooConnector._get_common")
def test_xmlrpc_authenticate_failure(mock_get_common, mock_get_workspace, mock_get_token, mock_get_settings):
    mock_get_token.return_value = "fake_token"
    mock_workspace = MagicMock()
    mock_workspace.odoo_url = "http://fake.odoo.com"
    mock_workspace.odoo_db = "testdb"
    mock_workspace.odoo_username = "user"
    mock_get_workspace.return_value = mock_workspace
    
    mock_common = MagicMock()
    mock_common.authenticate.return_value = False
    mock_get_common.return_value = mock_common
    
    with patch("odoo.xmlrpc.decrypt", return_value="pass"):
        connector = XmlRpcOdooConnector()
        with pytest.raises((OdooConnectionError, OdooAuthError)):
            connector._authenticate(force_refresh=True)

def test_circuit_breaker_logic():
    connector = XmlRpcOdooConnector()
    with patch("odoo.xmlrpc.redis_client", None):
        # Manually force a failure
        connector._record_failure("testdb")
        assert connector._circuit_breakers["testdb"][0] == 1
        
        connector._record_success("testdb")
        assert "testdb" not in connector._circuit_breakers
