from fastmcp import FastMCP
from typing import List, Optional, Dict, Any

from config.settings import get_settings
from core.logger import get_logger
from odoo.xmlrpc import XmlRpcOdooConnector
from repositories.odoo import OdooRepository
from services.crm import CRMService
from mcp_app.security import secure_tool
from mcp_app.validation import validate_write_input
from mcp_app.schemas import CreateLeadInput, UpdateLeadInput, ScheduleMeetingInput

logger = get_logger(__name__)

# Initialize dependencies (in a real app, use a DI container)
settings = get_settings()
odoo_connector = XmlRpcOdooConnector(settings)
odoo_repo = OdooRepository(odoo_connector)
crm_service = CRMService(odoo_repo)

# Initialize FastMCP Server
mcp = FastMCP("ODOOX")

# --- CRM Tools ---

@mcp.tool()
@secure_tool()
def get_leads(limit: int = 100) -> List[Dict[str, Any]]:
    """
    Retrieve active CRM leads (opportunities) from Odoo.
    
    Use this tool to fetch a list of current active sales leads.
    
    Args:
        limit (int): The maximum number of leads to return. Default is 100.
        
    Returns:
        List[Dict[str, Any]]: A list of dictionaries representing leads with fields like name, email_from, phone, partner_id, stage_id, expected_revenue, and description.
    """
    logger.info("MCP Tool Called: get_leads", limit=limit)
    leads = odoo_repo.get_active_leads(limit=limit)
    return [lead.model_dump() for lead in leads]


@mcp.tool()
@secure_tool()
@validate_write_input(CreateLeadInput)
def create_lead(name: str, email: Optional[str] = None, phone: Optional[str] = None, description: Optional[str] = None) -> Dict[str, Any]:
    """
    Create a new CRM lead (opportunity) in Odoo.
    
    Use this tool when you need to record a new prospect or sales opportunity.
    
    Args:
        name (str): The required name/title of the lead or opportunity.
        email (Optional[str]): The email address of the contact.
        phone (Optional[str]): The phone number of the contact.
        description (Optional[str]): Additional notes or context about the lead.
        
    Returns:
        Dict[str, Any]: A dictionary containing a 'status' string and the new 'lead_id' integer.
    """
    logger.info("MCP Tool Called: create_lead", name=name)
    lead_id = odoo_repo.create_lead(name, email, phone, description)
    return {"status": "success", "lead_id": lead_id}


