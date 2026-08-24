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
    odoo_repo, _ = server._get_tenant_service()
    products = odoo_repo.search_products(query, limit=limit)
    return [product.model_dump() for product in products]


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
        from services.inventory import InventoryService

        service = InventoryService(odoo_repo)
        return service.analyze_inventory_health()
