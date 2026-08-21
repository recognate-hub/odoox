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
@validate_write_input(ScheduleMeetingInput)
def schedule_meeting(
    name: str, start: str, stop: str, partner_ids: list[int], notes: str = ""
) -> dict[str, Any]:
    """
    Schedule a meeting in Odoo's calendar and log raw notes.

    Args:
        name (str): The title of the meeting.
        start (str): The start time in ISO format (e.g., '2026-08-01 10:00:00').
        stop (str): The stop time in ISO format.
        partner_ids (List[int]): A list of Odoo partner IDs to invite.
        notes (str): Optional meeting notes or agenda.

    Returns:
        Dict[str, Any]: Status and the new meeting_id.
    """
    logger.info("MCP Tool Called: schedule_meeting", name=name)
    _, crm_service = server._get_tenant_service()
    result = crm_service.create_meeting(name, start, stop, partner_ids, notes)
    return result


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


@mcp.tool()
@secure_tool()
@validate_write_input(UpdateMeetingInput)
def update_meeting(meeting_id: int, data: dict[str, Any]) -> dict[str, Any]:
    """
    Update an existing calendar event.

    Use this to reschedule, rename, or change the location of a meeting.

    Args:
        meeting_id (int): The ID of the calendar event to update.
        data (Dict): Fields to update (e.g., {"name": "...", "start": "...", "location": "..."}).

    Returns:
        Dict: Status of the update operation.
    """
    with _span("mcp.update_meeting"):
        logger.info("MCP Tool Called: update_meeting", meeting_id=meeting_id)
        odoo_repo, _ = server._get_tenant_service()
        from services.calendar import CalendarService

        service = CalendarService(odoo_repo)
        return service.update_meeting(meeting_id, data)


@mcp.tool()
@secure_tool()
@validate_write_input(DeleteMeetingInput)
def delete_meeting(meeting_id: int) -> dict[str, Any]:
    """
    Delete/cancel a calendar event.

    Args:
        meeting_id (int): The ID of the calendar event to remove.

    Returns:
        Dict: Status of the delete operation.
    """
    with _span("mcp.delete_meeting"):
        logger.info("MCP Tool Called: delete_meeting", meeting_id=meeting_id)
        odoo_repo, _ = server._get_tenant_service()
        from services.calendar import CalendarService

        service = CalendarService(odoo_repo)
        return service.delete_meeting(meeting_id)
