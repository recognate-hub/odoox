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
def get_messages(
    res_model: str | None = None, res_id: int | None = None, limit: int = 50
) -> list[dict[str, Any]]:
    """
    Retrieve messages from Odoo's chatter/mail system.

    Use this tool when:
    - The user wants to read conversation history or chatter on any record.
    - The user wants to browse all recent messages across the system.

    Args:
        res_model (str, optional): Filter by Odoo model (e.g., 'crm.lead'). Leave empty for all.
        res_id (int, optional): Filter by specific record ID. Requires res_model.
        limit (int): Maximum number of messages to return.

    Returns:
        List[Dict]: Messages with body, author, date, subject, and linked record info.
    """
    with _span("mcp.get_messages"):
        odoo_repo, _ = server._get_tenant_service()
        from services.discuss import DiscussService

        service = DiscussService(odoo_repo)
        return service.get_messages(res_model, res_id, limit)


@mcp.tool()
@secure_tool()
def get_channels(limit: int = 50) -> list[dict[str, Any]]:
    """
    List all Discuss channels available in the Odoo instance.
    
    Use this tool when:
    - The user wants to see what discussion channels exist.
    - You need to find a channel_id to use in other discuss tools.

    Args:
        limit (int): Maximum number of channels to return.

    Returns:
        List[Dict]: Channels with name, type, members, and description.
    """
    with _span("mcp.get_channels"):
        odoo_repo, _ = server._get_tenant_service()
        from services.discuss import DiscussService

        service = DiscussService(odoo_repo)
        return service.get_channels(limit)


@mcp.tool()
@secure_tool()
def get_channel_messages(channel_id: int, limit: int = 50) -> list[dict[str, Any]]:
    """
    Read messages from a specific Discuss channel.
    
    Use this tool when:
    - The user asks to read messages from a specific chat or channel.

    Args:
        channel_id (int): The ID of the Discuss channel.
        limit (int): Maximum number of messages to return.

    Returns:
        List[Dict]: Messages in the channel with body, author, and date.
    """
    with _span("mcp.get_channel_messages"):
        odoo_repo, _ = server._get_tenant_service()
        from services.discuss import DiscussService

        service = DiscussService(odoo_repo)
        return service.get_channel_messages(channel_id, limit)
