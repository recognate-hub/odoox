import sys
from typing import Any

filepath = "services/planning.py"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

new_method = """
    def create_planned_manufacturing_orders(self, orders: list[dict[str, Any]]) -> list[int]:
        \"\"\"
        Creates Manufacturing Orders in bulk.
        orders should be a list of dicts: [{"product_id": int, "qty": float}]
        \"\"\"
        if not orders:
            return []
            
        create_data = []
        for order in orders:
            create_data.append({
                "product_id": order["product_id"],
                "product_qty": order["qty"],
                # We could set date_planned_start or origin if we want
                "origin": "AI Production Plan"
            })
            
        return self.odoo.create_records("mrp.production", create_data)
"""

if "def create_planned_manufacturing_orders" not in content:
    content += new_method
    
with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
print("Updated services/planning.py")
