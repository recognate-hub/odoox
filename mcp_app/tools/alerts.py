from typing import Any
from mcp_app.server import mcp
from mcp_app.security import secure_tool
from mcp_app.server import _span
from mcp_app.server import get_settings
import mcp_app.server as server

@mcp.tool()
@secure_tool()
def get_recent_alerts(limit: int = 10, unread_only: bool = True) -> list[dict[str, Any]]:
    """
    Fetch recent proactive alerts pushed from Odoo (e.g., machine breakdowns, quality failures).
    Use this to stay aware of background events that require your attention.
    """
    with _span("mcp.get_recent_alerts"):
        # We need the tenant_db to fetch the alerts for the correct tenant
        odoo_repo, _ = server._get_tenant_service()
        tenant_db = odoo_repo.client._get_workspace().odoo_db
        
        from services.alerts import AlertService
        service = AlertService(tenant_db=tenant_db)
        return service.get_recent_alerts(limit=limit, unread_only=unread_only)

@mcp.tool()
@secure_tool()
def acknowledge_alerts(alert_ids: list[str]) -> dict[str, Any]:
    """
    Mark specific alerts as read/acknowledged so they no longer show up in the unread queue.
    """
    with _span("mcp.acknowledge_alerts"):
        odoo_repo, _ = server._get_tenant_service()
        tenant_db = odoo_repo.client._get_workspace().odoo_db
        
        from services.alerts import AlertService
        service = AlertService(tenant_db=tenant_db)
        return service.acknowledge_alerts(alert_ids)
