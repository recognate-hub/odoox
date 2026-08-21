from typing import Any

from core.logger import get_logger
from repositories.odoo import OdooRepository

logger = get_logger(__name__)


class DiscussService:
    def __init__(self, odoo_repo: OdooRepository):
        self.odoo = odoo_repo

    def post_message(
        self, res_model: str, res_id: int, body: str, message_type: str = "comment"
    ) -> dict[str, Any]:
        msg_id = self.odoo.post_message(res_model, res_id, body, message_type)
        return {"status": "success", "message_id": msg_id}

    def create_channel(
        self, name: str, channel_type: str = "channel"
    ) -> dict[str, Any]:
        channel_id = self.odoo.create_channel(name, channel_type)
        return {"status": "success", "channel_id": channel_id}

    def get_messages(
        self, res_model: str | None = None, res_id: int | None = None, limit: int = 50
    ) -> list[dict[str, Any]]:
        return self.odoo.get_messages(res_model, res_id, limit)

    def get_channels(self, limit: int = 50) -> list[dict[str, Any]]:
        return self.odoo.get_channels(limit)

    def get_channel_messages(
        self, channel_id: int, limit: int = 50
    ) -> list[dict[str, Any]]:
        return self.odoo.get_channel_messages(channel_id, limit)
