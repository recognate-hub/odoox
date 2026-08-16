from typing import Any

from core.logger import get_logger
from repositories.odoo import OdooRepository

logger = get_logger(__name__)

class CalendarService:
    def __init__(self, odoo_repo: OdooRepository):
        self.odoo = odoo_repo

    def schedule_meeting(self, name: str, start: str, stop: str, partner_ids: list[int], notes: str) -> dict[str, Any]:
        meeting_id = self.odoo.schedule_meeting(name, start, stop, partner_ids)
        if notes:
            self.odoo.log_activity("calendar.event", meeting_id, f"Meeting Notes: {notes}")
        return {"status": "success", "meeting_id": meeting_id}

    def get_meetings(self, partner_id: int | None = None, start_date: str | None = None, limit: int = 50) -> list[dict[str, Any]]:
        return self.odoo.get_meetings(partner_id, start_date, limit)

    def update_meeting(self, meeting_id: int, data: dict[str, Any]) -> dict[str, Any]:
        success = self.odoo.update_meeting(meeting_id, data)
        return {"status": "success"} if success else {"status": "error", "message": "Update failed"}

    def delete_meeting(self, meeting_id: int) -> dict[str, Any]:
        result = self.odoo.delete_meeting(meeting_id)
        return {"status": "success"} if result else {"status": "error", "message": "Delete failed"}
