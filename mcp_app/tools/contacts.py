from typing import Any
from core.logger import get_logger
from mcp_app import server
from mcp_app.schemas import *
from mcp_app.security import secure_tool
from mcp_app.server import mcp
from mcp_app.validation import validate_write_input

logger = get_logger(__name__)


@mcp.tool()
@secure_tool()
def search_customer(name: str, limit: int = 20) -> list[dict[str, Any]]:
    """
    Search for contacts/customers in Odoo by name.

    Use this tool when:
    - The user asks to find a customer, vendor, or contact by name.
    - You need to find a partner_id to use in another tool (like creating an invoice or quote).

    Args:
        name (str): The name query to search for (case-insensitive partial match).
        limit (int): The maximum number of records to return.

    Returns:
        List[Dict[str, Any]]: A list of contacts with fields like id, name, email, phone, is_company, and company_id.
    """
    logger.info("MCP Tool Called: search_customer", query=name)
    odoo_repo, _ = server._get_tenant_service()
    contacts = odoo_repo.search_contacts_by_name(name, limit=limit)
    return [contact.model_dump() for contact in contacts]


@mcp.tool()
@secure_tool()
def get_customer_details(partner_id: int) -> dict[str, Any]:
    """
    Fetch comprehensive customer details and recent quotes.

    Use this tool when:
    - The user asks for a 360-degree view of a specific customer.
    - The user asks for recent quotes or orders for a specific customer.
    
    Do NOT use this tool when:
    - You are searching by name (use search_customer first to get the partner_id).

    Args:
        partner_id (int): The exact Odoo ID of the partner/customer.

    Returns:
        Dict[str, Any]: A dictionary containing the 'contact' dictionary and a 'recent_quotes' list.
    """
    logger.info("MCP Tool Called: get_customer_details", partner_id=partner_id)
    _, crm_service = server._get_tenant_service()
    return crm_service.get_customer_summary_data(partner_id)
