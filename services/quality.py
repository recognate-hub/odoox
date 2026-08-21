from typing import Any

from core.logger import get_logger
from repositories.odoo import OdooRepository

logger = get_logger(__name__)


class QualityService:
    def __init__(self, odoo_repo: OdooRepository):
        self.odoo = odoo_repo

    def create_quality_alert(
        self,
        name: str,
        product_id: int,
        team_id: int | None = None,
        priority: str = "0",
    ) -> dict[str, Any]:
        alert_id = self.odoo.create_quality_alert(name, product_id, team_id, priority)
        return {"status": "success", "quality_alert_id": alert_id}

    def get_quality_checks(
        self, product_id: int | None = None, limit: int = 20
    ) -> list[dict[str, Any]]:
        return self.odoo.get_quality_checks(product_id, limit)

    def get_quality_alerts(
        self, product_id: int | None = None, limit: int = 50
    ) -> list[dict[str, Any]]:
        return self.odoo.get_quality_alerts(product_id, limit)

    def update_quality_alert(
        self, alert_id: int, data: dict[str, Any]
    ) -> dict[str, Any]:
        success = self.odoo.update_quality_alert(alert_id, data)
        return (
            {"status": "success"}
            if success
            else {"status": "error", "message": "Update failed"}
        )

    def get_quality_points(self, limit: int = 50) -> list[dict[str, Any]]:
        return self.odoo.get_quality_points(limit)
