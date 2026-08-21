from typing import Any

from core.logger import get_logger
from mcp_app import server
from mcp_app.security import secure_tool
from mcp_app.server import _span, mcp
from services.planning import PlanningService

logger = get_logger(__name__)


@mcp.tool()
@secure_tool()
def get_production_planning_report(months_history: int = 4) -> list[dict[str, Any]]:
    """
    Fetch and calculate the Production Planning Report dynamically.

    This tool replaces the manual Excel exports for Sale Variant Pivot, Stage Wise Stock,
    and Customer Pending Quantity. It aggregates everything into a single dataset.

    Args:
        months_history (int): The number of months to look back for sales history to calculate MOQ. Defaults to 4.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries containing product name (p), Finished Stock (s),
        Average MOQ (m), Customer Pending Order (o), Planning Qty (pl), Total WIP (wip),
        Stage-wise WIP (st), and Customer Pending Orders (cu).
    """
    with _span("mcp.get_production_planning_report"):
        odoo_repo, _ = server._get_tenant_service()
        service = PlanningService(odoo_repo)
        return service.get_production_planning_data(months=months_history)


@mcp.tool()
@secure_tool()
def create_planned_manufacturing_orders(orders: list[dict[str, Any]]) -> dict[str, Any]:
    """
    Push calculated production planning data back to Odoo by creating Manufacturing Orders in bulk.

    Args:
        orders: A list of dictionaries containing the product_id and qty to produce.
                Example: [{"product_id": 123, "qty": 500.0}]

    Returns:
        Dict: A success message containing the IDs of the created manufacturing orders.
    """
    with _span("mcp.create_planned_manufacturing_orders"):
        odoo_repo, _ = server._get_tenant_service()
        service = PlanningService(odoo_repo)

        try:
            mo_ids = service.create_planned_manufacturing_orders(orders)
            return {
                "status": "success",
                "message": f"Successfully created {len(mo_ids)} Manufacturing Orders.",
                "mo_ids": mo_ids,
            }
        except Exception as e:
            logger.error("Failed to create manufacturing orders", error=str(e))
            return {"status": "error", "message": str(e)}
