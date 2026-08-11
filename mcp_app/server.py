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
    CreateContactInput,
    CreateProductInput,
    CreateQuoteInput,
    SearchReadInput,
    CreateRecordInput,
    UpdateRecordInput,
    GetModelFieldsInput,
    ReadGroupInput,
    ArchiveRecordInput,
    CreateAttachmentInput,
    ReadAttachmentInput,
    ExecuteMethodInput,
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
    odoo_repo, _ = _get_tenant_service()
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
    _, crm_service = _get_tenant_service()
    return crm_service.get_customer_summary_data(partner_id)


# --- Sales & Inventory Tools ---

@mcp.tool()
@secure_tool()
def get_products(query: str = "", limit: int = 50) -> list[dict[str, Any]]:
    """
    Search for products in Odoo's inventory.
    
    Use this tool to check prices, availability, or details of products.
    
    Args:
        query (str): The name or serial number (SKU) query to search for. Leave blank to return all products up to the limit.
        limit (int): The maximum number of records to return.
        
    Returns:
        List[Dict[str, Any]]: A list of products with fields like id, name, list_price, default_code, and qty_available.
    """
    logger.info("MCP Tool Called: get_products", query=query)
    odoo_repo, _ = _get_tenant_service()
    products = odoo_repo.search_products(query, limit=limit)
    return [product.model_dump() for product in products]


@mcp.tool()
@secure_tool()
@validate_write_input(CreateProductInput)
def create_product(name: str, list_price: float, default_code: str | None = None, product_type: str = "service") -> dict[str, Any]:
    """
    Create a new product or service in Odoo's inventory.
    
    Use this tool to add new offerings to the catalog.
    
    Args:
        name (str): The name of the product.
        list_price (float): The sale price.
        default_code (Optional[str]): Internal reference or SKU.
        product_type (str): Usually 'consu', 'service', or 'product'.
        
    Returns:
        Dict[str, Any]: The status of the operation and new product ID.
    """
    logger.info("MCP Tool Called: create_product", name=name)
    odoo_repo, _ = _get_tenant_service()
    product_id = odoo_repo.create_product(name, list_price, default_code, type_code=product_type)
    return {"status": "success", "product_id": product_id}


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
@validate_write_input(CreateQuoteInput)
def create_quote(partner_id: int, order_lines: list[dict]) -> dict[str, Any]:
    """
    Create a new sales quotation or order.
    
    Use this tool to generate a full quote for a customer.
    
    Args:
        partner_id (int): The ID of the customer.
        order_lines (List[Dict]): List of line items, each must have 'product_id', 'quantity', and optional 'price_unit'.
        
    Returns:
        Dict[str, Any]: The status of the operation and new order ID.
    """
    logger.info("MCP Tool Called: create_quote", partner_id=partner_id)
    odoo_repo, _ = _get_tenant_service()
    quote_id = odoo_repo.create_quote(partner_id, order_lines)
    return {"status": "success", "quote_id": quote_id}


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

# --- Generic Odoo Integration Tools ---

@mcp.tool()
@secure_tool()
def search_read_records(model: str, domain: list[list[Any]] | None = None, fields: list[str] | None = None, limit: int = 50, offset: int = 0) -> list[dict[str, Any]]:
    """
    Generic tool to read records from ANY Odoo module or model.
    Use this to interact with HR, Project, Manufacturing, or other Odoo apps not explicitly covered by other tools.

    Args:
        model (str): The name of the Odoo model (e.g., 'hr.employee', 'project.task', 'mrp.production').
        domain (list): A list of search criteria to filter records. For example: [["name", "ilike", "John"]].
        fields (list): A list of fields to return. If omitted, returns all fields.
        limit (int): The maximum number of records to return (max 200).
        offset (int): The number of records to skip for pagination.
        
    Returns:
        list: A list of dictionaries representing the records matching the domain.
    """
    logger.info("MCP Tool Called: search_read_records", model=model, domain=domain)
    odoo_repo, _ = _get_tenant_service()
    if limit > 200:
        limit = 200
    try:
        return odoo_repo.search_read_records(model, domain=domain, fields=fields, limit=limit, offset=offset)
    except Exception as e:
        logger.error("search_read_records error", error=str(e))
        raise RuntimeError(f"Odoo search_read_records failed: {e!s}") from e

