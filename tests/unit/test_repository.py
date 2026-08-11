"""Unit tests for the OdooRepository layer."""
from unittest.mock import MagicMock

import pytest

from odoo.interface import OdooConnectorInterface
from repositories.odoo import OdooRepository
from schemas.odoo import (
    OdooContact,
    OdooLead,
    OdooProduct,
    OdooQuote,
    OdooSalesDashboard,
)


@pytest.fixture
def mock_connector():
    """Create a mock OdooConnectorInterface."""
    return MagicMock(spec=OdooConnectorInterface)


@pytest.fixture
def repo(mock_connector):
    return OdooRepository(mock_connector)


# --- get_active_leads ---

def test_get_active_leads(repo, mock_connector):
    mock_connector.get_leads.return_value = [
        OdooLead(id=1, name="Test Lead", expected_revenue=1000.0, probability=50.0)
    ]
    leads = repo.get_active_leads(limit=5)

    assert len(leads) == 1
    assert leads[0].id == 1
    assert leads[0].name == "<untrusted_crm_data>Test Lead</untrusted_crm_data>"
    mock_connector.get_leads.assert_called_once_with(
        domain=[["type", "=", "opportunity"]], limit=5
    )


def test_get_active_leads_empty(repo, mock_connector):
    mock_connector.get_leads.return_value = []
    leads = repo.get_active_leads()
    assert leads == []


# --- get_lead_by_id ---

def test_get_lead_by_id_found(repo, mock_connector):
    mock_connector.get_leads.return_value = [
        OdooLead(id=42, name="Found Lead", expected_revenue=5000.0, probability=80.0)
    ]
    lead = repo.get_lead_by_id(42)

    assert lead is not None
    assert lead.id == 42
    assert lead.name == "<untrusted_crm_data>Found Lead</untrusted_crm_data>"
    mock_connector.get_leads.assert_called_once_with(
        domain=[["id", "=", 42]], limit=1
    )


def test_get_lead_by_id_not_found(repo, mock_connector):
    mock_connector.get_leads.return_value = []
    lead = repo.get_lead_by_id(999)
    assert lead is None


# --- search_contacts_by_name ---

def test_search_contacts_by_name(repo, mock_connector):
    mock_connector.search_contacts.return_value = [
        OdooContact(id=2, name="John Doe", email="john@example.com")
    ]
    contacts = repo.search_contacts_by_name("John")

    assert len(contacts) == 1
    assert contacts[0].id == 2
    assert contacts[0].name == "<untrusted_crm_data>John Doe</untrusted_crm_data>"
    mock_connector.search_contacts.assert_called_once_with(
        domain=[["name", "ilike", "John"]], limit=20
    )


def test_search_contacts_by_name_custom_limit(repo, mock_connector):
    mock_connector.search_contacts.return_value = []
    repo.search_contacts_by_name("Jane", limit=5)
    mock_connector.search_contacts.assert_called_once_with(
        domain=[["name", "ilike", "Jane"]], limit=5
    )


# --- search_products ---

def test_search_products(repo, mock_connector):
    mock_connector.get_products.return_value = [
        OdooProduct(id=3, name="Product A", list_price=49.99, qty_available=100)
    ]
    products = repo.search_products("Prod")

    assert len(products) == 1
    assert products[0].id == 3
    assert products[0].name == "<untrusted_crm_data>Product A</untrusted_crm_data>"
    mock_connector.get_products.assert_called_once_with(
        domain=["|", ["name", "ilike", "Prod"], ["default_code", "ilike", "Prod"]], limit=20
    )


# --- get_recent_quotes ---

def test_get_recent_quotes_no_partner(repo, mock_connector):
    mock_connector.get_quotes.return_value = [
        OdooQuote(id=10, name="S00001", state="draft", amount_total=1500.0)
    ]
    quotes = repo.get_recent_quotes()

    assert len(quotes) == 1
    assert quotes[0].name == "<untrusted_crm_data>S00001</untrusted_crm_data>"
    mock_connector.get_quotes.assert_called_once_with(domain=[], limit=10)


def test_get_recent_quotes_with_partner(repo, mock_connector):
    mock_connector.get_quotes.return_value = []
    repo.get_recent_quotes(partner_id=5, limit=3)
    mock_connector.get_quotes.assert_called_once_with(
        domain=[["partner_id", "=", 5]], limit=3
    )


# --- create_lead ---

def test_create_lead_all_fields(repo, mock_connector):
    mock_connector.create_lead.return_value = 10
    lead_id = repo.create_lead("New Lead", email="e@test.com", phone="123", description="Desc")

    assert lead_id == 10
    mock_connector.create_lead.assert_called_once_with({
        "name": "New Lead",
        "type": "opportunity",
        "email_from": "e@test.com",
        "phone": "123",
        "description": "Desc"
    })


def test_create_lead_minimal(repo, mock_connector):
    mock_connector.create_lead.return_value = 11
    lead_id = repo.create_lead("Minimal Lead")

    assert lead_id == 11
    mock_connector.create_lead.assert_called_once_with({
        "name": "Minimal Lead",
        "type": "opportunity"
    })


# --- log_activity ---

def test_log_activity(repo, mock_connector):
    mock_connector.create_activity.return_value = 6
    activity_id = repo.log_activity("crm.lead", 1, "Follow up call")

    assert activity_id == 6
    mock_connector.create_activity.assert_called_once_with({
        "model": "crm.lead",
        "res_id": 1,
        "body": "Follow up call",
        "message_type": "comment",
        "subtype_id": 2
    })


def test_log_activity_custom_type(repo, mock_connector):
    mock_connector.create_activity.return_value = 7
    activity_id = repo.log_activity("res.partner", 10, "Send proposal", activity_type_id=2)

    assert activity_id == 7
    mock_connector.create_activity.assert_called_once_with({
        "model": "res.partner",
        "res_id": 10,
        "body": "Send proposal",
        "message_type": "comment",
        "subtype_id": 2
    })


# --- schedule_meeting ---

def test_schedule_meeting(repo, mock_connector):
    mock_connector.schedule_meeting.return_value = 5
    meeting_id = repo.schedule_meeting(
        "Kickoff Meeting", "2026-08-01 10:00:00", "2026-08-01 11:00:00", [1, 2]
    )

    assert meeting_id == 5
    mock_connector.schedule_meeting.assert_called_once_with({
        "name": "Kickoff Meeting",
        "start": "2026-08-01 10:00:00",
        "stop": "2026-08-01 11:00:00",
        "partner_ids": [[6, 0, [1, 2]]]
    })


# --- get_dashboard ---

def test_get_dashboard(repo, mock_connector):
    mock_connector.get_sales_dashboard.return_value = OdooSalesDashboard(
        total_revenue=50000.0, active_leads_count=10,
        quotes_count=5, win_rate_percentage=25.0
    )
    dashboard = repo.get_dashboard()

    assert dashboard.total_revenue == 50000.0
    assert dashboard.active_leads_count == 10
    assert dashboard.quotes_count == 5
    assert dashboard.win_rate_percentage == 25.0
    mock_connector.get_sales_dashboard.assert_called_once()
