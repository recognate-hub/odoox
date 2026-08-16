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
@validate_write_input(CreateManufacturingOrderInput)
def create_manufacturing_order(product_id: int, product_qty: float) -> dict[str, Any]:
    """
    Create a new manufacturing order (MO) to produce a product.
    
    Args:
        product_id (int): The ID of the product to manufacture.
        product_qty (float): The quantity to manufacture.
    """
    with _span("mcp.create_manufacturing_order"):
        odoo_repo, _ = server._get_tenant_service()
        from services.production import ProductionService
        service = ProductionService(odoo_repo)
        return service.create_manufacturing_order(product_id, product_qty)

@mcp.tool()
@secure_tool()
def get_manufacturing_orders(limit: int = 20) -> list[dict[str, Any]]:
    """
    List manufacturing orders.
    
    Args:
        limit (int): Maximum results to return.
        
    Returns:
        List[Dict]: Manufacturing orders with product, quantity, state, and dates.
    """
    with _span("mcp.get_manufacturing_orders"):
        odoo_repo, _ = server._get_tenant_service()
        from services.production import ProductionService
        service = ProductionService(odoo_repo)
        return service.get_manufacturing_orders(limit)


@mcp.tool()
@secure_tool()
@validate_write_input(UpdateManufacturingOrderInput)
def update_manufacturing_order(mo_id: int, data: dict[str, Any]) -> dict[str, Any]:
    """
    Update a manufacturing order (e.g., change quantity or scheduled date).
    
    Args:
        mo_id (int): The ID of the manufacturing order.
        data (Dict): Fields to update.
        
    Returns:
        Dict: Status of the update.
    """
    with _span("mcp.update_manufacturing_order"):
        logger.info("MCP Tool Called: update_manufacturing_order", mo_id=mo_id)
        odoo_repo, _ = server._get_tenant_service()
        from services.production import ProductionService
        service = ProductionService(odoo_repo)
        return service.update_manufacturing_order(mo_id, data)


@mcp.tool()
@secure_tool()
@validate_write_input(ConfirmManufacturingOrderInput)
def confirm_manufacturing_order(mo_id: int) -> dict[str, Any]:
    """
    Confirm a draft manufacturing order, triggering the production workflow.
    
    Args:
        mo_id (int): The ID of the manufacturing order to confirm.
        
    Returns:
        Dict: Status of the confirmation.
    """
    with _span("mcp.confirm_manufacturing_order"):
        logger.info("MCP Tool Called: confirm_manufacturing_order", mo_id=mo_id)
        odoo_repo, _ = server._get_tenant_service()
        from services.production import ProductionService
        service = ProductionService(odoo_repo)
        return service.confirm_manufacturing_order(mo_id)


@mcp.tool()
@secure_tool()
def get_bill_of_materials(product_id: int | None = None, limit: int = 50) -> list[dict[str, Any]]:
    """
    List Bills of Materials (BOM) — the recipes/formulas for manufacturing products.
    
    Args:
        product_id (int, optional): Filter by product template ID.
        limit (int): Maximum results to return.
        
    Returns:
        List[Dict]: BOMs with product, quantity, type, and component line IDs.
    """
    with _span("mcp.get_bill_of_materials"):
        logger.info("MCP Tool Called: get_bill_of_materials", product_id=product_id)
        odoo_repo, _ = server._get_tenant_service()
        from services.production import ProductionService
        service = ProductionService(odoo_repo)
        return service.get_bill_of_materials(product_id, limit)


@mcp.tool()
@secure_tool()
def get_work_orders(mo_id: int | None = None, limit: int = 50) -> list[dict[str, Any]]:
    """
    List work orders (individual production steps) within manufacturing orders.
    
    Args:
        mo_id (int, optional): Filter by manufacturing order ID.
        limit (int): Maximum results to return.
        
    Returns:
        List[Dict]: Work orders with name, workcenter, state, duration, and dates.
    """
    with _span("mcp.get_work_orders"):
        logger.info("MCP Tool Called: get_work_orders", mo_id=mo_id)
        odoo_repo, _ = server._get_tenant_service()
        from services.production import ProductionService
        service = ProductionService(odoo_repo)
        return service.get_work_orders(mo_id, limit)


@mcp.tool()
@secure_tool()
def get_workcenters(limit: int = 50) -> list[dict[str, Any]]:
    """
    List workcenters (machines/stations used in production).
    
    Use this for pre-production planning to check capacity and availability.
    
    Args:
        limit (int): Maximum results to return.
        
    Returns:
        List[Dict]: Workcenters with name, code, capacity, efficiency, and working state.
    """
    with _span("mcp.get_workcenters"):
        logger.info("MCP Tool Called: get_workcenters")
        odoo_repo, _ = server._get_tenant_service()
        from services.production import ProductionService
        service = ProductionService(odoo_repo)
        return service.get_workcenters(limit)


@mcp.tool()
@secure_tool()
def get_routings(limit: int = 50) -> list[dict[str, Any]]:
    """
    List production routings/operations (steps in a BOM's manufacturing process).
    
    Use this for pre-production planning to understand the sequence of work.
    
    Args:
        limit (int): Maximum results to return.
        
    Returns:
        List[Dict]: Routing operations with name, workcenter, BOM, cycle time, and sequence.
    """
    with _span("mcp.get_routings"):
        logger.info("MCP Tool Called: get_routings")
        odoo_repo, _ = server._get_tenant_service()
        from services.production import ProductionService
        service = ProductionService(odoo_repo)
        return service.get_routings(limit)
