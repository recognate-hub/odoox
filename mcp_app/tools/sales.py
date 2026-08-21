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
def get_recent_quotes(
    partner_id: int | None = None, limit: int = 50
) -> list[dict[str, Any]]:
    """
    Retrieve a list of recent quotes and sales orders.

    Use this tool to check the status of orders or look up quotes for the entire company or a specific customer.

    Args:
        partner_id (Optional[int]): Filter by a specific customer/partner ID. Leave empty for all recent quotes.
        limit (int): The maximum number of quotes to return.

    Returns:
        List[Dict[str, Any]]: A list of quotes with amount, status, and partner_id.
    """
    logger.info(
        "MCP Tool Called: get_recent_quotes", partner_id=partner_id, limit=limit
    )
    odoo_repo, _ = server._get_tenant_service()
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
    odoo_repo, _ = server._get_tenant_service()
    quote_id = odoo_repo.create_quote(partner_id, order_lines)
    return {"status": "success", "quote_id": quote_id}


@mcp.tool()
@secure_tool()
@validate_write_input(QuoteToCashInput)
def quote_to_cash_automation(
    partner_id: int, order_lines: list[dict]
) -> dict[str, Any]:
    """
    Automate the full quote-to-cash workflow for a customer.
    Creates a quote, confirms it into a sales order, and creates an invoice.
    """
    logger.info("MCP Tool Called: quote_to_cash_automation", partner_id=partner_id)
    odoo_repo, _ = server._get_tenant_service()
    try:
        # 1. Create Quote
        quote_id = odoo_repo.create_quote(partner_id, order_lines)

        # 2. Confirm Quote to Sales Order
        odoo_repo.execute_method("sale.order", "action_confirm", [[quote_id]])

        # 3. Create Invoice (using standard internal workflow method)
        invoice_result = odoo_repo.execute_method(
            "sale.order", "_create_invoices", [[quote_id]]
        )

        return {
            "status": "success",
            "quote_id": quote_id,
            "invoice_result": invoice_result,
        }
    except Exception as e:
        logger.error("quote_to_cash_automation error", error=str(e))
        return {"status": "error", "message": str(e)}
