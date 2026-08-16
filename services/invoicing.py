from typing import Any

from core.logger import get_logger
from repositories.odoo import OdooRepository

logger = get_logger(__name__)

class InvoicingService:
    def __init__(self, odoo_repo: OdooRepository):
        self.odoo = odoo_repo

    def create_invoice(self, partner_id: int, amount: float, description: str) -> dict[str, Any]:
        invoice_id = self.odoo.create_invoice(partner_id, amount, description)
        return {"status": "success", "invoice_id": invoice_id}

    def get_invoices(self, partner_id: int | None = None, state: str | None = None, limit: int = 50) -> list[dict[str, Any]]:
        return self.odoo.get_invoices(partner_id, state, limit)

    def post_invoice(self, invoice_id: int) -> dict[str, Any]:
        self.odoo.post_invoice(invoice_id)
        return {"status": "success", "message": f"Invoice {invoice_id} posted."}

    def register_payment(self, invoice_id: int, amount: float, journal_id: int) -> dict[str, Any]:
        result = self.odoo.register_payment(invoice_id, amount, journal_id)
        return {"status": "success", "result": result}

    def get_payment_journals(self) -> list[dict[str, Any]]:
        return self.odoo.get_payment_journals()
