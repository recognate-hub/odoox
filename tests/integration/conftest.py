"""Shared fixtures for integration tests."""
from unittest.mock import MagicMock

import pytest

from schemas.odoo import (
    OdooContact,
    OdooLead,
    OdooProduct,
    OdooQuote,
    OdooSalesDashboard,
)


@pytest.fixture
def mock_odoo_connector():
    """A mock OdooConnectorInterface with pre-configured return values."""
    from odoo.interface import OdooConnectorInterface

    connector = MagicMock(spec=OdooConnectorInterface)

    # Default lead data
    connector.get_leads.return_value = [
        OdooLead(
            id=1, name="Alpha Corp Deal",
            email_from="alice@alpha.com", phone="555-0101",
            partner_id=[10, "Alpha Corp"], stage_id=[1, "Qualification"],
            expected_revenue=15000.0, probability=40.0,
            description="Enterprise software deal"
        ),
        OdooLead(
            id=2, name="Beta Inc Renewal",
            email_from="bob@beta.com", phone="555-0202",
            expected_revenue=8000.0, probability=70.0,
            description="Annual contract renewal"
        ),
    ]

    # Default contacts
    connector.search_contacts.return_value = [
        OdooContact(id=10, name="Alpha Corp", email="contact@alpha.com", is_company=True),
        OdooContact(id=11, name="Alice Smith", email="alice@alpha.com", is_company=False),
    ]

    # Default products
    connector.get_products.return_value = [
        OdooProduct(id=100, name="Widget Pro", list_price=99.99, default_code="WP-001", qty_available=50),
    ]

    # Default quotes
    connector.get_quotes.return_value = [
        OdooQuote(id=200, name="S00042", partner_id=[10, "Alpha Corp"], state="draft", amount_total=5000.0),
    ]

    # Default mutation responses
    connector.create_lead.return_value = 99
    connector.update_lead.return_value = True
    connector.delete_lead.return_value = True
    connector.create_activity.return_value = 300
    connector.schedule_meeting.return_value = 400

    # Default dashboard
    connector.get_sales_dashboard.return_value = OdooSalesDashboard(
        total_revenue=50000.0, active_leads_count=12,
        quotes_count=5, win_rate_percentage=35.0
    )

    return connector


@pytest.fixture
def odoo_repo(mock_odoo_connector):
    """An OdooRepository wired to the mock connector."""
    from repositories.odoo import OdooRepository
    return OdooRepository(mock_odoo_connector)


@pytest.fixture
def mock_claude_service():
    """A mock ClaudeService with pre-configured return values."""
    from claude.service import ClaudeService

    service = MagicMock(spec=ClaudeService)
    service.analyze_lead.return_value = "AI Lead Analysis: Strong potential for enterprise deal."
    service.summarize_meeting.return_value = "Meeting Summary: Key decisions were made."
    service.generate_email.return_value = "Dear Alice, I wanted to follow up on our conversation..."
    service.customer_summary.return_value = "Customer 360: Alpha Corp is a key account with high LTV."
    service.sales_forecast.return_value = "Forecast: Pipeline is healthy with $23K expected revenue."
    service.rewrite_email.return_value = "Rewritten: Dear valued partner..."
    service.proposal_generator.return_value = "Proposal: Executive Summary..."
    service.followup_generator.return_value = "Follow-up: Just checking in..."
    service.quotation_summary.return_value = "Quote Summary: Total value $5000..."
    service.conversation_summary.return_value = "Thread Summary: Last 3 exchanges discussed pricing."
    return service


@pytest.fixture
def crm_service(odoo_repo, mock_claude_service):
    """A CRMService wired to mock repo and mock Claude."""
    from services.crm import CRMService
    return CRMService(odoo_repo, mock_claude_service)
