"""Unit tests for the CRMService business logic layer."""
import pytest
from unittest.mock import MagicMock

from repositories.odoo import OdooRepository
from services.crm import CRMService
from schemas.odoo import OdooLead, OdooContact, OdooQuote
from core.exceptions import OdooResourceNotFoundError


@pytest.fixture
def mock_odoo_repo():
    mock = MagicMock(spec=OdooRepository)
    # Ensure connector sub-mock is available
    mock.connector = MagicMock()
    return mock


def test_get_lead_context_success(mock_odoo_repo):
    mock_lead = OdooLead(
        id=1, name="Test Lead",
        expected_revenue=5000.0, probability=50.0,
        description="A great opportunity"
    )
    mock_odoo_repo.get_lead_by_id.return_value = mock_lead

    service = CRMService(mock_odoo_repo)
    result = service.get_lead_context(1)

    assert result["name"] == "Test Lead"
    assert result["expected_revenue"] == 5000.0
    mock_odoo_repo.get_lead_by_id.assert_called_once_with(1)


def test_get_lead_context_not_found(mock_odoo_repo):
    mock_odoo_repo.get_lead_by_id.return_value = None

    service = CRMService(mock_odoo_repo)

    with pytest.raises(OdooResourceNotFoundError):
        service.get_lead_context(999)


def test_get_customer_summary_data_success(mock_odoo_repo):
    mock_contact = OdooContact(
        id=10, name="Alpha Corp", email="contact@alpha.com", is_company=True
    )
    mock_odoo_repo.connector.search_contacts.return_value = [mock_contact]
    mock_odoo_repo.get_recent_quotes.return_value = [
        OdooQuote(id=200, name="S00042", state="draft", amount_total=5000.0),
        OdooQuote(id=201, name="S00043", state="sale", amount_total=12000.0),
    ]

    service = CRMService(mock_odoo_repo)
    result = service.get_customer_summary_data(10)

    assert result["contact"]["name"] == "Alpha Corp"
    assert len(result["recent_quotes"]) == 2
    mock_odoo_repo.connector.search_contacts.assert_called_once()
    mock_odoo_repo.get_recent_quotes.assert_called_once_with(partner_id=10, limit=5)


def test_get_customer_summary_data_not_found(mock_odoo_repo):
    mock_odoo_repo.connector.search_contacts.return_value = []

    service = CRMService(mock_odoo_repo)

    with pytest.raises(OdooResourceNotFoundError):
        service.get_customer_summary_data(999)


def test_get_pipeline_data(mock_odoo_repo):
    mock_odoo_repo.get_active_leads.return_value = [
        OdooLead(id=1, name="Lead 1", expected_revenue=1000.0, probability=10.0),
        OdooLead(id=2, name="Lead 2", expected_revenue=2000.0, probability=20.0)
    ]

    service = CRMService(mock_odoo_repo)
    result = service.get_pipeline_data()

    assert len(result) == 2
    assert result[0]["name"] == "Lead 1"
    mock_odoo_repo.get_active_leads.assert_called_once_with(limit=50)


def test_create_meeting(mock_odoo_repo):
    mock_odoo_repo.schedule_meeting.return_value = 100
    mock_odoo_repo.log_activity.return_value = 200

    service = CRMService(mock_odoo_repo)
    result = service.create_meeting(
        name="Kickoff",
        start="2026-08-01 10:00:00",
        stop="2026-08-01 11:00:00",
        partner_ids=[1, 2],
        notes="Discussed project scope."
    )

    assert result["meeting_id"] == 100
    assert result["status"] == "success"

    # Verify meeting was scheduled
    mock_odoo_repo.schedule_meeting.assert_called_once_with(
        "Kickoff", "2026-08-01 10:00:00", "2026-08-01 11:00:00", [1, 2]
    )

    # Verify activity was logged on the meeting
    mock_odoo_repo.log_activity.assert_called_once_with(
        "calendar.event", 100, "Meeting Notes: Discussed project scope."
    )
