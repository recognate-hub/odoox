import datetime
from typing import Any
from collections import defaultdict

from core.logger import get_logger
from repositories.odoo import OdooRepository

logger = get_logger(__name__)

class OperationsService:
    """
    Advanced analytics and operations service for Supply Chain,
    Production, Quality, and Sales Fulfillment.
    """
    def __init__(self, odoo: OdooRepository):
        self.odoo = odoo

    def get_purchase_plan(self) -> list[dict[str, Any]]:
        """
        Analyzes active Manufacturing Orders to determine raw material shortages.
        """
        # Fetch active MOs
        mo_domain = [("state", "not in", ["done", "cancel"])]
        mos = self.odoo.search_read_records("mrp.production", mo_domain, ["id"], limit=5000)
        mo_ids = [mo["id"] for mo in mos]
        
        if not mo_ids:
            return []
            
        # Fetch raw material moves for these MOs
        move_domain = [
            ("raw_material_production_id", "in", mo_ids),
            ("state", "not in", ["done", "cancel"])
        ]
        moves = self.odoo.search_read_records(
            "stock.move", move_domain, ["product_id", "product_uom_qty", "product_qty"], limit=10000
        )
        
        # Aggregate required quantities
        required_qty = defaultdict(float)
        for move in moves:
            pid = move.get("product_id")
            if pid:
                p_name = pid[1] if isinstance(pid, list) else str(pid)
                p_id = pid[0] if isinstance(pid, list) else pid
                # Usually product_uom_qty is the demanded qty
                qty = float(move.get("product_uom_qty") or move.get("product_qty") or 0.0)
                required_qty[(p_id, p_name)] += qty
                
        if not required_qty:
            return []
            
        # Check available stock for these products
        product_ids = [k[0] for k in required_qty.keys()]
        stock_domain = [
            ("location_id.usage", "=", "internal"),
            ("product_id", "in", product_ids)
        ]
        quants = self.odoo.search_read_records("stock.quant", stock_domain, ["product_id", "quantity"], limit=10000)
        
        available_qty = defaultdict(float)
        for q in quants:
            pid = q.get("product_id")
            if pid:
                p_id = pid[0] if isinstance(pid, list) else pid
                available_qty[p_id] += float(q.get("quantity") or 0.0)
                
        # Calculate shortage
        shortages = []
        for (p_id, p_name), req in required_qty.items():
            avail = available_qty.get(p_id, 0.0)
            shortage = req - avail
            if shortage > 0:
                shortages.append({
                    "product_id": p_id,
                    "product_name": p_name,
                    "required_qty": round(req, 2),
                    "available_qty": round(avail, 2),
                    "shortage_qty": round(shortage, 2)
                })
                
        shortages.sort(key=lambda x: x["shortage_qty"], reverse=True)
        return shortages

    def get_ready_to_ship_orders(self) -> list[dict[str, Any]]:
        """
        Analyzes pending sales orders and checks if they can be 100% fulfilled by current stock.
        """
        # 1. Fetch Sales Lines that are not fully delivered
        sol_domain = [("state", "=", "sale")]
        sols = self.odoo.search_read_records(
            "sale.order.line", sol_domain, 
            ["order_id", "product_id", "product_uom_qty", "qty_delivered", "order_partner_id"], 
            limit=10000
        )
        
        # 2. Group required quantities by Order
        orders_req = defaultdict(dict) # order_id -> {product_id: pending_qty}
        order_meta = {} # order_id -> {"name": order_name, "customer": customer_name}
        
        all_product_ids = set()
        for line in sols:
            oid = line.get("order_id")
            pid = line.get("product_id")
            if not oid or not pid:
                continue
                
            o_id = oid[0] if isinstance(oid, list) else oid
            o_name = oid[1] if isinstance(oid, list) else str(oid)
            
            p_id = pid[0] if isinstance(pid, list) else pid
            
            partner = line.get("order_partner_id")
            c_name = partner[1] if isinstance(partner, list) else "Unknown"
            
            order_meta[o_id] = {"order_name": o_name, "customer_name": c_name}
            
            ordered = float(line.get("product_uom_qty") or 0.0)
            delivered = float(line.get("qty_delivered") or 0.0)
            pending = ordered - delivered
            
            if pending > 0:
                orders_req[o_id][p_id] = orders_req[o_id].get(p_id, 0.0) + pending
                all_product_ids.add(p_id)
                
        if not orders_req:
            return []
            
        # 3. Get available stock
        stock_domain = [
            ("location_id.usage", "=", "internal"),
            ("product_id", "in", list(all_product_ids))
        ]
        quants = self.odoo.search_read_records("stock.quant", stock_domain, ["product_id", "quantity"], limit=10000)
        
        available_qty = defaultdict(float)
        for q in quants:
            pid = q.get("product_id")
            if pid:
                p_id = pid[0] if isinstance(pid, list) else pid
                available_qty[p_id] += float(q.get("quantity") or 0.0)
                
        # 4. Check which orders are fully ready
        ready_orders = []
        for o_id, reqs in orders_req.items():
            is_ready = True
            missing_items = []
            
            for p_id, req_qty in reqs.items():
                if available_qty.get(p_id, 0.0) < req_qty:
                    is_ready = False
                    missing_items.append({"product_id": p_id, "missing_qty": req_qty - available_qty.get(p_id, 0.0)})
                    
            if is_ready:
                ready_orders.append({
                    "order_id": o_id,
                    "order_name": order_meta[o_id]["order_name"],
                    "customer_name": order_meta[o_id]["customer_name"],
                    "items_count": len(reqs),
                    "total_units": sum(reqs.values())
                })
                
                # Deduct from available stock so we don't double count for other orders
                for p_id, req_qty in reqs.items():
                    available_qty[p_id] -= req_qty
                    
        return ready_orders

    def analyze_workcenter_bottlenecks(self) -> list[dict[str, Any]]:
        """
        Analyzes active Workorders to find which Workcenters have the largest backlog.
        """
        wip_records = self.odoo.search_read_records(
            "mrp.workorder",
            domain=[("state", "not in", ["done", "cancel"])],
            fields=["workcenter_id", "qty_production"],
            limit=10000
        )
        
        # Manual grouping
        wip_by_wc_dict = defaultdict(float)
        wc_meta = {}
        for rec in wip_records:
            wc = rec.get("workcenter_id")
            if wc:
                wc_id = wc[0] if isinstance(wc, list) else wc
                wc_name = wc[1] if isinstance(wc, list) else str(wc)
                wc_meta[wc_id] = wc_name
                qty = rec.get("qty_production") or 0.0
                wip_by_wc_dict[wc_id] += qty

        wip_by_wc = []
        for wc_id, qty in wip_by_wc_dict.items():
            wip_by_wc.append({
                "workcenter_id": [wc_id, wc_meta[wc_id]],
                "qty_production": qty
            })
        
        bottlenecks = []
        for wc in wip_by_wc:
            wc_info = wc.get("workcenter_id")
            if wc_info:
                wc_name = wc_info[1] if isinstance(wc_info, list) else str(wc_info)
                qty = wc.get("qty_production", 0.0)
                bottlenecks.append({
                    "workcenter": wc_name,
                    "backlog_qty": round(qty, 2)
                })
                
        bottlenecks.sort(key=lambda x: x["backlog_qty"], reverse=True)
        return bottlenecks

    def get_quality_metrics(self) -> dict[str, Any]:
        """
        Aggregates recent Quality Alerts and Checks.
        """
        # Quality Alerts by Product
        alert_records = self.odoo.search_read_records(
            "quality.alert",
            domain=[],
            fields=["product_id"],
            limit=10000
        )
        
        alert_dict = defaultdict(int)
        alert_meta = {}
        for rec in alert_records:
            pid = rec.get("product_id")
            if pid:
                p_id = pid[0] if isinstance(pid, list) else pid
                p_name = pid[1] if isinstance(pid, list) else str(pid)
                alert_meta[p_id] = p_name
                alert_dict[p_id] += 1
                
        alerts = [{"product_id": [pid, alert_meta[pid]], "id_count": count} for pid, count in alert_dict.items()]
        
        # Quality Checks by State
        check_records = self.odoo.search_read_records(
            "quality.check",
            domain=[],
            fields=["quality_state"],
            limit=10000
        )
        
        check_dict = defaultdict(int)
        for rec in check_records:
            state = rec.get("quality_state")
            if state:
                check_dict[state] += 1
                
        checks = [{"quality_state": state, "id_count": count} for state, count in check_dict.items()]
        
        alerts_formatted = []
        for a in alerts:
            pid = a.get("product_id")
            if pid:
                p_name = pid[1] if isinstance(pid, list) else str(pid)
                alerts_formatted.append({
                    "product": p_name,
                    "alert_count": a.get("id_count", 0)
                })
                
        alerts_formatted.sort(key=lambda x: x["alert_count"], reverse=True)
        
        checks_formatted = []
        for c in checks:
            state = c.get("quality_state")
            if state:
                checks_formatted.append({
                    "state": state,
                    "count": c.get("id_count", 0)
                })
                
        return {
            "top_products_with_alerts": alerts_formatted[:10],
            "quality_checks_summary": checks_formatted
        }
