from typing import Any
from core.logger import get_logger
from mcp_app.security import secure_tool, finops_service, get_current_user_context
from mcp_app.server import mcp

logger = get_logger(__name__)

@mcp.tool()
@secure_tool()
def get_finops_budget_status() -> dict[str, Any]:
    """
    Retrieve the current tenant's FinOps daily API budget status.
    
    Use this tool when:
    - You want to check how many API calls you have left for the day.
    - The user asks about their API usage, limits, or why they are being rate limited.
    """
    logger.info("MCP Tool Called: get_finops_budget_status")
    try:
        user = get_current_user_context()
        return finops_service.get_budget_status(user.user_id)
    except Exception as e:
        logger.error("get_finops_budget_status error", error=str(e))
        return {"status": "error", "message": str(e)}
