from typing import Any

from core.logger import get_logger
from repositories.odoo import OdooRepository

logger = get_logger(__name__)


class ReportsService:
    def __init__(self, odoo_repo: OdooRepository):
        self.odoo = odoo_repo

    def generate_report(
        self, model: str, domain: list[Any], fields: list[str], groupby: list[str]
    ) -> list[dict[str, Any]]:
        return self.odoo.read_group(model, domain, fields, groupby)
