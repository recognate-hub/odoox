
from fastmcp import FastMCP

from config.settings import get_settings
from core.logger import get_logger
from odoo.xmlrpc import XmlRpcOdooConnector
from repositories.odoo import OdooRepository
from services.crm import CRMService

logger = get_logger(__name__)

try:
    from opentelemetry import trace
    tracer = trace.get_tracer(__name__)
except Exception:  # noqa: BLE001
    tracer = None  # type: ignore

from contextlib import nullcontext


def _span(name: str):
    """Return a tracing span context manager, or a no-op if OTel is unavailable."""
    if tracer:
        return tracer.start_as_current_span(name)
    return nullcontext()


def _get_tenant_service() -> tuple[OdooRepository, CRMService]:
    """
    Lazily create an OdooConnector using the current tenant's credentials.
    This is called per-request so each tenant gets their own connection.
    """
    # The XmlRpcOdooConnector automatically reads the credentials from the
    # current_token and get_workspace_credentials context when making calls.
    settings = get_settings()
    connector = XmlRpcOdooConnector(settings)
    repo = OdooRepository(connector)
    service = CRMService(repo)
    return repo, service


# Initialize FastMCP Server
mcp = FastMCP("ODOOX")

# Register all tools — importing each module triggers the @mcp.tool() decorators
import mcp_app.tools.crm  # noqa: F401, E402
import mcp_app.tools.contacts  # noqa: F401, E402
import mcp_app.tools.sales  # noqa: F401, E402
import mcp_app.tools.inventory  # noqa: F401, E402
import mcp_app.tools.invoicing  # noqa: F401, E402
import mcp_app.tools.calendar  # noqa: F401, E402
import mcp_app.tools.discuss  # noqa: F401, E402
import mcp_app.tools.dashboards  # noqa: F401, E402
import mcp_app.tools.generic  # noqa: F401, E402
import mcp_app.tools.reports  # noqa: F401, E402
import mcp_app.tools.production  # noqa: F401, E402
import mcp_app.tools.purchase  # noqa: F401, E402
import mcp_app.tools.quality  # noqa: F401, E402