@mcp.tool()
@secure_tool()
@validate_write_input(CreateRecordInput)
def create_record(model: str, data: dict[str, Any]) -> dict[str, Any]:
    """
    Generic tool to create a record in ANY Odoo module or model.

    Args:
        model (str): The name of the Odoo model.
        data (dict): A dictionary mapping field names to values.

    Returns:
        dict: Status and ID of the newly created record.
    """
    logger.info("MCP Tool Called: create_record", model=model)
    odoo_repo, _ = _get_tenant_service()
    try:
        record_id = odoo_repo.create_record(model, data)
        return {"status": "success", "record_id": record_id}
    except Exception as e:
        logger.error("create_record error", error=str(e))
        return {"status": "error", "message": str(e)}

@mcp.tool()
@secure_tool()
@validate_write_input(UpdateRecordInput)
def update_record(model: str, record_id: int, data: dict[str, Any]) -> dict[str, Any]:
    """
    Generic tool to update a record in ANY Odoo module or model.

    Args:
        model (str): The name of the Odoo model.
        record_id (int): The ID of the record to update.
        data (dict): A dictionary of fields and values to update.

    Returns:
        dict: Status of the update operation.
    """
    logger.info("MCP Tool Called: update_record", model=model, record_id=record_id)
    odoo_repo, _ = _get_tenant_service()
    try:
        success = odoo_repo.update_record(model, record_id, data)
        return {"status": "success"} if success else {"status": "error", "message": "Update failed"}
    except Exception as e:
        logger.error("update_record error", error=str(e))
        return {"status": "error", "message": str(e)}

@mcp.tool()
@secure_tool()
def get_installed_apps() -> list[dict[str, Any]]:
    """
    Retrieve a list of installed applications/modules in the Odoo instance.
    
    Returns:
        List[Dict[str, Any]]: A list of installed apps.
    """
    with _span("mcp.get_installed_apps"):
        logger.info("MCP Tool Called: get_installed_apps")
        odoo_repo, _ = _get_tenant_service()
        return odoo_repo.get_installed_apps()

@mcp.tool()
@secure_tool()
def check_stock_availability(product_id: int) -> list[dict[str, Any]]:
    """
    Check the stock availability for a specific product across all locations.
    
    Args:
        product_id (int): The ID of the product in Odoo.
        
    Returns:
        List[Dict[str, Any]]: A list of stock quantities per location.
    """
    with _span("mcp.check_stock_availability") as span:
        if span:
            span.set_attribute("product_id", product_id)
        logger.info("MCP Tool Called: check_stock_availability", product_id=product_id)
        odoo_repo, _ = _get_tenant_service()
        return odoo_repo.get_product_stock(product_id)

@mcp.tool()
@secure_tool()
def create_sales_invoice(partner_id: int, amount: float, description: str) -> dict[str, Any]:
    """
    Create a new customer invoice (account.move) for a specific partner.
    
    Args:
        partner_id (int): The ID of the customer in Odoo.
        amount (float): The total amount for the invoice line.
        description (str): The description for the invoice line.
        
    Returns:
        Dict[str, Any]: The ID of the newly created invoice.
    """
    with _span("mcp.create_sales_invoice") as span:
        if span:
            span.set_attribute("partner_id", partner_id)
        logger.info("MCP Tool Called: create_sales_invoice", partner_id=partner_id, amount=amount)
        odoo_repo, _ = _get_tenant_service()
        invoice_id = odoo_repo.create_invoice(partner_id, amount, description)
        return {"invoice_id": invoice_id}

@mcp.tool()
@secure_tool()
@validate_write_input(GetModelFieldsInput)
def get_model_fields(model: str) -> dict[str, Any]:
    """
    Get the schema and all available fields for a specific Odoo model (e.g., 'stock.lot', 'hr.employee').
    Use this to discover custom fields (like 'x_metric_1', 'x_return_reason') before querying a model.
    
    Args:
        model (str): The Odoo model name to inspect.
        
    Returns:
        dict: A dictionary mapping field names to their metadata (type, string label, selection options, etc.).
    """
    logger.info("MCP Tool Called: get_model_fields", model=model)
    odoo_repo, _ = _get_tenant_service()
    try:
        return odoo_repo.get_model_fields(model)
    except Exception as e:
        logger.error("get_model_fields error", error=str(e))
        return {"status": "error", "message": str(e)}

