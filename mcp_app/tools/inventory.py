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
def get_products(
    query: str = "", 
    limit: int = 50,
    category_id: int | None = None,
    active: bool | None = None,
    min_stock: float | None = None,
    summarize: bool = False
) -> list[dict[str, Any]] | dict[str, Any]:
    """
    Search for products in Odoo's inventory.

    Use this tool when:
    - The user asks to find a product by name or SKU.
    - The user wants to check prices or availability of products.
    - The user wants a list of all products.

    Args:
        query (str): The name or serial number (SKU) query to search for. Leave blank to return all products up to the limit.
        limit (int): The maximum number of records to return.
        category_id (Optional[int]): Filter by product category ID.
        active (Optional[bool]): Filter by active status (True for active, False for archived).
        min_stock (Optional[float]): Return only products with at least this much quantity available.

    Returns:
        List[Dict[str, Any]]: A list of products with fields like id, name, list_price, default_code, and qty_available.
    """
    logger.info("MCP Tool Called: get_products", query=query, category_id=category_id, min_stock=min_stock)
    odoo_repo, _ = server._get_tenant_service()
    products = odoo_repo.search_products(
        query, 
        limit=limit, 
        category_id=category_id, 
        active=active, 
        min_stock=min_stock
    )
    data = [product.model_dump() for product in products]
    if summarize:
        return {
            "metadata": {"total_returned": len(data)},
            "data": data,
            "summary": f"Found {len(data)} products."
        }
    return data


@mcp.tool()
@secure_tool()
def get_inventory_valuation(product_id: int | None = None, limit: int = 50, offset: int = 0) -> list[dict[str, Any]]:
    """
    Get inventory valuation layers.
    
    Args:
        product_id (int, optional): Filter by product ID.
        limit (int): Maximum results to return.
        offset (int): Number of records to skip for pagination.
    """
    with _span("mcp.get_inventory_valuation"):
        odoo_repo, _ = server._get_tenant_service()
        from services.inventory import InventoryService

        service = InventoryService(odoo_repo)
        return service.get_inventory_valuation(product_id, limit, offset)

@mcp.tool()
@secure_tool()
def analyze_inventory_health() -> dict[str, Any]:
    """
    Perform a deep health check on inventory. 
    Calculates tied-up capital and flags dead/slow-moving stock that is costing the company money.
    """
    with _span("mcp.analyze_inventory_health"):
        odoo_repo, _ = server._get_tenant_service()
        from services.operations import OperationsService
        service = OperationsService(odoo_repo)
        return service.analyze_inventory_health()


@mcp.tool()
@secure_tool()
def get_inventory_locations(limit: int = 50) -> list[dict[str, Any]]:
    """
    Retrieve inventory locations (warehouses, shelves, virtual locations).
    
    Use this tool when:
    - The user asks about warehouses, zones, or where items are stored.
    """
    logger.info("MCP Tool Called: get_inventory_locations")
    odoo_repo, _ = server._get_tenant_service()
    try:
        fields = ["name", "complete_name", "usage", "warehouse_id"]
        return odoo_repo.search_read_records("stock.location", [], fields, limit=limit)
    except Exception as e:
        logger.error("get_inventory_locations error", error=str(e))
        return [{"status": "error", "message": str(e)}]


@mcp.tool()
@secure_tool()
def get_stock_moves(product_id: int | None = None, limit: int = 50) -> list[dict[str, Any]]:
    """
    Retrieve a history of stock moves (transfers).
    
    Use this tool when:
    - The user asks for the history of an item's movement.
    - You need to track why inventory levels changed.
    """
    logger.info("MCP Tool Called: get_stock_moves", product_id=product_id)
    odoo_repo, _ = server._get_tenant_service()
    try:
        domain = [["product_id", "=", product_id]] if product_id else []
        fields = ["product_id", "location_id", "location_dest_id", "product_uom_qty", "state", "date"]
        return odoo_repo.search_read_records("stock.move", domain, fields, limit=limit)
    except Exception as e:
        logger.error("get_stock_moves error", error=str(e))
        return [{"status": "error", "message": str(e)}]


@mcp.tool()
@secure_tool()
def get_incoming_shipments(limit: int = 50) -> list[dict[str, Any]]:
    """
    Retrieve incoming shipments (receipts from vendors).
    
    Use this tool when:
    - The user asks what shipments are expected to arrive.
    """
    logger.info("MCP Tool Called: get_incoming_shipments")
    odoo_repo, _ = server._get_tenant_service()
    try:
        domain = [["picking_type_code", "=", "incoming"], ["state", "not in", ["done", "cancel"]]]
        fields = ["name", "partner_id", "scheduled_date", "state", "origin"]
        return odoo_repo.search_read_records("stock.picking", domain, fields, limit=limit)
    except Exception as e:
        logger.error("get_incoming_shipments error", error=str(e))
        return [{"status": "error", "message": str(e)}]


@mcp.tool()
@secure_tool()
def get_outgoing_shipments(limit: int = 50) -> list[dict[str, Any]]:
    """
    Retrieve outgoing shipments (deliveries to customers).
    
    Use this tool when:
    - The user asks what orders are waiting to be shipped or delivered.
    """
    logger.info("MCP Tool Called: get_outgoing_shipments")
    odoo_repo, _ = server._get_tenant_service()
    try:
        domain = [["picking_type_code", "=", "outgoing"], ["state", "not in", ["done", "cancel"]]]
        fields = ["name", "partner_id", "scheduled_date", "state", "origin"]
        return odoo_repo.search_read_records("stock.picking", domain, fields, limit=limit)
    except Exception as e:
        logger.error("get_outgoing_shipments error", error=str(e))
        return [{"status": "error", "message": str(e)}]
