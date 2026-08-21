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
@validate_write_input(CreateProductInput)
def create_product(
    name: str,
    list_price: float,
    default_code: str | None = None,
    product_type: str = "service",
) -> dict[str, Any]:
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
    odoo_repo, _ = server._get_tenant_service()
    product_id = odoo_repo.create_product(
        name, list_price, default_code, type_code=product_type
    )
    return {"status": "success", "product_id": product_id}


@mcp.tool()
@secure_tool()
@validate_write_input(CreateStockMoveInput)
def create_stock_move(
    name: str,
    product_id: int,
    product_uom_qty: float,
    location_id: int,
    location_dest_id: int,
) -> dict[str, Any]:
    with _span("mcp.create_stock_move"):
        odoo_repo, _ = server._get_tenant_service()
        from services.inventory import InventoryService

        service = InventoryService(odoo_repo)
        return service.create_stock_move(
            name, product_id, product_uom_qty, location_id, location_dest_id
        )


@mcp.tool()
@secure_tool()
def get_inventory_valuation(product_id: int | None = None) -> list[dict[str, Any]]:
    with _span("mcp.get_inventory_valuation"):
        odoo_repo, _ = server._get_tenant_service()
        from services.inventory import InventoryService

        service = InventoryService(odoo_repo)
        return service.get_inventory_valuation(product_id)
