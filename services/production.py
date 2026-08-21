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

    def get_manufacturing_orders(self, limit: int = 20) -> list[dict[str, Any]]:
        return self.odoo.get_manufacturing_orders(limit)

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

    def get_workcenters(self, limit: int = 50) -> list[dict[str, Any]]:
        return self.odoo.get_workcenters(limit)

    def get_routings(self, limit: int = 50) -> list[dict[str, Any]]:
        return self.odoo.get_routings(limit)

    def get_bom_hierarchy(
        self, bom_id: int | None = None, limit: int = 200
    ) -> list[dict[str, Any]]:
        return self.odoo.get_bom_lines(bom_id, limit)

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
        return {
            "status": "success",
            "message": "Component shortage analysis requires complex stock/bom cross-referencing which is best handled via MPS forecast or custom Odoo views.",
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
