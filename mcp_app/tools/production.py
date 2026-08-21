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
def get_bill_of_materials(
    product_id: int | None = None, limit: int = 50
) -> list[dict[str, Any]]:
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
def get_wip_stock_by_stage(product_id: int) -> list[dict[str, Any]]:
    """
    Fetch the stage-wise WIP (Work In Progress) stock for a product.
    This aggregates active work orders grouped by their stage/workcenter.

    Args:
        product_id (int): The ID of the product.

    Returns:
        List[Dict]: Work orders with their current state, stage name, and quantities.
    """
    with _span("mcp.get_wip_stock_by_stage"):
        logger.info("MCP Tool Called: get_wip_stock_by_stage", product_id=product_id)
        odoo_repo, _ = server._get_tenant_service()
        from services.production import ProductionService

        service = ProductionService(odoo_repo)
        return service.get_wip_stock_by_stage(product_id)


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


# ── Advanced Manufacturing / PLM ───────────────────────────────────


@mcp.tool()
@secure_tool()
def get_bom_hierarchy(
    bom_id: int | None = None, limit: int = 200
) -> list[dict[str, Any]]:
    """Get the multi-level Bill of Materials hierarchy."""
    with _span("mcp.get_bom_hierarchy"):
        odoo_repo, _ = server._get_tenant_service()
        from services.production import ProductionService

        service = ProductionService(odoo_repo)
        return service.get_bom_hierarchy(bom_id, limit)


@mcp.tool()
@secure_tool()
@validate_write_input(CreateEcoInput)
def create_eco(product_tmpl_id: int, type_id: int, name: str) -> dict[str, Any]:
    """Create an Engineering Change Order (ECO) for a product."""
    with _span("mcp.create_eco"):
        odoo_repo, _ = server._get_tenant_service()
        from services.production import ProductionService

        service = ProductionService(odoo_repo)
        return service.create_eco(product_tmpl_id, type_id, name)


@mcp.tool()
@secure_tool()
def get_work_center_capacity(limit: int = 50) -> list[dict[str, Any]]:
    """Check the current load and capacity on work centers."""
    with _span("mcp.get_work_center_capacity"):
        odoo_repo, _ = server._get_tenant_service()
        from services.production import ProductionService

        service = ProductionService(odoo_repo)
        return service.get_workcenters(limit)


@mcp.tool()
@secure_tool()
def get_equipment_oee(
    workcenter_id: int | None = None, limit: int = 100
) -> list[dict[str, Any]]:
    """Fetch Overall Equipment Effectiveness (OEE) metrics for work centers."""
    with _span("mcp.get_equipment_oee"):
        odoo_repo, _ = server._get_tenant_service()
        from services.production import ProductionService

        service = ProductionService(odoo_repo)
        return service.get_equipment_oee(workcenter_id, limit)


@mcp.tool()
@secure_tool()
@validate_write_input(RescheduleWorkOrderInput)
def reschedule_work_order(
    workorder_id: int, date_start: str, date_finished: str
) -> dict[str, Any]:
    """Reschedule a work order to a different date to resolve bottlenecks."""
    with _span("mcp.reschedule_work_order"):
        odoo_repo, _ = server._get_tenant_service()
        from services.production import ProductionService

        service = ProductionService(odoo_repo)
        return service.reschedule_work_order(workorder_id, date_start, date_finished)


@mcp.tool()
@secure_tool()
def analyze_component_shortages() -> dict[str, Any]:
    """Analyze manufacturing orders against current inventory to identify missing components."""
    with _span("mcp.analyze_component_shortages"):
        odoo_repo, _ = server._get_tenant_service()
        from services.production import ProductionService

        service = ProductionService(odoo_repo)
        return service.analyze_component_shortages()


@mcp.tool()
@secure_tool()
def get_mps_forecast(limit: int = 50) -> list[dict[str, Any]]:
    """Pull the Master Production Schedule (MPS) forecast."""
    with _span("mcp.get_mps_forecast"):
        odoo_repo, _ = server._get_tenant_service()
        from services.production import ProductionService

        service = ProductionService(odoo_repo)
        return service.get_mps_forecast(limit)


@mcp.tool()
@secure_tool()
def run_mrp_scheduler() -> dict[str, Any]:
    """Trigger Odoo's automated procurement rules to generate Purchase Orders."""
    with _span("mcp.run_mrp_scheduler"):
        odoo_repo, _ = server._get_tenant_service()
        from services.production import ProductionService

        service = ProductionService(odoo_repo)
        return service.run_mrp_scheduler()


@mcp.tool()
@secure_tool()
def trace_lot_number(
    lot_id: int | None = None, limit: int = 100
) -> list[dict[str, Any]]:
    """Trace a specific lot or serial number for quality or recall purposes."""
    with _span("mcp.trace_lot_number"):
        odoo_repo, _ = server._get_tenant_service()
        from services.production import ProductionService

        service = ProductionService(odoo_repo)
        return service.trace_lot_number(lot_id, limit)


@mcp.tool()
@secure_tool()
@validate_write_input(LogWorkOrderTimeInput)
def log_work_order_time(
    workorder_id: int, duration_minutes: float, loss_id: int | None = None
) -> dict[str, Any]:
    """Log labor time or machine downtime for a specific work order."""
    with _span("mcp.log_work_order_time"):
        odoo_repo, _ = server._get_tenant_service()
        from services.production import ProductionService

        service = ProductionService(odoo_repo)
        return service.log_work_order_time(workorder_id, duration_minutes, loss_id)
