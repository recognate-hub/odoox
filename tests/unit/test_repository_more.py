import pytest
from unittest.mock import MagicMock
from repositories.odoo import OdooRepository
from odoo.interface import OdooConnectorInterface

@pytest.fixture
def repo():
    return OdooRepository(MagicMock(spec=OdooConnectorInterface))

def test_get_active_leads_no_filters(repo):
    repo.get_active_leads()
    repo.connector.get_leads.assert_called_once_with(domain=[["type", "=", "opportunity"]], limit=100)

def test_get_active_leads_all_filters(repo):
    repo.get_active_leads(name_query="test", stage_id=2, limit=50)
    repo.connector.get_leads.assert_called_once_with(
        domain=[["type", "=", "opportunity"], ["name", "ilike", "test"], ["stage_id", "=", 2]],
        limit=50
    )

def test_create_contact_full(repo):
    repo.create_contact("John", email="j@j.com", phone="123", is_company=True)
    repo.connector.create_contact.assert_called_once_with({
        "name": "John", "is_company": True, "email": "j@j.com", "phone": "123"
    })

def test_create_contact_minimal(repo):
    repo.create_contact("Jane")
    repo.connector.create_contact.assert_called_once_with({
        "name": "Jane", "is_company": False
    })

def test_create_product_full(repo):
    repo.create_product("Prod", 10.0, default_code="P1", type_code="product")
    repo.connector.create_product.assert_called_once_with({
        "name": "Prod", "list_price": 10.0, "detailed_type": "product", "default_code": "P1"
    })

def test_create_product_minimal(repo):
    repo.create_product("Prod", 10.0)
    repo.connector.create_product.assert_called_once_with({
        "name": "Prod", "list_price": 10.0, "detailed_type": "service"
    })

def test_get_recent_quotes_no_partner(repo):
    repo.get_recent_quotes(limit=10)
    repo.connector.get_quotes.assert_called_once_with(domain=[], limit=10)

def test_create_quote(repo):
    repo.create_quote(1, [{"product_id": 2, "quantity": 1}, {"product_id": 3, "quantity": 2, "price_unit": 5.0}])
    repo.connector.create_quote.assert_called_once_with({
        "partner_id": 1,
        "order_line": [
            [0, 0, {"product_id": 2, "product_uom_qty": 1}],
            [0, 0, {"product_id": 3, "product_uom_qty": 2, "price_unit": 5.0}]
        ]
    })

def test_update_lead(repo):
    repo.update_lead(1, {"name": "test"})
    repo.connector.update_lead.assert_called_once_with(1, {"name": "test"})

def test_create_invoice(repo):
    repo.create_invoice(1, 100.0, "test")
    repo.connector.create_invoice.assert_called_once_with({
        "partner_id": 1,
        "move_type": "out_invoice",
        "invoice_line_ids": [
            [0, 0, {"name": "test", "price_unit": 100.0, "quantity": 1}]
        ]
    })

def test_send_email(repo):
    repo.send_email("test@test", "subj", "body")
    repo.connector.send_email.assert_called_once_with({
        "email_to": "test@test", "subject": "subj", "body_html": "body", "state": "outgoing"
    })

def test_search_read_records(repo):
    repo.search_read_records("model")
    repo.connector.search_read_records.assert_called_once_with("model", domain=None, fields=None, limit=100, offset=0)

def test_create_record(repo):
    repo.create_record("model", {})
    repo.connector.create_record.assert_called_once_with("model", {})

def test_update_record(repo):
    repo.update_record("model", 1, {})
    repo.connector.update_record.assert_called_once_with("model", 1, {})

def test_get_installed_apps(repo):
    repo.get_installed_apps()
    repo.connector.get_installed_apps.assert_called_once()

def test_get_model_fields(repo):
    repo.get_model_fields("model")
    repo.connector.get_model_fields.assert_called_once_with("model")
