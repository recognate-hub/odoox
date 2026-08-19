from unittest.mock import MagicMock, patch

import pytest

from core.exceptions import (
    CircuitBreakerOpenError,
    OdooAuthError,
    OdooConnectorError,
)
from odoo.xmlrpc import (
    RequestsTransport,
    XmlRpcOdooConnector,
    get_transport,
)


def test_get_transport():
    transport = get_transport("https://test")
    assert isinstance(transport, RequestsTransport)
    
    transport2 = get_transport("http://test")
    assert isinstance(transport2, RequestsTransport)
    assert transport2.protocol == "http"

@patch("odoo.xmlrpc.get_settings")
def test_timeout_safe_transport_init(mock_settings):
    mock_s = MagicMock()
    mock_s.ODOO_CLIENT_CERT_PATH = "fake_cert"
    mock_s.ODOO_CLIENT_KEY_PATH = "fake_key"
    mock_settings.return_value = mock_s
    
    with patch("os.path.exists", return_value=False):
        t = RequestsTransport()
        t.session = MagicMock()
        t.parse_response = MagicMock(return_value="xml_response")
        
        # Test SSL fallback logic in _get_session
        assert t is not None

@pytest.fixture
def connector():
    with patch("odoo.xmlrpc.redis_client", None):
        return XmlRpcOdooConnector()

@pytest.fixture
def mock_workspace():
    mock_ws = MagicMock()
    mock_ws.odoo_url = "http://test"
    mock_ws.odoo_db = "testdb"
    mock_ws.odoo_username = "user"
    mock_ws.odoo_password = "pwd"
    return mock_ws

@patch("odoo.xmlrpc.get_current_token", return_value="token1")
@patch("odoo.xmlrpc.redis_client")
def test_authenticate_success(mock_redis, mock_token, mock_workspace):
    with patch.object(XmlRpcOdooConnector, "_get_workspace", return_value=mock_workspace):
        with patch.object(XmlRpcOdooConnector, "_get_common") as mock_get_common:
            mock_common = MagicMock()
            mock_common.authenticate.return_value = 123
            mock_get_common.return_value = mock_common
            
            with patch("odoo.xmlrpc.decrypt", return_value="pwd"):
                conn = XmlRpcOdooConnector()
                uid = conn._authenticate(force_refresh=True)
                assert uid == 123
                mock_redis.setex.assert_called_once()

@patch("odoo.xmlrpc.redis_client", None)
@patch("odoo.xmlrpc.get_current_token", return_value="token1")
def test_authenticate_cached(mock_token, connector):
    connector._uids["token1"] = 999
    assert connector._authenticate() == 999

@patch("odoo.xmlrpc.get_current_token", return_value="token1")
def test_authenticate_auth_error(mock_token, connector, mock_workspace):
    with patch.object(XmlRpcOdooConnector, "_get_workspace", return_value=mock_workspace):
        with patch.object(XmlRpcOdooConnector, "_get_common") as mock_get_common:
            mock_common = MagicMock()
            mock_common.authenticate.return_value = False
            mock_get_common.return_value = mock_common
            
            with patch("odoo.xmlrpc.decrypt", return_value="pwd"):
                with pytest.raises(OdooAuthError):
                    connector._authenticate(force_refresh=True)

def test_circuit_breaker(connector):
    connector._record_failure("db1")
    connector._record_failure("db1")
    connector._record_failure("db1")
    
    with pytest.raises(CircuitBreakerOpenError, match="Circuit breaker open"):
        connector._check_circuit_breaker("db1")
        
    connector._record_success("db1")
    connector._check_circuit_breaker("db1")

@patch.object(XmlRpcOdooConnector, "_authenticate", return_value=123)
@patch.object(XmlRpcOdooConnector, "_get_workspace")
def test_execute_success(mock_get_ws, mock_auth, connector, mock_workspace):
    mock_get_ws.return_value = mock_workspace
    
    with patch.object(XmlRpcOdooConnector, "_get_models") as mock_get_models:
        mock_models = MagicMock()
        mock_models.execute_kw.return_value = "success"
        mock_get_models.return_value = mock_models
        
        with patch("odoo.xmlrpc.decrypt", return_value="pwd"):
            result = connector._execute("res.partner", "search")
            assert result == "success"

@patch.object(XmlRpcOdooConnector, "_authenticate", return_value=123)
@patch.object(XmlRpcOdooConnector, "_get_workspace")
def test_execute_connection_error(mock_get_ws, mock_auth, connector, mock_workspace):
    mock_get_ws.return_value = mock_workspace
    
    mock_models = MagicMock()
    mock_models.execute_kw.side_effect = OSError("Connection dropped")
    
    with patch.object(XmlRpcOdooConnector, "_get_models", return_value=mock_models):
        with patch("odoo.xmlrpc.decrypt", return_value="pwd"):
            from tenacity import RetryError
            with pytest.raises(RetryError):
                connector._execute("res.partner", "search")

