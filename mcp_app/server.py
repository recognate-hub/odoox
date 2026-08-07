from typing import Any

from fastmcp import FastMCP

from config.settings import get_settings
from core.logger import get_logger
from mcp_app.schemas import (
    CreateLeadInput,
    LogActivityInput,
    ScheduleMeetingInput,
    UpdateLeadInput,
    CreateInvoiceInput,
    SendEmailInput,
)
from mcp_app.security import secure_tool
from mcp_app.validation import validate_write_input
from odoo.xmlrpc import XmlRpcOdooConnector
from repositories.odoo import OdooRepository
from services.crm import CRMService

logger = get_logger(__name__)

try:
    from opentelemetry import trace
    tracer = trace.get_tracer(__name__)
except Exception:  # noqa: BLE001
    tracer = None  # type: ignore

from contextlib import nullcontext


def _span(name: str):
    """Return a tracing span context manager, or a no-op if OTel is unavailable."""
    if tracer:
        return tracer.start_as_current_span(name)
    return nullcontext()


def _get_tenant_service() -> tuple[OdooRepository, CRMService]:
    """
    Lazily create an OdooConnector using the current tenant's credentials.
    This is called per-request so each tenant gets their own connection.
    """
    # The XmlRpcOdooConnector automatically reads the credentials from the
    # current_token and get_workspace_credentials context when making calls.
    settings = get_settings()
    connector = XmlRpcOdooConnector(settings)
    repo = OdooRepository(connector)
    service = CRMService(repo)
    return repo, service


# Initialize FastMCP Server
mcp = FastMCP("ODOOX")

# --- CRM Tools ---

@mcp.tool()
@secure_tool()
def get_leads(name_query: str | None = None, stage_id: int | None = None, limit: int = 100) -> list[dict[str, Any]]:
    """
    Retrieve active CRM leads (opportunities) from Odoo.
    
    Use this tool to fetch a list of current active sales leads or search for specific leads.
    
    Args:
        name_query (Optional[str]): Search by lead name (case-insensitive partial match).
        stage_id (Optional[int]): Filter by a specific pipeline stage ID.
        limit (int): The maximum number of leads to return. Default is 100.
        
    Returns:
        List[Dict[str, Any]]: A list of dictionaries representing leads with fields like name, email_from, phone, partner_id, stage_id, expected_revenue, and description.
    """
    with _span("mcp.get_leads") as span:
        if span:
            span.set_attribute("limit", limit)
        logger.info("MCP Tool Called: get_leads", limit=limit, query=name_query, stage_id=stage_id)
        odoo_repo, _ = _get_tenant_service()
        leads = odoo_repo.get_active_leads(name_query=name_query, stage_id=stage_id, limit=limit)
        if span:
            span.set_attribute("returned_leads", len(leads))
        return [lead.model_dump() for lead in leads]


@mcp.tool()
@secure_tool()
@validate_write_input(CreateLeadInput)
def create_lead(name: str, email: str | None = None, phone: str | None = None, description: str | None = None) -> dict[str, Any]:
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
    with _span("mcp.create_lead") as span:
        if span:
            span.set_attribute("lead.name", name)
        logger.info("MCP Tool Called: create_lead", name=name)
        odoo_repo, _ = _get_tenant_service()
        lead_id = odoo_repo.create_lead(name, email, phone, description)
        if span:
            span.set_attribute("lead.id", lead_id)
        return {"status": "success", "lead_id": lead_id}


@mcp.tool()
@secure_tool()
@validate_write_input(UpdateLeadInput)
def update_lead(lead_id: int, data: dict[str, Any]) -> dict[str, Any]:
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
    odoo_repo, _ = _get_tenant_service()
    success = odoo_repo.update_lead(lead_id, data)
    return {"status": "success" if success else "failed"}


@mcp.tool()
@secure_tool()
@validate_write_input(LogActivityInput)
def log_crm_note(res_model: str, res_id: int, summary: str) -> dict[str, Any]:
    """
    Log a note or activity on an Odoo record.
    
    Use this tool to add call notes, meeting summaries, or updates to a lead/contact.
    
    Args:
        res_model (str): The Odoo model (e.g., 'crm.lead', 'res.partner').
        res_id (int): The ID of the record.
        summary (str): The text content of the note.
        
    Returns:
        Dict[str, Any]: The status of the operation and activity ID.
    """
    logger.info("MCP Tool Called: log_crm_note", model=res_model, id=res_id)
    odoo_repo, _ = _get_tenant_service()
    # 4 is usually 'Todo' or general note
    activity_id = odoo_repo.log_activity(res_model, res_id, summary, activity_type_id=4)
    return {"status": "success", "activity_id": activity_id}


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
    odoo_repo, _ = _get_tenant_service()
    contacts = odoo_repo.search_contacts_by_name(name, limit=limit)
    return [contact.model_dump() for contact in contacts]


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
    _, crm_service = _get_tenant_service()
    return crm_service.get_customer_summary_data(partner_id)


