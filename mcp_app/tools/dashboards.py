from typing import Any

from core.logger import get_logger
from mcp_app import server
from mcp_app.schemas import *
from mcp_app.security import secure_tool
from mcp_app.server import mcp

logger = get_logger(__name__)


@mcp.tool()
@secure_tool()
def get_pipeline_forecast_data() -> list[dict[str, Any]]:
    """
    Fetch active leads and pipeline data for sales forecasting.

    Use this tool to analyze the probability and expected revenue of current deals.

    Returns:
        List[Dict[str, Any]]: A list of leads with full fields.
    """
    logger.info("MCP Tool Called: get_pipeline_forecast_data")
    _, crm_service = server._get_tenant_service()
    return crm_service.get_pipeline_data()


# --- Calendar & Email Tools ---