@mcp.tool()
@secure_tool()
@validate_write_input(UpdateLeadInput)
def update_lead(lead_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Update an existing CRM lead in Odoo.
    
    Use this tool to modify fields on an existing lead.
    
    Args:
        lead_id (int): The integer ID of the lead to update.
        data (Dict[str, Any]): A dictionary of key-value pairs to update. Common keys include 'expected_revenue' (float), 'probability' (float), 'name' (str), 'description' (str), 'email_from' (str).
        
    Returns:
        Dict[str, Any]: A dictionary containing the success status.
    """
    logger.info("MCP Tool Called: update_lead", lead_id=lead_id)
    success = odoo_repo.update_lead(lead_id, data)
    return {"status": "success" if success else "failed"}


@mcp.tool()
@secure_tool()
def search_customer(name: str, limit: int = 20) -> List[Dict[str, Any]]:
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
    contacts = odoo_repo.search_contacts_by_name(name, limit=limit)
    return [contact.model_dump() for contact in contacts]


@mcp.tool()
@secure_tool()
def get_customer_details(partner_id: int) -> Dict[str, Any]:
    """
    Fetch comprehensive customer details and recent quotes.
    
    Use this tool to generate a 360-degree view of a customer.
    
    Args:
        partner_id (int): The exact Odoo ID of the partner/customer.
        
    Returns:
        Dict[str, Any]: A dictionary containing the 'contact' dictionary and a 'recent_quotes' list.
    """
    logger.info("MCP Tool Called: get_customer_details", partner_id=partner_id)
    return crm_service.get_customer_summary_data(partner_id)


# --- Sales & Inventory Tools ---

@mcp.tool()
@secure_tool()
def get_products(name_query: str = "", limit: int = 50) -> List[Dict[str, Any]]:
    """
    Search for products in Odoo's inventory.
    
    Use this tool to check prices or availability of products.
    
    Args:
        name_query (str): The name query to search for. Leave blank to return all products up to the limit.
        limit (int): The maximum number of records to return.
        
    Returns:
        List[Dict[str, Any]]: A list of products with fields like id, name, list_price, default_code, and qty_available.
    """
    logger.info("MCP Tool Called: get_products", query=name_query)
    products = odoo_repo.search_products(name_query, limit=limit)
    return [product.model_dump() for product in products]


@mcp.tool()
@secure_tool()
def revenue_report() -> Dict[str, Any]:
    """
    Get the current sales dashboard and revenue report.
    (Note: This tool provides identical data to get_sales_dashboard).
    
    Returns:
        Dict[str, Any]: A dictionary containing total_revenue, active_leads_count, quotes_count, and win_rate_percentage.
    """
    logger.info("MCP Tool Called: revenue_report")
    dashboard = odoo_repo.get_dashboard()
    return dashboard.model_dump()


@mcp.tool()
@secure_tool()
def get_sales_dashboard() -> Dict[str, Any]:
    """
    Get the current sales dashboard metrics.
    (Note: This tool provides identical data to revenue_report).
    
    Returns:
        Dict[str, Any]: A dictionary containing total_revenue, active_leads_count, quotes_count, and win_rate_percentage.
    """
    logger.info("MCP Tool Called: get_sales_dashboard")
    dashboard = odoo_repo.get_dashboard()
    return dashboard.model_dump()


@mcp.tool()
@secure_tool()
def get_pipeline_forecast_data() -> List[Dict[str, Any]]:
    """
    Fetch active leads and pipeline data for sales forecasting.
    
    Use this tool to analyze the probability and expected revenue of current deals.
    
    Returns:
        List[Dict[str, Any]]: A list of leads with full fields.
    """
    logger.info("MCP Tool Called: get_pipeline_forecast_data")
    return crm_service.get_pipeline_data()


# --- Calendar & Email Tools ---

@mcp.tool()
@secure_tool()
@validate_write_input(ScheduleMeetingInput)
def schedule_meeting(name: str, start: str, stop: str, partner_ids: List[int], notes: str = "") -> Dict[str, Any]:
    """
    Schedule a meeting in Odoo's calendar and log raw notes.
    
    Use this tool to set up an appointment with customers.
    
    Args:
        name (str): The title of the meeting.
        start (str): The start time in ISO format (e.g., '2026-08-01 10:00:00').
        stop (str): The stop time in ISO format.
        partner_ids (List[int]): A list of Odoo partner IDs to invite to the meeting.
        notes (str): Optional meeting notes or agenda.
        
    Returns:
        Dict[str, Any]: A dictionary containing the success status and the new meeting_id.
    """
    logger.info("MCP Tool Called: schedule_meeting", name=name)
    result = crm_service.create_meeting(name, start, stop, partner_ids, notes)
    return result


@mcp.tool()
@secure_tool()
def get_lead_context(lead_id: int) -> Dict[str, Any]:
    """
    Fetch raw lead context to draft emails or perform analysis.
    
    Use this tool to get all details about a specific lead.
    
    Args:
        lead_id (int): The ID of the lead.
        
    Returns:
        Dict[str, Any]: A dictionary representing the lead.
    """
    logger.info("MCP Tool Called: get_lead_context", lead_id=lead_id)
    return crm_service.get_lead_context(lead_id)


if __name__ == "__main__":
    # For local testing of the MCP server
    mcp.run()
