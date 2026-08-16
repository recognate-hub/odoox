from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture(autouse=True)
def mock_security():
    with patch("mcp_app.security.get_current_user_context") as mock_get_user:
        mock_user = MagicMock()
        mock_user.user_id = "test_user"
        mock_user.role = "Admin"
        mock_get_user.return_value = mock_user
        
        with patch("mcp_app.security.PolicyEngine.is_allowed", return_value=True):
            with patch("mcp_app.security.PolicyEngine.is_model_allowed", return_value=True):
                yield

@pytest.fixture
def mock_repo_service():
    import mcp_app.server
    original = mcp_app.server._get_tenant_service
    mock_repo = MagicMock()
    mock_service = MagicMock()
    mock_get_tenant = MagicMock(return_value=(mock_repo, mock_service))
    mcp_app.server._get_tenant_service = mock_get_tenant
    yield mock_repo, mock_service
    mcp_app.server._get_tenant_service = original

def test_get_leads(mock_repo_service):
    repo, _ = mock_repo_service
    mock_lead = MagicMock()
    mock_lead.model_dump.return_value = {"id": 1, "name": "L"}
    repo.get_active_leads.return_value = [mock_lead]
    
    from mcp_app.tools.crm import get_leads
    res = get_leads("test", 1, 10)
    assert res == [{"id": 1, "name": "L"}]
    repo.get_active_leads.assert_called_once_with(name_query="test", stage_id=1, limit=10)

def test_create_lead(mock_repo_service):
    repo, _ = mock_repo_service
    repo.create_lead.return_value = 42
    
    from mcp_app.tools.crm import create_lead
    res = create_lead(name="test")
    assert res == {"status": "success", "lead_id": 42}
    repo.create_lead.assert_called_once()

def test_update_lead(mock_repo_service):
    repo, _ = mock_repo_service
    repo.update_lead.return_value = True
    
    from mcp_app.tools.crm import update_lead
    res = update_lead(lead_id=1, data={})
    assert res == {"status": "success"}
    repo.update_lead.assert_called_once()

def test_log_crm_note(mock_repo_service):
    repo, _ = mock_repo_service
    repo.log_activity.return_value = 99
    
    from mcp_app.tools.crm import log_crm_note
    res = log_crm_note(res_model="crm.lead", res_id=1, summary="note")
    assert res == {"status": "success", "activity_id": 99}
    repo.log_activity.assert_called_once()

def test_search_customer(mock_repo_service):
    repo, _ = mock_repo_service
    mock_contact = MagicMock()
    mock_contact.model_dump.return_value = {"id": 1}
    repo.search_contacts_by_name.return_value = [mock_contact]
    
    from mcp_app.tools.contacts import search_customer
    res = search_customer("query")
    assert res == [{"id": 1}]
    repo.search_contacts_by_name.assert_called_once()

def test_create_contact(mock_repo_service):
    repo, _ = mock_repo_service
    repo.create_contact.return_value = 55
    
    from mcp_app.tools.contacts import create_contact
    res = create_contact(name="c")
    assert res == {"status": "success", "partner_id": 55}
    repo.create_contact.assert_called_once()

def test_get_customer_details(mock_repo_service):
    _, service = mock_repo_service
    service.get_customer_summary_data.return_value = {"contact": {}}
    
    from mcp_app.tools.contacts import get_customer_details
    res = get_customer_details(1)
    assert res == {"contact": {}}
    service.get_customer_summary_data.assert_called_once()

def test_get_products(mock_repo_service):
    repo, _ = mock_repo_service
    mock_prod = MagicMock()
    mock_prod.model_dump.return_value = {"id": 1}
    repo.search_products.return_value = [mock_prod]
    
    from mcp_app.tools.inventory import get_products
    res = get_products("query")
    assert res == [{"id": 1}]
    repo.search_products.assert_called_once()

def test_create_product(mock_repo_service):
    repo, _ = mock_repo_service
    repo.create_product.return_value = 88
    
    from mcp_app.tools.inventory import create_product
    res = create_product(name="P", list_price=10.0)
    assert res == {"status": "success", "product_id": 88}
    repo.create_product.assert_called_once()

def test_get_recent_quotes(mock_repo_service):
    repo, _ = mock_repo_service
    mock_q = MagicMock()
    mock_q.model_dump.return_value = {"id": 1}
    repo.get_recent_quotes.return_value = [mock_q]
    
    from mcp_app.tools.sales import get_recent_quotes
    res = get_recent_quotes()
    assert res == [{"id": 1}]
    repo.get_recent_quotes.assert_called_once()

