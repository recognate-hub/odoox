import datetime
from typing import Any
from collections import defaultdict

from core.logger import get_logger
from repositories.odoo import OdooRepository

logger = get_logger(__name__)


class PlanningService:
    """
    Service to generate the Production Planning Report data.
    """

    def __init__(self, odoo: OdooRepository):
        self.odoo = odoo

    def get_production_planning_data(self, months: int = 4) -> list[dict[str, Any]]:
        today = datetime.date.today()
        start_date = today - datetime.timedelta(days=30 * months)
        start_date_str = start_date.strftime("%Y-%m-%d")

        # 1. Fetch Sales over the last N months to calculate MOQ
        so_domain = [
            ("state", "in", ["sale", "done"]),
            ("date_order", ">=", start_date_str),
        ]
        # We only need the ids to filter order lines
        so_records = self.odoo.search_read_records(
            "sale.order", so_domain, ["id"], limit=5000
        )
        so_ids = [so["id"] for so in so_records]

        sol_domain = [("order_id", "in", so_ids)]
        sol_records = []
        if so_ids:
            sol_records = self.odoo.search_read_records(
                "sale.order.line",
                sol_domain,
                ["product_id", "product_uom_qty"],
                limit=10000,
            )

        # 2. Fetch Customer Pending Quantity
        # Lines not fully delivered. In Odoo, qty_delivered < product_uom_qty isn't supported directly in domain
        # So we fetch lines where state is sale and compute it
        pending_domain = [("state", "=", "sale")]
        pending_lines = self.odoo.search_read_records(
            "sale.order.line",
            pending_domain,
            [
                "product_id",
                "product_uom_qty",
                "qty_delivered",
                "order_partner_id",
                "order_id",
            ],
            limit=10000,
        )

        # 3. Finished Stock (Internal Locations)
        stock_domain = [("location_id.usage", "=", "internal")]
        quants = self.odoo.search_read_records(
            "stock.quant", stock_domain, ["product_id", "quantity"], limit=10000
        )

        # 4. WIP Stock (Workorders)
        wip_domain = [("state", "not in", ["cancel", "done"])]
        workorders = self.odoo.search_read_records(
            "mrp.workorder",
            wip_domain,
            ["product_id", "workcenter_id", "qty_production"],
            limit=10000,
        )

        # --- AGGREGATION ---
        products = defaultdict(
            lambda: {
                "p": "",  # Name
                "s": 0.0,  # Finished Stock
                "m": 0.0,  # MOQ (Average per month)
                "o": 0.0,  # Pending Order Qty
                "pl": 0.0,  # Planning = m - s + o
                "wip": 0.0,  # Total WIP
                "st": defaultdict(float),  # Stage-wise WIP
                "cu": defaultdict(float),  # Customer Pending Orders
            }
        )

        def get_product_name(pid):
            if isinstance(pid, list) and len(pid) == 2:
                return pid[1]
            return str(pid)

        # Aggregate Sales for MOQ
        sales_qty = defaultdict(float)
        for line in sol_records:
            pid = line.get("product_id")
            if pid:
                p_name = get_product_name(pid)
                products[p_name]["p"] = p_name
                sales_qty[p_name] += float(line.get("product_uom_qty", 0.0))

        for p_name, total_qty in sales_qty.items():
            products[p_name]["m"] = round(total_qty / months, 2)

        # Aggregate Pending Orders
        for line in pending_lines:
            pid = line.get("product_id")
            if pid:
                qty_ordered = float(line.get("product_uom_qty", 0.0))
                qty_delivered = float(line.get("qty_delivered", 0.0))
                pending = qty_ordered - qty_delivered
                if pending > 0:
                    p_name = get_product_name(pid)
                    partner_id = line.get("order_partner_id")
                    customer_name = (
                        get_product_name(partner_id) if partner_id else "Unknown"
                    )

                    products[p_name]["p"] = p_name
                    products[p_name]["o"] += pending
                    products[p_name]["cu"][customer_name] += pending

        # Aggregate Finished Stock
        for q in quants:
            pid = q.get("product_id")
            if pid:
                qty = float(q.get("quantity", 0.0))
                if qty > 0:
                    p_name = get_product_name(pid)
                    products[p_name]["p"] = p_name
                    products[p_name]["s"] += qty

        # Aggregate WIP Stock
        for wo in workorders:
            pid = wo.get("product_id")
            wc = wo.get("workcenter_id")
            if pid and wc:
                p_name = get_product_name(pid)
                wc_name = get_product_name(wc)
                qty = float(wo.get("qty_production", 0.0))

                products[p_name]["p"] = p_name
                products[p_name]["wip"] += qty
                products[p_name]["st"][wc_name] += qty

        # Final Calculation
        result = []
        for p_name, data in products.items():
            if not data["p"]:
                continue

            data["s"] = round(data["s"], 2)
            data["o"] = round(data["o"], 2)
            data["wip"] = round(data["wip"], 2)

            # Planning = MOQ - Stock + Pending Order
            planning = data["m"] - data["s"] + data["o"]
            data["pl"] = round(planning, 2)

            # Format dictionaries to lists where necessary if needed, but dicts are fine
            data["st"] = dict(data["st"])

            # Format cu to match expected HTML structure: [{"c": "Name", "q": 100}]
            cu_list = [{"c": k, "q": round(v, 2)} for k, v in data["cu"].items()]
            data["cu"] = sorted(cu_list, key=lambda x: x["q"], reverse=True)

            result.append(data)

        # Sort by planning qty descending
        result.sort(key=lambda x: x["pl"], reverse=True)
        return result

    def create_planned_manufacturing_orders(
        self, orders: list[dict[str, Any]]
    ) -> list[int]:
        """
        Creates Manufacturing Orders in bulk.
        orders should be a list of dicts: [{"product_id": int, "qty": float}]
        """
        if not orders:
            return []

        create_data = []
        for order in orders:
            create_data.append(
                {
                    "product_id": order["product_id"],
                    "product_qty": order["qty"],
                    # We could set date_planned_start or origin if we want
                    "origin": "AI Production Plan",
                }
            )

        return self.odoo.create_records("mrp.production", create_data)
