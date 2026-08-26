from unittest.mock import MagicMock, patch
import pytest
import json


@pytest.fixture(autouse=True)
def mock_security():
    with patch("mcp_app.security.get_current_user_context") as mock_get_user:
        mock_user = MagicMock()
        mock_user.user_id = "test_user"
        mock_user.role = "Admin"
        mock_get_user.return_value = mock_user

        with patch("mcp_app.security.PolicyEngine.is_allowed", return_value=True):
            with patch(
                "mcp_app.security.PolicyEngine.is_model_allowed", return_value=True
            ):
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

    res = get_leads(name_query="test", stage_id=1, limit=10)
    assert res == [{"id": 1, "name": "L"}]
    repo.get_active_leads.assert_called_once_with(
        name_query="test", stage_id=1, user_id=None, date_from=None, date_to=None, limit=10
    )


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
    repo.search_contacts_by_name.assert_called_once_with("query", limit=20)


def test_get_customer_details(mock_repo_service):
    _, service = mock_repo_service
    service.get_customer_summary_data.return_value = {"contact": {}}

    from mcp_app.tools.contacts import get_customer_details

    res = get_customer_details(1)
    assert res == {"contact": {}}
    service.get_customer_summary_data.assert_called_once_with(1)


def test_get_recent_quotes(mock_repo_service):
    repo, _ = mock_repo_service
    mock_q = MagicMock()
    mock_q.model_dump.return_value = {"id": 1}
    repo.get_recent_quotes.return_value = [mock_q]

    from mcp_app.tools.sales import get_recent_quotes

    res = get_recent_quotes()
    assert res == [{"id": 1}]
    repo.get_recent_quotes.assert_called_once()


def test_get_sales_dashboard(mock_repo_service):
    repo, _ = mock_repo_service
    mock_dash = MagicMock()
    mock_dash.model_dump.return_value = {"rev": 100}
    repo.get_dashboard.return_value = mock_dash

    from mcp_app.tools.generic import get_sales_dashboard

    assert get_sales_dashboard() == {"rev": 100}


def test_get_lead_context(mock_repo_service):
    _, service = mock_repo_service
    service.get_lead_context.return_value = {"id": 1, "name": "Lead"}

    from mcp_app.tools.crm import get_lead_context

    assert get_lead_context(1) == {"id": 1, "name": "Lead"}


def test_search_read_records(mock_repo_service):
    repo, _ = mock_repo_service
    repo.search_read_records.return_value = []

    from mcp_app.tools.generic import search_read_records

    assert search_read_records(model="res.partner", fields=["name"]) == []
    assert search_read_records(model="res.partner", fields=["name"], limit=300) == []  # Clips to 200
    repo.search_read_records.assert_called_with(
        "res.partner", domain=None, fields=["name"], limit=200, offset=0, expand_fields=None
    )


def test_get_installed_apps(mock_repo_service):
    repo, _ = mock_repo_service
    repo.get_installed_apps.return_value = [{"name": "crm"}]
    from mcp_app.tools.generic import get_installed_apps

    assert get_installed_apps() == [{"name": "crm"}]


def test_get_model_fields(mock_repo_service):
    repo, _ = mock_repo_service
    repo.get_model_fields.return_value = {"name": {"type": "char"}}
    from mcp_app.tools.generic import get_model_fields

    assert get_model_fields(model="res.partner") == {"name": {"type": "char"}}


def test_execute_model_method(mock_repo_service):
    repo, _ = mock_repo_service
    repo.execute_method.return_value = "success"

    from mcp_app.tools.generic import execute_model_method

    assert (
        execute_model_method(model="sale.order", method="action_confirm", args=[1])
        == "success"
    )
    repo.execute_method.assert_called_once_with("sale.order", "action_confirm", [1], {})


def test_mcp_prompts():
    from mcp_app.prompts import (
        daily_business_briefing,
        crm_lead_prioritization,
        manufacturing_bottleneck_audit,
        financial_health_audit,
        inventory_reorder_recommendation,
    )

    briefing = daily_business_briefing()
    assert "Daily Business Briefing" in briefing
    assert "analyze_pipeline_metrics" in briefing

    crm_prompt = crm_lead_prioritization(min_expected_revenue=5000.0)
    assert "5000" in crm_prompt

    mfg_prompt = manufacturing_bottleneck_audit()
    assert "bottleneck" in mfg_prompt.lower()

    fin_prompt = financial_health_audit()
    assert "invoices" in fin_prompt.lower()

    inv_prompt = inventory_reorder_recommendation()
    assert "purchase order" in inv_prompt.lower()


def test_mcp_resources(mock_repo_service):
    repo, _ = mock_repo_service
    repo.search_read_records.return_value = [{"model": "sale.order", "name": "Sales"}]
    
    from mcp_app.resources import (
        get_system_status_resource,
        get_schema_models_resource,
        get_realtime_kpis_resource,
    )

    schema_res = get_schema_models_resource()
    parsed_schema = json.loads(schema_res)
    assert "models" in parsed_schema
