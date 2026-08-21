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
@validate_write_input(ReadGroupInput)
def generate_report(
    model: str, domain: list[Any], fields: list[str], groupby: list[str]
) -> list[dict[str, Any]]:
    with _span("mcp.generate_report"):
        odoo_repo, _ = server._get_tenant_service()
        from services.reports import ReportsService

        service = ReportsService(odoo_repo)
        return service.generate_report(model, domain, fields, groupby)
