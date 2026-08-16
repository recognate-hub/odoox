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
@validate_write_input(CreateInvoiceInput)
def create_invoice(partner_id: int, amount: float, description: str = "Consulting Services") -> dict[str, Any]:
    """
    Create a draft customer invoice in Odoo.
    
    Args:
        partner_id (int): The ID of the customer.
        amount (float): The total amount for the invoice line.
        description (str): The description for the invoice line item.
        
    Returns:
        Dict: Status and new invoice_id.
    """
    logger.info("MCP Tool Called: create_invoice", partner_id=partner_id, amount=amount)
    odoo_repo, _ = server._get_tenant_service()
    invoice_id = odoo_repo.create_invoice(partner_id, amount, description)
    return {"status": "success", "invoice_id": invoice_id}


@mcp.tool()
@secure_tool()
def get_invoices(partner_id: int | None = None, state: str | None = None, limit: int = 50) -> list[dict[str, Any]]:
    """
    List customer invoices with optional filters.
    
    Use this to check outstanding invoices, payment status, or invoice history.
    
    Args:
        partner_id (int, optional): Filter by customer partner ID.
        state (str, optional): Filter by state ('draft', 'posted', 'cancel').
        limit (int): Maximum results to return.
        
    Returns:
        List[Dict]: Invoices with name, customer, total, residual, state, date, and payment status.
    """
    with _span("mcp.get_invoices"):
        logger.info("MCP Tool Called: get_invoices", partner_id=partner_id, state=state)
        odoo_repo, _ = server._get_tenant_service()
        from services.invoicing import InvoicingService
        service = InvoicingService(odoo_repo)
        return service.get_invoices(partner_id, state, limit)


@mcp.tool()
@secure_tool()
@validate_write_input(PostInvoiceInput)
def post_invoice(invoice_id: int) -> dict[str, Any]:
    """
    Post/validate a draft invoice, moving it from 'draft' to 'posted' state.
    
    This creates the accounting journal entries and makes the invoice official.
    
    Args:
        invoice_id (int): The ID of the invoice to post.
        
    Returns:
        Dict: Status of the post operation.
    """
    with _span("mcp.post_invoice"):
        logger.info("MCP Tool Called: post_invoice", invoice_id=invoice_id)
        odoo_repo, _ = server._get_tenant_service()
        from services.invoicing import InvoicingService
        service = InvoicingService(odoo_repo)
        return service.post_invoice(invoice_id)


@mcp.tool()
@secure_tool()
@validate_write_input(RegisterPaymentInput)
def register_payment(invoice_id: int, amount: float, journal_id: int) -> dict[str, Any]:
    """
    Register a payment against a posted invoice.
    
    Use get_payment_journals first to find the correct journal_id for the payment method.
    
    Args:
        invoice_id (int): The ID of the invoice to pay.
        amount (float): The payment amount.
        journal_id (int): The ID of the payment journal (bank/cash). Use get_payment_journals to find this.
        
    Returns:
        Dict: Status and payment result.
    """
    with _span("mcp.register_payment"):
        logger.info("MCP Tool Called: register_payment", invoice_id=invoice_id, amount=amount)
        odoo_repo, _ = server._get_tenant_service()
        from services.invoicing import InvoicingService
        service = InvoicingService(odoo_repo)
        return service.register_payment(invoice_id, amount, journal_id)


@mcp.tool()
@secure_tool()
def get_payment_journals() -> list[dict[str, Any]]:
    """
    List available payment journals (bank accounts, cash registers).
    
    Use this to find the journal_id needed for the register_payment tool.
    
    Returns:
        List[Dict]: Journals with name, type, and currency.
    """
    with _span("mcp.get_payment_journals"):
        logger.info("MCP Tool Called: get_payment_journals")
        odoo_repo, _ = server._get_tenant_service()
        from services.invoicing import InvoicingService
        service = InvoicingService(odoo_repo)
        return service.get_payment_journals()
