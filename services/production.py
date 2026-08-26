from typing import Any

from core.logger import get_logger
from repositories.odoo import OdooRepository

logger = get_logger(__name__)


class ProductionService:
    def __init__(self, odoo_repo: OdooRepository):
        self.odoo = odoo_repo

    def create_manufacturing_order(
        self, product_id: int, product_qty: float
    ) -> dict[str, Any]:
        mo_id = self.odoo.create_manufacturing_order(product_id, product_qty)
        return {"status": "success", "manufacturing_order_id": mo_id}

    def get_manufacturing_orders(self, limit: int = 20, offset: int = 0, date_from: str | None = None, date_to: str | None = None, product_name_query: str | None = None) -> list[dict[str, Any]]:
        return self.odoo.get_manufacturing_orders(limit, offset, date_from, date_to, product_name_query)

    def update_manufacturing_order(
        self, mo_id: int, data: dict[str, Any]
    ) -> dict[str, Any]:
        success = self.odoo.update_manufacturing_order(mo_id, data)
        return (
            {"status": "success"}
            if success
            else {"status": "error", "message": "Update failed"}
        )

    def confirm_manufacturing_order(self, mo_id: int) -> dict[str, Any]:
        self.odoo.confirm_manufacturing_order(mo_id)
        return {
            "status": "success",
            "message": f"Manufacturing order {mo_id} confirmed.",
        }

    def get_bill_of_materials(
        self, product_id: int | None = None, limit: int = 50
    ) -> list[dict[str, Any]]:
        return self.odoo.get_bill_of_materials(product_id, limit)

    def get_work_orders(
        self, mo_id: int | None = None, limit: int = 50
    ) -> list[dict[str, Any]]:
        return self.odoo.get_work_orders(mo_id, limit)

    def get_wip_stock_by_stage(self, product_id: int) -> list[dict[str, Any]]:
        return self.odoo.get_wip_stock_by_stage(product_id)

    def get_workcenters(self, limit: int = 50) -> list[dict[str, Any]]:
        return self.odoo.get_workcenters(limit)

    def get_routings(self, limit: int = 50) -> list[dict[str, Any]]:
        return self.odoo.get_routings(limit)

    def get_bom_hierarchy(
        self, bom_id: int | None = None, limit: int = 200
    ) -> list[dict[str, Any]]:
        bom_lines = self.odoo.get_bom_lines(bom_id, limit)
        if not bom_lines:
            return []

        # Extract product IDs
        product_ids = []
        for line in bom_lines:
            pid = line.get("product_id")
            if pid:
                p_id = pid[0] if isinstance(pid, list) else pid
                product_ids.append(p_id)

        if not product_ids:
            return bom_lines

        # Fetch cost and exact names in bulk
        products = self.odoo.search_read_records(
            "product.product",
            domain=[("id", "in", product_ids)],
            fields=["name", "standard_price", "default_code"],
            limit=len(product_ids),
        )

        # Build mapping
        prod_map = {
            p["id"]: {
                "name": p.get("name", ""),
                "cost": p.get("standard_price", 0.0),
                "code": p.get("default_code", ""),
            }
            for p in products
        }

        # Enrich the response
        for line in bom_lines:
            pid = line.get("product_id")
            if pid:
                p_id = pid[0] if isinstance(pid, list) else pid
                prod_info = prod_map.get(p_id, {})

                # Expand product_id to include full details instead of just [id, name]
                line["product_name"] = prod_info.get("name", "")
                line["product_code"] = prod_info.get("code", "")

                qty = float(line.get("product_qty", 0.0))
                unit_cost = float(prod_info.get("cost", 0.0))

                line["unit_cost"] = round(unit_cost, 2)
                line["total_cost"] = round(qty * unit_cost, 2)

        return bom_lines

    def create_eco(
        self, product_tmpl_id: int, type_id: int, name: str
    ) -> dict[str, Any]:
        eco_id = self.odoo.create_eco(product_tmpl_id, type_id, name)
        return {"status": "success", "eco_id": eco_id}

    def get_equipment_oee(
        self, workcenter_id: int | None = None, limit: int = 100
    ) -> list[dict[str, Any]]:
        return self.odoo.get_equipment_oee(workcenter_id, limit)

    def reschedule_work_order(
        self, workorder_id: int, date_start: str, date_finished: str
    ) -> dict[str, Any]:
        success = self.odoo.update_record(
            "mrp.workorder",
            workorder_id,
            {"date_start": date_start, "date_finished": date_finished},
        )
        return (
            {"status": "success"}
            if success
            else {"status": "error", "message": "Failed to reschedule"}
        )

    def analyze_component_shortages(self) -> dict[str, Any]:
        """
        Cross-reference active MO raw material requirements against live stock to detect shortages.
        """
        raw_materials = self.odoo.get_mo_raw_materials(limit=1000)
        product_ids = {m["product_id"][0] for m in raw_materials if m.get("product_id")}
        
        if not product_ids:
            return {"status": "success", "message": "No active raw material demands found."}
            
        # Fetch current stock for required products
        stock_data = self.odoo.search_read_records(
            "product.product",
            domain=[("id", "in", list(product_ids))],
            fields=["qty_available", "virtual_available", "name", "default_code"],
            limit=len(product_ids)
        )
        
        stock_map = {p["id"]: p for p in stock_data}
        shortages = []
        
        # We'll group demand by product to see overall shortages
        demand_map = {}
        for move in raw_materials:
            pid = move.get("product_id")
            if not pid:
                continue
            p_id, p_name = pid[0], pid[1]
            qty_required = move.get("product_uom_qty", 0.0)
            qty_reserved = move.get("quantity", 0.0) # Using 'quantity' field from stock.move in Odoo 17+
            
            if p_id not in demand_map:
                demand_map[p_id] = {"name": p_name, "total_required": 0.0, "total_reserved": 0.0, "affected_mos": set()}
                
            demand_map[p_id]["total_required"] += qty_required
            demand_map[p_id]["total_reserved"] += qty_reserved
            mo = move.get("raw_material_production_id")
            if mo:
                demand_map[p_id]["affected_mos"].add(mo[1])
                
        for p_id, demand in demand_map.items():
            stock = stock_map.get(p_id, {})
            qty_available = stock.get("qty_available", 0.0)
            virtual_available = stock.get("virtual_available", 0.0)
            
            # If total required is greater than what is physically available or virtually forecasted
            if demand["total_required"] > qty_available or virtual_available < 0:
                shortages.append({
                    "product_id": p_id,
                    "product_name": demand["name"],
                    "required_quantity": demand["total_required"],
                    "available_quantity": qty_available,
                    "forecasted_quantity": virtual_available,
                    "shortage_amount": demand["total_required"] - qty_available,
                    "affected_manufacturing_orders": list(demand["affected_mos"])
                })
                
        shortages.sort(key=lambda x: x["shortage_amount"], reverse=True)
        return {
            "status": "success",
            "total_products_checked": len(product_ids),
            "shortage_count": len(shortages),
            "shortages": shortages
        }

    from core.cache import cache_response
    
    @cache_response(ttl_seconds=300)
    def analyze_oee_losses(self, limit: int = 500) -> dict[str, Any]:
        """
        Aggregate equipment downtime by loss reasons to identify top efficiency sinks.
        """
        logs = self.odoo.search_read_records(
            "mrp.workcenter.productivity",
            domain=[],
            fields=["workcenter_id", "loss_id", "duration"],
            limit=limit
        )
        
        losses = {}
        total_downtime = 0.0
        
        for log in logs:
            loss = log.get("loss_id")
            if not loss:
                continue
                
            loss_name = loss[1]
            duration = log.get("duration", 0.0)
            
            if loss_name not in losses:
                losses[loss_name] = 0.0
                
            losses[loss_name] += duration
            total_downtime += duration
            
        sorted_losses = [{"loss_reason": k, "duration_minutes": round(v, 2), "percentage_of_downtime": round((v / total_downtime * 100) if total_downtime else 0, 2)} for k, v in losses.items()]
        sorted_losses.sort(key=lambda x: x["duration_minutes"], reverse=True)
        
        from services.visualization import generate_pareto_chart
        chart_b64 = generate_pareto_chart(sorted_losses, title="OEE Losses Pareto Chart")
        
        return {
            "status": "success",
            "total_downtime_minutes": round(total_downtime, 2),
            "pareto_analysis": sorted_losses,
            "pareto_chart_base64": chart_b64
        }

    def predict_production_delays(self) -> dict[str, Any]:
        """
        Compare actual WIP duration vs expected duration to flag delayed work orders.
        """
        wos = self.odoo.get_active_work_orders_duration(limit=300)
        
        high_risk = []
        for wo in wos:
            duration = wo.get("duration", 0.0)
            expected = wo.get("duration_expected", 0.0)
            
            # If actual duration exceeds expected by more than 20%, it's a delay risk
            if expected > 0 and duration > (expected * 1.2):
                variance = duration - expected
                variance_pct = (variance / expected) * 100
                mo_data = wo.get("production_id")
                mo_name = mo_data[1] if mo_data else "Unknown MO"
                wc_data = wo.get("workcenter_id")
                wc_name = wc_data[1] if wc_data else "Unknown Workcenter"
                
                high_risk.append({
                    "workorder_id": wo.get("id"),
                    "workorder_name": wo.get("name"),
                    "manufacturing_order": mo_name,
                    "workcenter": wc_name,
                    "expected_duration_minutes": expected,
                    "actual_duration_minutes": round(duration, 2),
                    "delay_minutes": round(variance, 2),
                    "delay_percentage": round(variance_pct, 1)
                })
                
        high_risk.sort(key=lambda x: x["delay_minutes"], reverse=True)
        
        return {
            "status": "success",
            "active_orders_analyzed": len(wos),
            "delayed_operations_count": len(high_risk),
            "high_risk_bottlenecks": high_risk
        }

    def get_mps_forecast(self, limit: int = 50) -> list[dict[str, Any]]:
        return self.odoo.get_mps_forecast(limit)

    def run_mrp_scheduler(self) -> dict[str, Any]:
        self.odoo.run_mrp_scheduler()
        return {"status": "success", "message": "MRP scheduler executed successfully."}

    def trace_lot_number(
        self, lot_id: int | None = None, limit: int = 100
    ) -> list[dict[str, Any]]:
        return self.odoo.trace_lot_number(lot_id, limit)

    def log_work_order_time(
        self, workorder_id: int, duration_minutes: float, loss_id: int | None = None
    ) -> dict[str, Any]:
        rec_id = self.odoo.log_work_order_time(workorder_id, duration_minutes, loss_id)
        return {"status": "success", "productivity_record_id": rec_id}

