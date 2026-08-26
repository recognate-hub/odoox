from typing import Any
from core.logger import get_logger
from mcp_app import server
from mcp_app.schemas import *
from mcp_app.security import secure_tool
from mcp_app.server import mcp, _span
from mcp_app.validation import validate_write_input

logger = get_logger(__name__)


@mcp.tool()
@secure_tool()
def get_recent_quotes(
    partner_id: int | None = None, limit: int = 50, expand_lines: bool = False
) -> list[dict[str, Any]]:
    """
    Retrieve a list of recent quotes and sales orders.

    Use this tool when:
    - The user asks for a list of recent quotes or sales.
    - The user wants to check the status of orders for the entire company or a specific customer.

    Args:
        partner_id (Optional[int]): Filter by a specific customer/partner ID. Leave empty for all recent quotes.
        limit (int): The maximum number of quotes to return.
        expand_lines (bool): Set to True if detailed nested order lines are needed. Default is False for fast, trimmed responses.

    Returns:
        List[Dict[str, Any]]: A list of quotes with amount, status, date, and customer.
    """
    logger.info(
        "MCP Tool Called: get_recent_quotes", partner_id=partner_id, limit=limit
    )
    odoo_repo, _ = server._get_tenant_service()
    expand_fields = ["order_line"] if expand_lines else None
    quotes = odoo_repo.get_recent_quotes(partner_id=partner_id, limit=limit, expand_fields=expand_fields)
    return [quote.model_dump(exclude_none=True) for quote in quotes]


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
        quote_id = odoo_repo.create_quote(partner_id, order_lines)
        odoo_repo.execute_method("sale.order", "action_confirm", [[quote_id]])
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




@mcp.tool()
@secure_tool()
def get_ready_to_ship_orders() -> list[dict[str, Any]]:
    """
    Analyzes all pending sales orders and checks them against current Finished Goods stock.
    Returns a list of Sales Orders that can be 100% fulfilled immediately.
    
    Use this tool when:
    - The user asks what orders are ready to ship.
    - The user wants to know which sales can be fulfilled from existing inventory.
    """
    with _span("mcp.get_ready_to_ship_orders"):
        odoo_repo, _ = server._get_tenant_service()
        from services.operations import OperationsService
        service = OperationsService(odoo_repo)
        return service.get_ready_to_ship_orders()
