from typing import Any

from core.logger import get_logger
from repositories.odoo import OdooRepository

logger = get_logger(__name__)

class PurchaseService:
    def __init__(self, odoo_repo: OdooRepository):
        self.odoo = odoo_repo

    def create_purchase_order(self, partner_id: int, order_lines: list[dict]) -> dict[str, Any]:
        po_id = self.odoo.create_purchase_order(partner_id, order_lines)
        return {"status": "success", "purchase_order_id": po_id}

    def get_purchase_orders(self, partner_id: int | None = None, limit: int = 20) -> list[dict[str, Any]]:
        return self.odoo.get_purchase_orders(partner_id, limit)

    def update_purchase_order(self, po_id: int, data: dict[str, Any]) -> dict[str, Any]:
        success = self.odoo.update_purchase_order(po_id, data)
        return {"status": "success"} if success else {"status": "error", "message": "Update failed"}

    def confirm_purchase_order(self, po_id: int) -> dict[str, Any]:
        self.odoo.confirm_purchase_order(po_id)
        return {"status": "success", "message": f"Purchase order {po_id} confirmed."}

    def get_purchase_order_lines(self, po_id: int) -> list[dict[str, Any]]:
        return self.odoo.get_purchase_order_lines(po_id)

    def get_vendor_bills(self, partner_id: int | None = None, limit: int = 50) -> list[dict[str, Any]]:
        return self.odoo.get_vendor_bills(partner_id, limit)
