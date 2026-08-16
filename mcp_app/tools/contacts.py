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
    
    Use this tool to find a partner's ID or basic contact info.
    
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
@validate_write_input(CreateContactInput)
def create_contact(name: str, email: str | None = None, phone: str | None = None, is_company: bool = False) -> dict[str, Any]:
    """
    Create a new CRM contact or customer in Odoo.
    
    Use this tool to add new people or companies to the system.
    
    Args:
        name (str): The full name of the contact or company.
        email (Optional[str]): The email address.
        phone (Optional[str]): The phone number.
        is_company (bool): True if the contact represents a company.
        
    Returns:
        Dict[str, Any]: The status of the operation and new partner ID.
    """
    logger.info("MCP Tool Called: create_contact", name=name)
    odoo_repo, _ = server._get_tenant_service()
    partner_id = odoo_repo.create_contact(name, email, phone, is_company)
    return {"status": "success", "partner_id": partner_id}



@mcp.tool()
@secure_tool()
def get_customer_details(partner_id: int) -> dict[str, Any]:
    """
    Fetch comprehensive customer details and recent quotes.
    
    Use this tool to generate a 360-degree view of a customer.
    
    Args:
        partner_id (int): The exact Odoo ID of the partner/customer.
        
    Returns:
        Dict[str, Any]: A dictionary containing the 'contact' dictionary and a 'recent_quotes' list.
    """
    logger.info("MCP Tool Called: get_customer_details", partner_id=partner_id)
    _, crm_service = server._get_tenant_service()
    return crm_service.get_customer_summary_data(partner_id)


# --- Sales & Inventory Tools ---


