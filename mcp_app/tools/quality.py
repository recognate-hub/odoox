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
def get_quality_checks(
    product_id: int | None = None, limit: int = 20, offset: int = 0, date_from: str | None = None, date_to: str | None = None
) -> list[dict[str, Any]]:
    """
    List quality checks, optionally filtered by product and date.
    
    Use this tool when:
    - The user asks for a list of quality inspections or checks.
    - The user asks whether a product passed or failed quality control.

    Args:
        product_id (int, optional): Filter by product ID.
        limit (int): Maximum results to return.
        offset (int): Number of records to skip for pagination.
        date_from (str, optional): Filter records created on or after this date (YYYY-MM-DD).
        date_to (str, optional): Filter records created on or before this date (YYYY-MM-DD).

    Returns:
        List[Dict]: Quality check records with status, product, and inspection details.
    """
    with _span("mcp.get_quality_checks"):
        odoo_repo, _ = server._get_tenant_service()
        from services.quality import QualityService

        service = QualityService(odoo_repo)
        return service.get_quality_checks(product_id, limit, offset, date_from, date_to)


@mcp.tool()
@secure_tool()
def get_quality_alerts(
    product_id: int | None = None, limit: int = 50, offset: int = 0, date_from: str | None = None, date_to: str | None = None
) -> list[dict[str, Any]]:
    """
    List quality alerts, optionally filtered by product and date.

    Use this tool when:
    - The user wants to monitor open quality issues and their current stages.
    - The user asks about defects, problems, or alerts raised for a product.

    Args:
        product_id (int, optional): Filter by product ID.
        limit (int): Maximum results to return.
        offset (int): Number of records to skip for pagination.
        date_from (str, optional): Filter records created on or after this date (YYYY-MM-DD).
        date_to (str, optional): Filter records created on or before this date (YYYY-MM-DD).

    Returns:
        List[Dict]: Quality alerts with name, product, team, stage, priority, and description.
    """
    with _span("mcp.get_quality_alerts"):
        logger.info("MCP Tool Called: get_quality_alerts", product_id=product_id)
        odoo_repo, _ = server._get_tenant_service()
        from services.quality import QualityService

        service = QualityService(odoo_repo)
        return service.get_quality_alerts(product_id, limit, offset, date_from, date_to)


@mcp.tool()
@secure_tool()
def get_quality_points(limit: int = 50) -> list[dict[str, Any]]:
    """
    List quality control points (inspection rules).

    Use this to understand what quality checks are configured for products and operations.

    Args:
        limit (int): Maximum results to return.

    Returns:
        List[Dict]: Quality points with name, products, operations, test type, and team.
    """
    with _span("mcp.get_quality_points"):
        logger.info("MCP Tool Called: get_quality_points")
        odoo_repo, _ = server._get_tenant_service()
        from services.quality import QualityService

        service = QualityService(odoo_repo)
        return service.get_quality_points(limit)




@mcp.tool()
@secure_tool()
def get_quality_metrics() -> dict[str, Any]:
    """
    Fetches aggregate quality metrics including the top products generating Quality Alerts
    and a summary of Quality Check states (pass vs fail).
    """
    with _span("mcp.get_quality_metrics"):
        odoo_repo, _ = server._get_tenant_service()
        from services.operations import OperationsService
        service = OperationsService(odoo_repo)
        return service.get_quality_metrics()


@mcp.tool()
@secure_tool()
def get_product_stage_metrics(product_id: int) -> dict[str, Any]:
    """
    Fetches specific measurements (e.g., diameter, radius, height) recorded during various stages of production.
    Groups the quality check metrics by their manufacturing stage (work order) for a given product.

    Args:
        product_id (int): The ID of the product.

    Returns:
        Dict: A structured dictionary mapping each production stage to its recorded metrics.
    """
    with _span("mcp.get_product_stage_metrics"):
        logger.info("MCP Tool Called: get_product_stage_metrics", product_id=product_id)
        odoo_repo, _ = server._get_tenant_service()
        from services.quality import QualityService

        service = QualityService(odoo_repo)
        return service.get_product_stage_metrics(product_id)


@mcp.tool()
@secure_tool()
def analyze_quality_trends(product_id: int, metric_label: str) -> dict[str, Any]:
    """
    Perform Statistical Process Control (SPC) analysis on a specific product metric (e.g., 'Diameter')
    to detect drift and calculate standard deviation and mean over time.
    
    Returns a JSON object that includes `spc_chart_base64`. When replying to the user, you MUST 
    render this chart directly in your response using markdown syntax:
    ![SPC Chart](data:image/png;base64,<spc_chart_base64_string>)
    """
    with _span("mcp.analyze_quality_trends"):
        odoo_repo, _ = server._get_tenant_service()
        from services.quality import QualityService
        service = QualityService(odoo_repo)
        return service.analyze_quality_trends(product_id, metric_label)


@mcp.tool()
@secure_tool()
def analyze_defect_root_causes() -> dict[str, Any]:
    """
    Aggregate all failed quality checks to identify the root cause bottlenecks
    (e.g., specific workcenters or stages generating the most defects).
    """
    with _span("mcp.analyze_defect_root_causes"):
        odoo_repo, _ = server._get_tenant_service()
        from services.quality import QualityService
        service = QualityService(odoo_repo)
        return service.analyze_defect_root_causes()


@mcp.tool()
@secure_tool()
@validate_write_input(LogQualityResultInput)
def log_quality_result(check_id: int, measure: float | None = None, quality_state: str | None = None) -> dict[str, Any]:
    """
    Record a quality check result (e.g., a measurement or a pass/fail state).
    """
    with _span("mcp.log_quality_result"):
        odoo_repo, _ = server._get_tenant_service()
        from services.quality import QualityService
        service = QualityService(odoo_repo)
        return service.log_quality_result(check_id, measure, quality_state)


@mcp.tool()
@secure_tool()
@validate_write_input(RaiseQualityAlertInput)
def raise_quality_alert(product_id: int, name: str, team_id: int | None = None, priority: str = "0") -> dict[str, Any]:
    """
    Trigger a Quality Alert when an issue is detected (e.g., drifting measurements).
    """
    with _span("mcp.raise_quality_alert"):
        odoo_repo, _ = server._get_tenant_service()
        from services.quality import QualityService
        service = QualityService(odoo_repo)
        return service.create_quality_alert(name, product_id, team_id, priority)

