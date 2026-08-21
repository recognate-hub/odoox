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
