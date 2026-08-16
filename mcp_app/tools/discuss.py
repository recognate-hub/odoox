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
@validate_write_input(SendEmailInput)
def send_email(email_to: str, subject: str, body: str) -> dict[str, Any]:
    """
    Send an email via Odoo's mail system.
    
    Use this tool to send outbound communications to leads or customers.
    
    Args:
        email_to (str): The recipient's email address.
        subject (str): The subject line.
        body (str): The email body (HTML or plain text).
        
    Returns:
        Dict[str, Any]: The status of the operation and mail ID.
    """
    logger.info("MCP Tool Called: send_email", email_to=email_to, subject=subject)
    odoo_repo, _ = server._get_tenant_service()
    mail_id = odoo_repo.send_email(email_to, subject, body)
    return {"status": "success", "mail_id": mail_id}


@mcp.tool()
@secure_tool()
@validate_write_input(PostMessageInput)
def post_message(res_model: str, res_id: int, body: str, message_type: str = "comment") -> dict[str, Any]:
    """
    Post a message or internal note on any Odoo record (chatter).
    
    Args:
        res_model (str): The Odoo model (e.g., 'crm.lead', 'sale.order').
        res_id (int): The ID of the record.
        body (str): The message body (HTML or plain text).
        message_type (str): 'comment' for public note, 'notification' for system note.
    """
    with _span("mcp.post_message"):
        odoo_repo, _ = server._get_tenant_service()
        from services.discuss import DiscussService
        service = DiscussService(odoo_repo)
        return service.post_message(res_model, res_id, body, message_type)

@mcp.tool()
@secure_tool()
@validate_write_input(CreateChannelInput)
def create_channel(name: str, channel_type: str = "channel") -> dict[str, Any]:
    """
    Create a new Discuss channel for team communication.
    
    Args:
        name (str): The name of the channel.
        channel_type (str): 'channel' for public, 'chat' for DM, 'group' for private group.
    """
    with _span("mcp.create_channel"):
        odoo_repo, _ = server._get_tenant_service()
        from services.discuss import DiscussService
        service = DiscussService(odoo_repo)
        return service.create_channel(name, channel_type)


@mcp.tool()
@secure_tool()
def get_messages(res_model: str | None = None, res_id: int | None = None, limit: int = 50) -> list[dict[str, Any]]:
    """
    Retrieve messages from Odoo's chatter/mail system.
    
    Use this to read conversation history on any record, or browse all recent messages.
    
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
