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
