from typing import Any

from core.logger import get_logger
from repositories.odoo import OdooRepository

logger = get_logger(__name__)


class DashboardsService:
    def __init__(self, odoo_repo: OdooRepository):
        self.odoo = odoo_repo

    def get_sales_dashboard(self) -> dict[str, Any]:
        dashboard = self.odoo.get_dashboard()
        return dashboard.model_dump()
