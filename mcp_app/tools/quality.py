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
    product_id: int | None = None, limit: int = 20
) -> list[dict[str, Any]]:
    """
    List quality checks, optionally filtered by product.

    Args:
        product_id (int, optional): Filter by product ID.
        limit (int): Maximum results to return.

    Returns:
        List[Dict]: Quality check records with status, product, and inspection details.
    """
    with _span("mcp.get_quality_checks"):
        odoo_repo, _ = server._get_tenant_service()
        from services.quality import QualityService

        service = QualityService(odoo_repo)
        return service.get_quality_checks(product_id, limit)


@mcp.tool()
@secure_tool()
def get_quality_alerts(
    product_id: int | None = None, limit: int = 50
) -> list[dict[str, Any]]:
    """
    List quality alerts, optionally filtered by product.

    Use this to monitor open quality issues and their current stages.

    Args:
        product_id (int, optional): Filter by product ID.
        limit (int): Maximum results to return.

    Returns:
        List[Dict]: Quality alerts with name, product, team, stage, priority, and description.
    """
    with _span("mcp.get_quality_alerts"):
        logger.info("MCP Tool Called: get_quality_alerts", product_id=product_id)
        odoo_repo, _ = server._get_tenant_service()
        from services.quality import QualityService

        service = QualityService(odoo_repo)
        return service.get_quality_alerts(product_id, limit)


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