def test_create_quote(mock_repo_service):
    repo, _ = mock_repo_service
    repo.create_quote.return_value = 77
    
    from mcp_app.tools.sales import create_quote
    res = create_quote(partner_id=1, order_lines=[{"product_id":1, "quantity":1}])
    assert res == {"status": "success", "quote_id": 77}
    repo.create_quote.assert_called_once()

def test_revenue_report(mock_repo_service):
    repo, _ = mock_repo_service
    mock_dash = MagicMock()
    mock_dash.model_dump.return_value = {"rev": 100}
    repo.get_dashboard.return_value = mock_dash
    
    from mcp_app.tools.dashboards import revenue_report
    assert revenue_report() == {"rev": 100}

def test_get_pipeline_forecast_data(mock_repo_service):
    _, service = mock_repo_service
    service.get_pipeline_data.return_value = []
    
    from mcp_app.tools.dashboards import get_pipeline_forecast_data
    assert get_pipeline_forecast_data() == []
    service.get_pipeline_data.assert_called_once()

def test_schedule_meeting(mock_repo_service):
    _, service = mock_repo_service
    service.create_meeting.return_value = {"status": "success", "meeting_id": 1}
    
    from mcp_app.tools.calendar import schedule_meeting
    res = schedule_meeting(name="N", start="2026-08-01T10:00:00Z", stop="2026-08-01T11:00:00Z", partner_ids=[1])
    assert res == {"status": "success", "meeting_id": 1}
    service.create_meeting.assert_called_once()

def test_get_lead_context(mock_repo_service):
    _, service = mock_repo_service
    service.get_lead_context.return_value = {}
    
    from mcp_app.tools.crm import get_lead_context
    assert get_lead_context(1) == {}

def test_create_invoice(mock_repo_service):
    repo, _ = mock_repo_service
    repo.create_invoice.return_value = 66
    
    from mcp_app.tools.invoicing import create_invoice
    assert create_invoice(partner_id=1, amount=10.0) == {"status": "success", "invoice_id": 66}

def test_send_email(mock_repo_service):
    repo, _ = mock_repo_service
    repo.send_email.return_value = 55
    
    from mcp_app.tools.discuss import send_email
    assert send_email(email_to="a@a", subject="s", body="b") == {"status": "success", "mail_id": 55}

def test_search_read_records(mock_repo_service):
    repo, _ = mock_repo_service
    repo.search_read_records.return_value = []
    
    from mcp_app.tools.generic import search_read_records
    assert search_read_records(model="m") == []
    assert search_read_records(model="m", limit=300) == [] # Should clip to 200
    repo.search_read_records.assert_called_with("m", domain=None, fields=None, limit=200, offset=0)

def test_search_read_records_error(mock_repo_service):
    repo, _ = mock_repo_service
    repo.search_read_records.side_effect = Exception("err")
    from mcp_app.tools.generic import search_read_records
    result = search_read_records(model="m")
    assert result["status"] == "error"
    assert "Unexpected error" in result["message"]

def test_get_installed_apps(mock_repo_service):
    repo, _ = mock_repo_service
    repo.get_installed_apps.return_value = []
    from mcp_app.tools.generic import get_installed_apps
    assert get_installed_apps() == []
    
    repo.get_installed_apps.side_effect = Exception("err")
    result = get_installed_apps()
    assert result["status"] == "error"
    assert "Unexpected error" in result["message"]

def test_get_model_fields(mock_repo_service):
    repo, _ = mock_repo_service
    repo.get_model_fields.return_value = {}
    from mcp_app.tools.generic import get_model_fields
    assert get_model_fields(model="m") == {}
    
    repo.get_model_fields.side_effect = Exception("err")
    assert get_model_fields(model="m") == {"status": "error", "message": "err"}

def test_execute_model_method(mock_repo_service):
    repo, _ = mock_repo_service
    repo.execute_method.return_value = "success"
    
    from mcp_app.tools.generic import execute_model_method
    assert execute_model_method(model="sale.order", method="action_confirm", args=[1]) == "success"
    repo.execute_method.assert_called_once_with("sale.order", "action_confirm", [1], {})
    
    repo.execute_method.side_effect = Exception("err")
    result = execute_model_method(model="sale.order", method="action_confirm")
    assert result["status"] == "error"
    assert "Unexpected error" in result["message"]
