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
@validate_write_input(CreatePurchaseOrderInput)
def create_purchase_order(partner_id: int, order_lines: list[dict]) -> dict[str, Any]:
    """
    Create a new purchase order for a vendor.

    Args:
        partner_id (int): The ID of the vendor (partner).
        order_lines (List[Dict]): List of line items with product_id, product_qty, and optional price_unit.
    """
    with _span("mcp.create_purchase_order"):
        odoo_repo, _ = server._get_tenant_service()
        from services.purchase import PurchaseService

        service = PurchaseService(odoo_repo)
        return service.create_purchase_order(partner_id, order_lines)


@mcp.tool()
@secure_tool()
def get_purchase_orders(
    partner_id: int | None = None, limit: int = 20
) -> list[dict[str, Any]]:
    """
    List purchase orders, optionally filtered by vendor.

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
@validate_write_input(UpdatePurchaseOrderInput)
def update_purchase_order(po_id: int, data: dict[str, Any]) -> dict[str, Any]:
    """
    Update a purchase order (e.g., change vendor reference, planned date).

    Args:
        po_id (int): The ID of the purchase order.
        data (Dict): Fields to update.

    Returns:
        Dict: Status of the update.
    """
    with _span("mcp.update_purchase_order"):
        logger.info("MCP Tool Called: update_purchase_order", po_id=po_id)
        odoo_repo, _ = server._get_tenant_service()
        from services.purchase import PurchaseService

        service = PurchaseService(odoo_repo)
        return service.update_purchase_order(po_id, data)


@mcp.tool()
@secure_tool()
@validate_write_input(ConfirmPurchaseOrderInput)
def confirm_purchase_order(po_id: int) -> dict[str, Any]:
    """
    Confirm a draft purchase order, triggering the procurement workflow.

    Args:
        po_id (int): The ID of the purchase order to confirm.

    Returns:
        Dict: Status of the confirmation.
    """
    with _span("mcp.confirm_purchase_order"):
        logger.info("MCP Tool Called: confirm_purchase_order", po_id=po_id)
        odoo_repo, _ = server._get_tenant_service()
        from services.purchase import PurchaseService

        service = PurchaseService(odoo_repo)
        return service.confirm_purchase_order(po_id)


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