@mcp.tool()
@secure_tool()
@validate_write_input(ReadGroupInput)
def read_group_records(model: str, domain: list[list[Any]] | None = None, fields: list[str] | None = None, groupby: list[str] | None = None) -> list[dict[str, Any]]:
    """
    Perform a read_group operation on an Odoo model for aggregation (e.g., sum, count).
    
    Args:
        model (str): The Odoo model name.
        domain (list): Search criteria.
        fields (list): Fields to fetch/aggregate.
        groupby (list): Fields to group by.
        
    Returns:
        list: A list of aggregated records.
    """
    logger.info("MCP Tool Called: read_group_records", model=model, groupby=groupby)
    odoo_repo, _ = _get_tenant_service()
    try:
        return odoo_repo.read_group(model, domain=domain or [], fields=fields or [], groupby=groupby or [])
    except Exception as e:
        logger.error("read_group_records error", error=str(e))
        raise RuntimeError(f"Odoo read_group_records failed: {e!s}") from e

@mcp.tool()
@secure_tool()
@validate_write_input(ArchiveRecordInput)
def archive_record(model: str, record_id: int, archive: bool = True) -> dict[str, Any]:
    """
    Archive or unarchive a record in Odoo (sets active=False/True).
    
    Args:
        model (str): The Odoo model name.
        record_id (int): The ID of the record.
        archive (bool): True to archive, False to unarchive.
        
    Returns:
        dict: Status of the operation.
    """
    logger.info("MCP Tool Called: archive_record", model=model, record_id=record_id, archive=archive)
    odoo_repo, _ = _get_tenant_service()
    try:
        success = odoo_repo.archive_record(model, record_id, archive)
        return {"status": "success"} if success else {"status": "error", "message": "Archive failed"}
    except Exception as e:
        logger.error("archive_record error", error=str(e))
        return {"status": "error", "message": str(e)}

@mcp.tool()
@secure_tool()
def get_attachment(attachment_id: int) -> dict[str, Any]:
    """
    Fetch an attachment from Odoo (ir.attachment).
    Base64 data is truncated if it's too large to prevent context limits.
    
    Args:
        attachment_id (int): The ID of the attachment.
        
    Returns:
        dict: The attachment data including base64 content.
    """
    logger.info("MCP Tool Called: get_attachment", attachment_id=attachment_id)
    odoo_repo, _ = _get_tenant_service()
    try:
        attachment = odoo_repo.get_attachment(attachment_id)
        if attachment.get("datas") and len(attachment["datas"]) > 100000:
            attachment["datas"] = attachment["datas"][:100000] + "...[TRUNCATED]"
            attachment["_truncated"] = True
        return attachment
    except Exception as e:
        logger.error("get_attachment error", error=str(e))
        return {"status": "error", "message": str(e)}

@mcp.tool()
@secure_tool()
@validate_write_input(CreateAttachmentInput)
def create_attachment(res_model: str, res_id: int, name: str, base64_data: str) -> dict[str, Any]:
    """
    Create a new file attachment in Odoo and link it to a record.
    
    Args:
        res_model (str): The model to attach to.
        res_id (int): The record ID.
        name (str): The file name.
        base64_data (str): The base64 encoded file content.
        
    Returns:
        dict: Status and new attachment_id.
    """
    logger.info("MCP Tool Called: create_attachment", res_model=res_model, res_id=res_id)
    odoo_repo, _ = _get_tenant_service()
    try:
        data = {
            "name": name,
            "res_model": res_model,
            "res_id": res_id,
            "datas": base64_data,
            "type": "binary"
        }
        attachment_id = odoo_repo.create_attachment(data)
        return {"status": "success", "attachment_id": attachment_id}
    except Exception as e:
        logger.error("create_attachment error", error=str(e))
        return {"status": "error", "message": str(e)}

@mcp.tool()
@secure_tool()
@validate_write_input(ExecuteMethodInput)
def execute_model_method(model: str, method: str, args: list[Any] | None = None, kwargs: dict[str, Any] | None = None) -> Any:
    """
    Execute any arbitrary method on an Odoo model.
    This allows you to trigger Odoo workflows (e.g. 'action_confirm' on a sales order, 'action_post' on an invoice).
    """
    logger.info("MCP Tool Called: execute_model_method", model=model, method=method)
    odoo_repo, _ = _get_tenant_service()
    try:
        return odoo_repo.execute_method(model, method, args, kwargs)
    except Exception as e:
        logger.error("execute_model_method error", error=str(e))
        raise RuntimeError(f"Failed to execute method {method} on {model}: {e}")

if __name__ == "__main__":
    from core.secrets import initialize_secrets
    initialize_secrets()
    mcp.run()
