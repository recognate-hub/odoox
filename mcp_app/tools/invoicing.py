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
def get_invoices(
    partner_id: int | None = None,
    state: str | None = None,
    limit: int = 50,
    offset: int = 0,
    date_from: str | None = None,
    date_to: str | None = None,
    overdue_only: bool = False,
    summarize: bool = False
) -> list[dict[str, Any]] | dict[str, Any]:
    """
    List customer invoices with optional filters.

    Use this tool when:
    - The user asks for a list of customer invoices.
    - The user wants to check outstanding invoices, payment status, or invoice history.
    - The user asks for invoices for a specific customer or in a specific state.

    Args:
        partner_id (int, optional): Filter by customer partner ID.
        state (str, optional): Filter by state ('draft', 'posted', 'cancel').
        limit (int): Maximum results to return.
        offset (int): Number of records to skip for pagination.
        date_from (str, optional): Filter invoices dated on or after this date (YYYY-MM-DD).
        date_to (str, optional): Filter invoices dated on or before this date (YYYY-MM-DD).
        overdue_only (bool): Filter only overdue invoices.
        summarize (bool): Return a summary dictionary.

    Returns:
        List[Dict]: Invoices with name, customer, total, residual, state, date, and payment status.
    """
    with _span("mcp.get_invoices"):
        logger.info("MCP Tool Called: get_invoices", partner_id=partner_id, state=state, overdue_only=overdue_only)
        odoo_repo, _ = server._get_tenant_service()
        from services.invoicing import InvoicingService

        service = InvoicingService(odoo_repo)
        invoices = service.get_invoices(partner_id, state, limit, offset, date_from, date_to, overdue_only=overdue_only)
        if summarize:
            return {
                "metadata": {"total_returned": len(invoices)},
                "data": invoices,
                "summary": f"Found {len(invoices)} invoices."
            }
        return invoices


@mcp.tool()
@secure_tool()
def get_payment_journals() -> list[dict[str, Any]]:
    """
    List available payment journals (bank accounts, cash registers).

    Use this tool when:
    - You need to find the journal_id to use with the register_payment tool.
    - The user asks what bank accounts or payment methods are available.

    Returns:
        List[Dict]: Journals with name, type, and currency.
    """
    with _span("mcp.get_payment_journals"):
        logger.info("MCP Tool Called: get_payment_journals")
        odoo_repo, _ = server._get_tenant_service()
        from services.invoicing import InvoicingService

        service = InvoicingService(odoo_repo)
        return service.get_payment_journals()

@mcp.tool()
@secure_tool()
def predict_cashflow_shortages() -> dict[str, Any]:
    """
    Analyzes unpaid Accounts Receivable (AR) vs Accounts Payable (AP)
    to forecast if the company will run out of cash in the next 30 days.
    
    Use this tool when:
    - The user asks about cashflow, cash shortages, or financial health.
    - The user asks if they can afford an upcoming expense.
    
    Returns:
        Dict[str, Any]: A dictionary containing AR/AP metrics and cashflow predictions.
    """
    with _span("mcp.predict_cashflow_shortages"):
        logger.info("MCP Tool Called: predict_cashflow_shortages")
        odoo_repo, _ = server._get_tenant_service()
        from services.invoicing import InvoicingService

        service = InvoicingService(odoo_repo)
        return service.predict_cashflow_shortages()