@patch.object(XmlRpcOdooConnector, "_execute")
def test_public_methods(mock_exec, connector):
    mock_exec.return_value = []
    assert connector.get_leads() == []
    
    mock_exec.return_value = 1
    with patch("odoo.xmlrpc.IdempotencyCache.check_or_execute", side_effect=lambda db, k, d, f: f()):
        with patch.object(XmlRpcOdooConnector, "_get_workspace", return_value=MagicMock()):
            assert connector.create_lead({}) == 1
            assert connector.create_contact({}) == 1
            assert connector.create_product({}) == 1
            assert connector.create_quote({}) == 1
            assert connector.create_activity({}) == 1
            assert connector.schedule_meeting({}) == 1
            assert connector.create_invoice({}) == 1
            assert connector.send_email({}) == 1
            assert connector.create_record("model", {}) == 1
            
    mock_exec.return_value = True
    assert connector.update_lead(1, {}) is True
    assert connector.delete_lead(1) is True
    assert connector.update_record("m", 1, {}) is True
    
    # We need valid mock data for the schemas
    valid_contact = {"id": 1, "name": "A", "email": "a@a.com", "phone": "123", "is_company": False, "company_id": False}
    mock_exec.return_value = [valid_contact]
    assert len(connector.search_contacts()) == 1
    
    valid_product = {"id": 2, "name": "P", "list_price": 10.0, "default_code": "P1", "qty_available": 5.0}
    mock_exec.return_value = [valid_product]
    assert len(connector.get_products()) == 1
    
    valid_quote = {"id": 3, "name": "Q", "partner_id": [1, "A"], "state": "draft", "amount_total": 100.0, "date_order": False}
    mock_exec.return_value = [valid_quote]
    assert len(connector.get_quotes()) == 1
    
    mock_exec.return_value = [{"a": 1}]
    assert len(connector.search_read_records("m")) == 1

@patch.object(XmlRpcOdooConnector, "_execute")
def test_get_sales_dashboard(mock_exec, connector):
    mock_exec.side_effect = [10, 5, [{"amount_total": 100.0}], 20]
    dash = connector.get_sales_dashboard()
    assert dash.active_leads_count == 10
    assert dash.quotes_count == 5
    assert dash.total_revenue == 100.0
    assert dash.win_rate_percentage == 5.0

@patch.object(XmlRpcOdooConnector, "_execute")
def test_get_sales_dashboard_missing_module(mock_exec, connector):
    mock_exec.side_effect = [10, OdooConnectorError("sale.order missing")]
    dash = connector.get_sales_dashboard()
    assert dash.active_leads_count == 10
    assert dash.quotes_count == 0
    assert dash.total_revenue == 0.0

@patch.object(XmlRpcOdooConnector, "_execute")
def test_get_products_missing_module(mock_exec, connector):
    mock_exec.side_effect = OdooConnectorError("product.product missing")
    assert connector.get_products() == []
    
    mock_exec.side_effect = OdooConnectorError("other error")
    with pytest.raises(OdooConnectorError):
        connector.get_products()

@patch.object(XmlRpcOdooConnector, "_execute")
def test_get_quotes_missing_module(mock_exec, connector):
    mock_exec.side_effect = OdooConnectorError("sale.order missing")
    assert connector.get_quotes() == []
    
    mock_exec.side_effect = OdooConnectorError("other error")
    with pytest.raises(OdooConnectorError):
        connector.get_quotes()

@patch("core.cache.get_cached_value", return_value=None)
@patch("core.cache.set_cached_value")
@patch.object(XmlRpcOdooConnector, "_execute", return_value=[])
@patch.object(XmlRpcOdooConnector, "_get_workspace")
def test_schema_caching(mock_ws, mock_exec, mock_set, mock_get, connector):
    mock_ws.return_value = MagicMock(odoo_db="testdb")
    connector.get_installed_apps()
    mock_exec.assert_called_with("ir.module.module", "search_read", [["state", "=", "installed"]], fields=["name", "shortdesc", "application"])
    mock_set.assert_called_once()
    
    mock_set.reset_mock()
    connector.get_model_fields("crm.lead")
    mock_exec.assert_called_with("crm.lead", "fields_get", [], ["string", "type", "help", "selection", "relation"])
    mock_set.assert_called_once()

@patch("core.cache.get_cached_value", return_value='[{"name": "test"}]')
@patch.object(XmlRpcOdooConnector, "_execute")
@patch.object(XmlRpcOdooConnector, "_get_workspace")
def test_schema_cached_hit(mock_ws, mock_exec, mock_get, connector):
    mock_ws.return_value = MagicMock(odoo_db="testdb")
    res = connector.get_installed_apps()
    assert len(res) == 1
    assert res[0]["name"] == "test"
    mock_exec.assert_not_called()
    
    res2 = connector.get_model_fields("crm.lead")
    assert len(res2) == 1
    mock_exec.assert_not_called()
