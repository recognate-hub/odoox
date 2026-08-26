from fastmcp import FastMCP
import functools

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


_tenant_services = {}

def _get_tenant_service() -> tuple[OdooRepository, CRMService]:
    """
    Lazily create or retrieve an OdooConnector using the current tenant's credentials.
    """
    from core.context import get_current_token, current_workspace_id
    token = get_current_token()
    workspace_id = current_workspace_id.get()
    cache_key = f"{token}:{workspace_id}"
    
    if cache_key not in _tenant_services:
        settings = get_settings()
        connector = XmlRpcOdooConnector(settings)
        repo = OdooRepository(connector)
        service = CRMService(repo)
        _tenant_services[cache_key] = (repo, service)
        
    return _tenant_services[cache_key]


# Initialize FastMCP Server
mcp = FastMCP("ODOOX")

# Patch mcp.tool to inject a global timeout of 600s (10 minutes) for all tools
original_tool = mcp.tool

@functools.wraps(original_tool)
def patched_tool(*args, **kwargs):
    kwargs.setdefault("timeout", 600)
    return original_tool(*args, **kwargs)

mcp.tool = patched_tool

# Register all tools — importing each module triggers the @mcp.tool() decorators
import mcp_app.tools.accounting
import mcp_app.tools.alerts
import mcp_app.tools.analyzer
import mcp_app.tools.calendar
import mcp_app.tools.contacts
import mcp_app.tools.crm
import mcp_app.tools.dashboards
import mcp_app.tools.discuss
import mcp_app.tools.generic
import mcp_app.tools.hr
import mcp_app.tools.inventory
import mcp_app.tools.invoicing
import mcp_app.tools.maintenance
import mcp_app.tools.planning
import mcp_app.tools.production
import mcp_app.tools.projects
import mcp_app.tools.purchase
import mcp_app.tools.quality
import mcp_app.tools.reports
import mcp_app.tools.finops
import mcp_app.tools.sales  # noqa: F401
import mcp_app.tools.schema
import mcp_app.tools.intelligence

# Register Prompts and Resources
import mcp_app.prompts
import mcp_app.resources
