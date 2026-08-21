from typing import Any

from core.logger import get_logger
from repositories.odoo import OdooRepository

logger = get_logger(__name__)


class SalesService:
    def __init__(self, odoo_repo: OdooRepository):
        self.odoo = odoo_repo

    def create_quote(self, partner_id: int, order_lines: list[dict]) -> dict[str, Any]:
        quote_id = self.odoo.create_quote(partner_id, order_lines)
        return {"status": "success", "quote_id": quote_id}

    def get_recent_quotes(
        self, partner_id: int | None = None, limit: int = 10
    ) -> list[dict[str, Any]]:
        quotes = self.odoo.get_recent_quotes(partner_id, limit)
        return [q.model_dump() for q in quotes]