# --- Sales & Inventory Tools ---

@mcp.tool()
@secure_tool()
def get_products(name_query: str = "", limit: int = 50) -> list[dict[str, Any]]:
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
    odoo_repo, _ = _get_tenant_service()
    products = odoo_repo.search_products(name_query, limit=limit)
    return [product.model_dump() for product in products]


@mcp.tool()
@secure_tool()
def get_recent_quotes(partner_id: int | None = None, limit: int = 50) -> list[dict[str, Any]]:
    """
    Retrieve a list of recent quotes and sales orders.
    
    Use this tool to check the status of orders or look up quotes for the entire company or a specific customer.
    
    Args:
        partner_id (Optional[int]): Filter by a specific customer/partner ID. Leave empty for all recent quotes.
        limit (int): The maximum number of quotes to return.
        
    Returns:
        List[Dict[str, Any]]: A list of quotes with amount, status, and partner_id.
    """
    logger.info("MCP Tool Called: get_recent_quotes", partner_id=partner_id, limit=limit)
    odoo_repo, _ = _get_tenant_service()
    quotes = odoo_repo.get_recent_quotes(partner_id=partner_id, limit=limit)
    return [quote.model_dump() for quote in quotes]


@mcp.tool()
@secure_tool()
def revenue_report() -> dict[str, Any]:
    """
    Get the current sales dashboard and revenue report.
    (Note: This tool provides identical data to get_sales_dashboard).
    
    Returns:
        Dict[str, Any]: A dictionary containing total_revenue, active_leads_count, quotes_count, and win_rate_percentage.
    """
    logger.info("MCP Tool Called: revenue_report")
    odoo_repo, _ = _get_tenant_service()
    dashboard = odoo_repo.get_dashboard()
    return dashboard.model_dump()


@mcp.tool()
@secure_tool()
def get_sales_dashboard() -> dict[str, Any]:
    """
    Get the current sales dashboard metrics.
    (Note: This tool provides identical data to revenue_report).
    
    Returns:
        Dict[str, Any]: A dictionary containing total_revenue, active_leads_count, quotes_count, and win_rate_percentage.
    """
    logger.info("MCP Tool Called: get_sales_dashboard")
    odoo_repo, _ = _get_tenant_service()
    dashboard = odoo_repo.get_dashboard()
    return dashboard.model_dump()


@mcp.tool()
@secure_tool()
def get_pipeline_forecast_data() -> list[dict[str, Any]]:
    """
    Fetch active leads and pipeline data for sales forecasting.
    
    Use this tool to analyze the probability and expected revenue of current deals.
    
    Returns:
        List[Dict[str, Any]]: A list of leads with full fields.
    """
    logger.info("MCP Tool Called: get_pipeline_forecast_data")
    _, crm_service = _get_tenant_service()
    return crm_service.get_pipeline_data()


# --- Calendar & Email Tools ---

@mcp.tool()
@secure_tool()
@validate_write_input(ScheduleMeetingInput)
def schedule_meeting(name: str, start: str, stop: str, partner_ids: list[int], notes: str = "") -> dict[str, Any]:
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
    _, crm_service = _get_tenant_service()
    result = crm_service.create_meeting(name, start, stop, partner_ids, notes)
    return result


@mcp.tool()
@secure_tool()
def get_lead_context(lead_id: int) -> dict[str, Any]:
    """
    Fetch raw lead context to draft emails or perform analysis.
    
    Use this tool to get all details about a specific lead.
    
    Args:
        lead_id (int): The ID of the lead.
        
    Returns:
        Dict[str, Any]: A dictionary representing the lead.
    """
    logger.info("MCP Tool Called: get_lead_context", lead_id=lead_id)
    _, crm_service = _get_tenant_service()
    return crm_service.get_lead_context(lead_id)


@mcp.tool()
@secure_tool()
@validate_write_input(CreateInvoiceInput)
def create_invoice(partner_id: int, amount: float, description: str = "Consulting Services") -> dict[str, Any]:
    """
    Create a draft customer invoice in Odoo.
    
    Use this tool to bill a customer for a specific amount.
    
    Args:
        partner_id (int): The ID of the customer.
        amount (float): The total amount for the invoice line.
        description (str): The description for the invoice line item.
        
    Returns:
        Dict[str, Any]: The status of the operation and new invoice ID.
    """
    logger.info("MCP Tool Called: create_invoice", partner_id=partner_id, amount=amount)
    odoo_repo, _ = _get_tenant_service()
    invoice_id = odoo_repo.create_invoice(partner_id, amount, description)
    return {"status": "success", "invoice_id": invoice_id}


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
    odoo_repo, _ = _get_tenant_service()
    mail_id = odoo_repo.send_email(email_to, subject, body)
    return {"status": "success", "mail_id": mail_id}


if __name__ == "__main__":
    # For local testing of the MCP server
    mcp.run()
