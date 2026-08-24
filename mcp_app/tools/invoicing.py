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
    partner_id: int | None = None, state: str | None = None, limit: int = 50, offset: int = 0, date_from: str | None = None, date_to: str | None = None
) -> list[dict[str, Any]]:
    """
    List customer invoices with optional filters.

    Use this to check outstanding invoices, payment status, or invoice history.

    Args:
        partner_id (int, optional): Filter by customer partner ID.
        state (str, optional): Filter by state ('draft', 'posted', 'cancel').
        limit (int): Maximum results to return.
        offset (int): Number of records to skip for pagination.
        date_from (str, optional): Filter invoices dated on or after this date (YYYY-MM-DD).
        date_to (str, optional): Filter invoices dated on or before this date (YYYY-MM-DD).

    Returns:
        List[Dict]: Invoices with name, customer, total, residual, state, date, and payment status.
    """
    with _span("mcp.get_invoices"):
        logger.info("MCP Tool Called: get_invoices", partner_id=partner_id, state=state)
        odoo_repo, _ = server._get_tenant_service()
        from services.invoicing import InvoicingService

        service = InvoicingService(odoo_repo)
        return service.get_invoices(partner_id, state, limit, offset, date_from, date_to)


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

@mcp.tool()
@secure_tool()
def predict_cashflow_shortages() -> dict[str, Any]:
    """
    Analyzes unpaid Accounts Receivable (AR) vs Accounts Payable (AP)
    to forecast if the company will run out of cash in the next 30 days.
    """
    with _span("mcp.predict_cashflow_shortages"):
        logger.info("MCP Tool Called: predict_cashflow_shortages")
        odoo_repo, _ = server._get_tenant_service()
        from services.invoicing import InvoicingService

        service = InvoicingService(odoo_repo)
        return service.predict_cashflow_shortages()
