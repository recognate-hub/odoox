from typing import Any

from core.logger import get_logger
from repositories.odoo import OdooRepository

logger = get_logger(__name__)

class MaintenanceService:
    def __init__(self, odoo_repo: OdooRepository):
        self.odoo = odoo_repo

    def create_maintenance_request(self, name: str, equipment_id: int, description: str | None = None, priority: str = "0") -> dict[str, Any]:
        req_id = self.odoo.create_maintenance_request(name, equipment_id, description, priority)
        return {"status": "success", "maintenance_request_id": req_id}

    def get_equipment_status(self, equipment_id: int | None = None, limit: int = 50) -> list[dict[str, Any]]:
        return self.odoo.get_equipment_status(equipment_id, limit)

    def schedule_preventative_maintenance(self, equipment_id: int, next_action_date: str) -> dict[str, Any]:
        success = self.odoo.update_record("maintenance.equipment", equipment_id, {
            "next_action_date": next_action_date
        })
        return {"status": "success"} if success else {"status": "error", "message": "Failed to schedule"}
