from typing import Any

from core.logger import get_logger
from repositories.odoo import OdooRepository

logger = get_logger(__name__)


class InventoryService:
    def __init__(self, odoo_repo: OdooRepository):
        self.odoo = odoo_repo

    def create_stock_move(
        self,
        name: str,
        product_id: int,
        product_uom_qty: float,
        location_id: int,
        location_dest_id: int,
    ) -> dict[str, Any]:
        move_id = self.odoo.create_stock_move(
            name, product_id, product_uom_qty, location_id, location_dest_id
        )
        return {"status": "success", "stock_move_id": move_id}

    def get_inventory_valuation(
        self, product_id: int | None = None, limit: int = 50, offset: int = 0
    ) -> list[dict[str, Any]]:
        return self.odoo.get_inventory_valuation(product_id, limit, offset)

    from core.cache import cache_response
    
    @cache_response(ttl_seconds=300)
    def analyze_inventory_health(self) -> dict[str, Any]:
        """
        Calculates dead stock and flags slow-moving items costing the company money.
        (ABC Analysis proxy)
        """
        # Fetch active products with stock
        products = self.odoo.search_read_records(
            "product.product",
            domain=[("qty_available", ">", 0)],
            fields=["id", "name", "qty_available", "standard_price"],
            limit=500
        )
        
        total_value = 0.0
        dead_stock = []
        healthy_stock = []
        
        for p in products:
            qty = p.get("qty_available", 0.0)
            cost = p.get("standard_price", 0.0)
            val = qty * cost
            total_value += val
            
            # Proxy for dead stock (e.g. high value tied up in low turnover, assuming for now arbitrary rule)
            if val > 1000 and qty > 50:
                dead_stock.append({
                    "product_id": p["id"],
                    "product_name": p["name"],
                    "qty_on_hand": qty,
                    "tied_up_capital": round(val, 2),
                    "health_status": "Dead Stock Risk"
                })
            else:
                healthy_stock.append({
                    "product_id": p["id"],
                    "product_name": p["name"],
                    "tied_up_capital": round(val, 2)
                })
                
        dead_stock.sort(key=lambda x: x["tied_up_capital"], reverse=True)
        
        return {
            "status": "success",
            "total_inventory_value": round(total_value, 2),
            "dead_stock_value": round(sum(d["tied_up_capital"] for d in dead_stock), 2),
            "dead_stock_items": dead_stock[:20],
            "recommendation": "Consider discounting or liquidating the top dead stock items to free up cash flow."
        }
