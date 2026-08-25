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
def get_leads(
    name_query: str | None = None, stage_id: int | None = None, limit: int = 100
) -> list[dict[str, Any]]:
    """
    Retrieve active CRM leads (opportunities) from Odoo.

    Use this tool to fetch a list of current active sales leads or search for specific leads.

    Args:
        name_query (Optional[str]): Search by lead name (case-insensitive partial match).
        stage_id (Optional[int]): Filter by a specific pipeline stage ID.
        limit (int): The maximum number of leads to return. Default is 100.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries representing leads with fields like name, email_from, phone, partner_id, stage_id, expected_revenue, and description.
    """
    with _span("mcp.get_leads") as span:
        if span:
            span.set_attribute("limit", limit)
        logger.info(
            "MCP Tool Called: get_leads",
            limit=limit,
            query=name_query,
            stage_id=stage_id,
        )
        odoo_repo, _ = server._get_tenant_service()
        leads = odoo_repo.get_active_leads(
            name_query=name_query, stage_id=stage_id, limit=limit
        )
        if span:
            span.set_attribute("returned_leads", len(leads))
        return [lead.model_dump() for lead in leads]


@mcp.tool()
@secure_tool()
@validate_write_input(LogActivityInput)
def log_crm_note(res_model: str, res_id: int, summary: str) -> dict[str, Any]:
    """
    Log a note or activity on an Odoo record.

    Use this tool to add call notes, meeting summaries, or updates to a lead/contact.

    Args:
        res_model (str): The Odoo model (e.g., 'crm.lead', 'res.partner').
        res_id (int): The ID of the record.
        summary (str): The text content of the note.

    Returns:
        Dict[str, Any]: The status of the operation and activity ID.
    """
    logger.info("MCP Tool Called: log_crm_note", model=res_model, id=res_id)
    odoo_repo, _ = server._get_tenant_service()
    activity_id = odoo_repo.log_activity(res_model, res_id, summary, activity_type_id=4)
    return {"status": "success", "activity_id": activity_id}


@mcp.tool()
@secure_tool()
def get_lead_context(lead_id: int) -> dict[str, Any]:
    """
    Fetch raw lead context to draft emails or perform analysis.

    Use this tool to get all details about a specific lead.

    Args:
        lead_id (int): The ID of the lead.

    Returns:
        Dict[str, Any]: A dictionary representing the lead.
    """
    logger.info("MCP Tool Called: get_lead_context", lead_id=lead_id)
    _, crm_service = server._get_tenant_service()
    return crm_service.get_lead_context(lead_id)


@mcp.tool()
@secure_tool()
def get_lead_funnel_metrics() -> list[dict[str, Any]]:
    """
    Fetch aggregated metrics for the CRM sales funnel.

    Use this tool to analyze lead conversion rates, pipeline health, and identify bottlenecks by grouping active leads by stage.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries containing stage_id, count, and expected_revenue grouped by pipeline stage.
    """
    logger.info("MCP Tool Called: get_lead_funnel_metrics")
    odoo_repo, _ = server._get_tenant_service()
    try:
        domain = [["type", "=", "opportunity"]]
        fields = ["stage_id", "expected_revenue"]
        leads = odoo_repo.search_read_records("crm.lead", domain, fields, limit=5000)
        
        summary = {}
        for lead in leads:
            stage = lead.get("stage_id")
            if not stage:
                continue
            stage_id = stage[0] if isinstance(stage, (list, tuple)) else stage
            stage_name = stage[1] if isinstance(stage, (list, tuple)) and len(stage) > 1 else str(stage)
            
            if stage_id not in summary:
                summary[stage_id] = {
                    "stage_id": stage,
                    "stage_id_count": 0,
                    "expected_revenue": 0.0
                }
            summary[stage_id]["stage_id_count"] += 1
            summary[stage_id]["expected_revenue"] += lead.get("expected_revenue", 0.0)
            
        return list(summary.values())
    except Exception as e:
        logger.error("get_lead_funnel_metrics error", error=str(e))
        return [{"status": "error", "message": str(e)}]
