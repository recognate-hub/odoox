from typing import Any
from core.logger import get_logger
from mcp_app import server
from mcp_app.schemas import *
from mcp_app.security import secure_tool
from mcp_app.server import _span, mcp
from mcp_app.validation import validate_write_input

logger = get_logger(__name__)


@mcp.tool()
@secure_tool()
def get_meetings(
    partner_id: int | None = None, start_date: str | None = None, limit: int = 50
) -> list[dict[str, Any]]:
    """
    List calendar events/meetings from Odoo.

    Use this to check upcoming meetings, filter by attendee, or review schedule from a given date.

    Args:
        partner_id (int, optional): Filter meetings by a specific attendee's partner ID.
        start_date (str, optional): Only show meetings starting on or after this date (ISO format).
        limit (int): Maximum number of meetings to return.

    Returns:
        List[Dict]: Meetings with name, start, stop, attendees, location, and description.
    """
    with _span("mcp.get_meetings"):
        logger.info(
            "MCP Tool Called: get_meetings",
            partner_id=partner_id,
            start_date=start_date,
        )
        odoo_repo, _ = server._get_tenant_service()
        from services.calendar import CalendarService

        service = CalendarService(odoo_repo)
        return service.get_meetings(partner_id, start_date, limit)
