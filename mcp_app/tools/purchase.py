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
def get_purchase_orders(
    partner_id: int | None = None, limit: int = 20
) -> list[dict[str, Any]]:
    """
    List purchase orders, optionally filtered by vendor.

    Use this tool when:
    - The user asks for a list of purchase orders.
    - The user asks what orders were placed with a specific vendor/supplier.

    Args:
        partner_id (int, optional): Filter by vendor partner ID.
        limit (int): Maximum results to return.

    Returns:
        List[Dict]: Purchase orders with vendor, amounts, state, and dates.
    """
    with _span("mcp.get_purchase_orders"):
        odoo_repo, _ = server._get_tenant_service()
        from services.purchase import PurchaseService

        service = PurchaseService(odoo_repo)
        return service.get_purchase_orders(partner_id, limit)


@mcp.tool()
@secure_tool()
def get_purchase_order_lines(po_id: int) -> list[dict[str, Any]]:
    """
    Get the line items of a specific purchase order.

    Use this to see what products, quantities, and prices are on a PO, and check received quantities.

    Args:
        po_id (int): The ID of the purchase order.

    Returns:
        List[Dict]: PO lines with product, qty, price, subtotal, planned date, and received qty.
    """
    with _span("mcp.get_purchase_order_lines"):
        logger.info("MCP Tool Called: get_purchase_order_lines", po_id=po_id)
        odoo_repo, _ = server._get_tenant_service()
        from services.purchase import PurchaseService

        service = PurchaseService(odoo_repo)
        return service.get_purchase_order_lines(po_id)


@mcp.tool()
@secure_tool()
def get_vendor_bills(
    partner_id: int | None = None, limit: int = 50
) -> list[dict[str, Any]]:
    """
    List vendor bills (incoming invoices from suppliers).
    
    Use this tool when:
    - The user asks for a list of bills or expenses from vendors.
    - The user wants to see what money is owed to suppliers.

    Args:
        partner_id (int, optional): Filter by vendor partner ID.
        limit (int): Maximum results to return.

    Returns:
        List[Dict]: Vendor bills with name, vendor, total, state, date, and payment status.
    """
    with _span("mcp.get_vendor_bills"):
        logger.info("MCP Tool Called: get_vendor_bills", partner_id=partner_id)
        odoo_repo, _ = server._get_tenant_service()
        from services.purchase import PurchaseService

        service = PurchaseService(odoo_repo)
        return service.get_vendor_bills(partner_id, limit)




@mcp.tool()
@secure_tool()
def get_purchase_plan() -> list[dict[str, Any]]:
    """
    Analyzes active Manufacturing Orders and calculates raw material shortages based on current stock.
    Returns a list of raw materials critically short.
    """
    with _span("mcp.get_purchase_plan"):
        odoo_repo, _ = server._get_tenant_service()
        from services.operations import OperationsService
        service = OperationsService(odoo_repo)
        return service.get_purchase_plan()
