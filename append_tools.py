import os

purchase_tool = """
from services.operations import OperationsService

@mcp.tool()
@secure_tool()
def get_purchase_plan() -> list[dict[str, Any]]:
    \"\"\"
    Analyzes active Manufacturing Orders and calculates raw material shortages based on current stock.
    Returns a list of raw materials critically short.
    \"\"\"
    with _span("mcp.get_purchase_plan"):
        odoo_repo, _ = server._get_tenant_service()
        service = OperationsService(odoo_repo)
        return service.get_purchase_plan()
"""

sales_tool = """
from services.operations import OperationsService

@mcp.tool()
@secure_tool()
def get_ready_to_ship_orders() -> list[dict[str, Any]]:
    \"\"\"
    Analyzes all pending sales orders and checks them against current Finished Goods stock.
    Returns a list of Sales Orders that can be 100% fulfilled immediately.
    \"\"\"
    with _span("mcp.get_ready_to_ship_orders"):
        odoo_repo, _ = server._get_tenant_service()
        service = OperationsService(odoo_repo)
        return service.get_ready_to_ship_orders()
"""

production_tool = """
from services.operations import OperationsService

@mcp.tool()
@secure_tool()
def analyze_workcenter_bottlenecks() -> list[dict[str, Any]]:
    \"\"\"
    Analyzes all active Work Orders to identify bottlenecks by grouping the backlog at each Workcenter.
    Returns a ranked list of Workcenters sorted by backlog.
    \"\"\"
    with _span("mcp.analyze_workcenter_bottlenecks"):
        odoo_repo, _ = server._get_tenant_service()
        service = OperationsService(odoo_repo)
        return service.analyze_workcenter_bottlenecks()
"""

quality_tool = """
from services.operations import OperationsService

@mcp.tool()
@secure_tool()
def get_quality_metrics() -> dict[str, Any]:
    \"\"\"
    Fetches aggregate quality metrics including the top products generating Quality Alerts 
    and a summary of Quality Check states (pass vs fail).
    \"\"\"
    with _span("mcp.get_quality_metrics"):
        odoo_repo, _ = server._get_tenant_service()
        service = OperationsService(odoo_repo)
        return service.get_quality_metrics()
"""

mapping = {
    "mcp_app/tools/purchase.py": purchase_tool,
    "mcp_app/tools/sales.py": sales_tool,
    "mcp_app/tools/production.py": production_tool,
    "mcp_app/tools/quality.py": quality_tool,
}

for filepath, content_to_append in mapping.items():
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    if "from services.operations import OperationsService" not in content:
        with open(filepath, "a", encoding="utf-8") as f:
            f.write(content_to_append)
            
print("Tools appended successfully.")
