from typing import Any

from core.logger import get_logger
from mcp_app import server
from mcp_app.security import secure_tool
from mcp_app.server import mcp
from services.analyzer import AnalyzerService

logger = get_logger(__name__)


@mcp.tool()
@secure_tool()
def analyze_system_structure() -> dict[str, Any]:
    """
    Analyzes the Odoo system structure.
    Returns the count of active users, active companies, and a list of installed apps.
    
    Use this tool when:
    - You need to understand what modules are available in the tenant's Odoo instance.
    - The user asks how many users or apps are in the system.
    """
    logger.info("MCP Tool Called: analyze_system_structure")
    odoo_repo, _ = server._get_tenant_service()
    service = AnalyzerService(odoo_repo)
    return service.analyze_system_structure()


@mcp.tool()
@secure_tool()
def analyze_pipeline_metrics() -> dict[str, Any]:
    """
    Analyzes the CRM and Sales pipelines at a high level.
    Returns aggregated expected revenue grouped by CRM Stage and aggregated sales order totals by state.
    
    Use this tool when:
    - You need to get a bird's-eye view of sales performance without fetching thousands of records.
    - The user asks for total sales by stage.
    """
    logger.info("MCP Tool Called: analyze_pipeline_metrics")
    odoo_repo, _ = server._get_tenant_service()
    service = AnalyzerService(odoo_repo)
    return service.analyze_pipeline_metrics()


@mcp.tool()
@secure_tool()
def analyze_production_metrics() -> dict[str, Any]:
    """
    Analyzes manufacturing stages and WIP quantities.
    Returns aggregated active manufacturing orders and WIP quantities sitting in each workcenter/stage.
    
    Use this tool when:
    - The user asks to identify production bottlenecks and total factory load.
    - You need a high-level summary of what's being built.
    """
    logger.info("MCP Tool Called: analyze_production_metrics")
    odoo_repo, _ = server._get_tenant_service()
    service = AnalyzerService(odoo_repo)
    return service.analyze_production_metrics()


@mcp.tool()
@secure_tool()
def analyze_inventory_financials() -> dict[str, Any]:
    """
    Analyzes high-level stock valuation and invoicing metrics.
    Returns the total system stock valuation and aggregated invoiced amounts grouped by invoice state.
    
    Use this tool when:
    - The user asks for a financial summary of inventory or invoicing.
    """
    logger.info("MCP Tool Called: analyze_inventory_financials")
    odoo_repo, _ = server._get_tenant_service()
    service = AnalyzerService(odoo_repo)
    return service.analyze_inventory_financials()
