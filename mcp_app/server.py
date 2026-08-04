from fastmcp import FastMCP
from typing import List, Optional, Dict, Any

from config.settings import get_settings
from core.logger import get_logger
from odoo.xmlrpc import XmlRpcOdooConnector
from repositories.odoo import OdooRepository
from services.crm import CRMService
from mcp_app.security import secure_tool

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
@secure_tool(allowed_roles=["Admin", "Sales", "Manager"])
def get_leads(limit: int = 100) -> List[Dict[str, Any]]:
    """Retrieve active CRM leads from Odoo."""
    logger.info("MCP Tool Called: get_leads", limit=limit)
    leads = odoo_repo.get_active_leads(limit=limit)
    return [lead.model_dump() for lead in leads]


@mcp.tool()
@secure_tool(allowed_roles=["Admin", "Sales"])
def create_lead(name: str, email: Optional[str] = None, phone: Optional[str] = None, description: Optional[str] = None) -> Dict[str, Any]:
    """Create a new CRM lead in Odoo."""
    logger.info("MCP Tool Called: create_lead", name=name)
    lead_id = odoo_repo.create_lead(name, email, phone, description)
    return {"status": "success", "lead_id": lead_id}


@mcp.tool()
@secure_tool(allowed_roles=["Admin", "Sales", "Manager", "Support"])
def search_customer(name: str, limit: int = 20) -> List[Dict[str, Any]]:
    """Search for contacts/customers in Odoo by name."""
    logger.info("MCP Tool Called: search_customer", query=name)
    contacts = odoo_repo.search_contacts_by_name(name, limit=limit)
    return [contact.model_dump() for contact in contacts]


@mcp.tool()
@secure_tool(allowed_roles=["Admin", "Sales", "Manager"])
def get_customer_details(partner_id: int) -> Dict[str, Any]:
    """Fetch raw customer details and recent quotes so Claude can generate a 360-degree view."""
    logger.info("MCP Tool Called: get_customer_details", partner_id=partner_id)
    return crm_service.get_customer_summary_data(partner_id)


# --- Sales & Inventory Tools ---

@mcp.tool()
@secure_tool(allowed_roles=["Admin", "Sales", "Manager", "Support"])
def get_products(name_query: str = "", limit: int = 50) -> List[Dict[str, Any]]:
    """Search for products in Odoo's inventory."""
    logger.info("MCP Tool Called: get_products", query=name_query)
    products = odoo_repo.search_products(name_query, limit=limit)
    return [product.model_dump() for product in products]


@mcp.tool()
@secure_tool(allowed_roles=["Admin", "Manager", "Finance"])
def revenue_report() -> Dict[str, Any]:
    """Get the current sales dashboard and revenue report."""
    logger.info("MCP Tool Called: revenue_report")
    dashboard = odoo_repo.get_dashboard()
    return dashboard.model_dump()


@mcp.tool()
@secure_tool(allowed_roles=["Admin", "Manager"])
def get_pipeline_forecast_data() -> List[Dict[str, Any]]:
    """Fetch active leads and pipeline data so Claude can generate a sales forecast."""
    logger.info("MCP Tool Called: get_pipeline_forecast_data")
    return crm_service.get_pipeline_data()


# --- Calendar & Email Tools ---

@mcp.tool()
@secure_tool(allowed_roles=["Admin", "Sales"])
def schedule_meeting(name: str, start: str, stop: str, partner_ids: List[int], notes: str = "") -> Dict[str, Any]:
    """
    Schedule a meeting in Odoo and log the raw notes.
    Dates should be in ISO format (e.g., '2026-08-01 10:00:00').
    """
    logger.info("MCP Tool Called: schedule_meeting", name=name)
    result = crm_service.create_meeting(name, start, stop, partner_ids, notes)
    return result


@mcp.tool()
@secure_tool(allowed_roles=["Admin", "Sales", "Support"])
def get_lead_context(lead_id: int) -> Dict[str, Any]:
    """Fetch raw lead context so Claude can draft an email or analyze it."""
    logger.info("MCP Tool Called: get_lead_context", lead_id=lead_id)
    return crm_service.get_lead_context(lead_id)


if __name__ == "__main__":
    # For local testing of the MCP server
    mcp.run()
