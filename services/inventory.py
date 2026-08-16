from typing import Any

from core.logger import get_logger
from repositories.odoo import OdooRepository

logger = get_logger(__name__)

class InventoryService:
    def __init__(self, odoo_repo: OdooRepository):
        self.odoo = odoo_repo

    def create_stock_move(self, name: str, product_id: int, product_uom_qty: float, location_id: int, location_dest_id: int) -> dict[str, Any]:
        move_id = self.odoo.create_stock_move(name, product_id, product_uom_qty, location_id, location_dest_id)
        return {"status": "success", "stock_move_id": move_id}

    def get_inventory_valuation(self, product_id: int | None = None) -> list[dict[str, Any]]:
        return self.odoo.get_inventory_valuation(product_id)
