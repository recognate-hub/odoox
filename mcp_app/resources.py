"""
MCP Resources Registry for OdooX.
Provides readable URI-based context data streams for Claude, Cursor, and LLMs.
"""

import json
from typing import Any
from core.logger import get_logger
from mcp_app import server
from mcp_app.security import secure_tool
from mcp_app.server import mcp

logger = get_logger(__name__)


@mcp.resource("odoo://system/status")
def get_system_status_resource() -> str:
    """
    Returns real-time status of the connected Odoo instance, including active users, companies, and installed apps.
    """
    logger.info("MCP Resource Read: odoo://system/status")
    odoo_repo, _ = server._get_tenant_service()
    from services.analyzer import AnalyzerService
    service = AnalyzerService(odoo_repo)
    data = service.analyze_system_structure()
    return json.dumps(data, indent=2)


@mcp.resource("odoo://schema/models")
def get_schema_models_resource() -> str:
    """
    Returns the schema registry of active Odoo business models and relational structures.
    """
    logger.info("MCP Resource Read: odoo://schema/models")
    odoo_repo, _ = server._get_tenant_service()
    try:
        models = odoo_repo.search_read_records(
            "ir.model",
            domain=[["transient", "=", False]],
            fields=["model", "name", "state"],
            limit=100
        )
        return json.dumps({"models": models, "count": len(models)}, indent=2)
    except Exception as e:
        logger.error("Failed to read schema models resource", error=str(e))
        return json.dumps({"error": str(e)})


@mcp.resource("odoo://kpis/realtime")
def get_realtime_kpis_resource() -> str:
    """
    Returns a high-level summary of CRM revenue, active manufacturing orders, and stock valuation.
    """
    logger.info("MCP Resource Read: odoo://kpis/realtime")
    odoo_repo, _ = server._get_tenant_service()
    from services.analyzer import AnalyzerService
    service = AnalyzerService(odoo_repo)
    
    pipeline = service.analyze_pipeline_metrics()
    production = service.analyze_production_metrics()
    financials = service.analyze_inventory_financials()
    
    kpis = {
        "sales_and_crm": pipeline,
        "manufacturing_wip": production,
        "inventory_and_invoicing": financials,
    }
    return json.dumps(kpis, indent=2)
