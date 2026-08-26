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
def get_equipment_status(
    equipment_id: int | None = None, limit: int = 50
) -> list[dict[str, Any]]:
    """Check the status of manufacturing equipment and machines."""
    with _span("mcp.get_equipment_status"):
        odoo_repo, _ = server._get_tenant_service()
        from services.maintenance import MaintenanceService

        service = MaintenanceService(odoo_repo)
        return service.get_equipment_status(equipment_id, limit)


@mcp.tool()
@secure_tool()
def get_maintenance_requests(
    equipment_id: int | None = None, limit: int = 50, summarize: bool = False
) -> list[dict[str, Any]] | dict[str, Any]:
    """
    Retrieve maintenance requests (CMMS) for equipment.

    Use this tool when:
    - The user asks about broken machines, repair requests, or maintenance schedules.
    """
    logger.info("MCP Tool Called: get_maintenance_requests", equipment_id=equipment_id)
    odoo_repo, _ = server._get_tenant_service()
    try:
        domain = []
        if equipment_id:
            domain.append(["equipment_id", "=", equipment_id])
            
        fields = ["name", "equipment_id", "maintenance_type", "stage_id", "priority", "schedule_date", "user_id"]
        requests = odoo_repo.search_read_records("maintenance.request", domain, fields, limit=limit)
        
        if summarize:
            return {
                "metadata": {"total_returned": len(requests), "equipment_id": equipment_id},
                "data": requests,
                "summary": f"Found {len(requests)} maintenance requests."
            }
        return requests
    except Exception as e:
        return [{"status": "error", "message": "Module missing or error: maintenance.request. " + str(e), "suggestion": "The Maintenance module (maintenance) must be installed.", "module_required": "maintenance"}]
