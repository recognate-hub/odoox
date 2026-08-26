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
    name_query: str | None = None, 
    stage_id: int | None = None, 
    user_id: int | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    limit: int = 100, 
    summarize: bool = False
) -> list[dict[str, Any]] | dict[str, Any]:
    """
    Retrieve active CRM leads (opportunities) from Odoo.

    Use this tool when:
    - The user wants to see a list of current sales leads.
    - The user asks to search for a specific lead by name.
    - The user wants to see leads in a specific pipeline stage.
    
    Do NOT use this tool when:
    - You need to see leads that are won or lost (this only fetches active leads).

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
            name_query=name_query, stage_id=stage_id, user_id=user_id, date_from=date_from, date_to=date_to, limit=limit
        )
        if span:
            span.set_attribute("returned_leads", len(leads))
            
        data = [lead.model_dump() for lead in leads]
        if summarize:
            return {
                "metadata": {
                    "total_returned": len(data),
                    "filters": {"name_query": name_query, "stage_id": stage_id},
                },
                "data": data,
                "summary": f"Found {len(data)} active leads.",
            }
        return data


@mcp.tool()
@secure_tool()
@validate_write_input(LogActivityInput)
def log_crm_note(res_model: str, res_id: int, summary: str) -> dict[str, Any]:
    """
    Log a note or activity on an Odoo record.

    Use this tool when:
    - The user asks to log a call, meeting, note, or update on a lead or contact.
    
    Do NOT use this tool when:
    - You are trying to change a field value like expected revenue (use generic update for that).

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

    Use this tool when:
    - The user wants all available details about a single specific lead.
    - You need to draft an email to a lead and need context on their history.

    Args:
        lead_id (int): The ID of the lead.

    Returns:
        Dict[str, Any]: A comprehensive dictionary representing the lead context.
    """
    logger.info("MCP Tool Called: get_lead_context", lead_id=lead_id)
    _, crm_service = server._get_tenant_service()
    return crm_service.get_lead_context(lead_id)


@mcp.tool()
@secure_tool()
def get_lead_funnel_metrics() -> list[dict[str, Any]]:
    """
    Fetch aggregated metrics for the CRM sales funnel.

    Use this tool when:
    - The user asks for a pipeline overview or health check.
    - The user wants to see conversion rates or bottlenecks.
    - The user asks for expected revenue grouped by stage.
    
    Do NOT use this tool when:
    - You need individual lead records (use get_leads instead).

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


@mcp.tool()
@secure_tool()
def get_crm_team_performance(limit: int = 50) -> list[dict[str, Any]]:
    """
    Retrieve performance metrics for CRM sales teams.
    
    Use this tool when:
    - The user asks about sales team performance or team targets.
    """
    logger.info("MCP Tool Called: get_crm_team_performance")
    odoo_repo, _ = server._get_tenant_service()
    try:
        fields = ["name", "user_id", "invoiced_target", "member_ids"]
        return odoo_repo.search_read_records("crm.team", [], fields, limit=limit)
    except Exception as e:
        logger.error("get_crm_team_performance error", error=str(e))
        return [{"status": "error", "message": str(e)}]


@mcp.tool()
@secure_tool()
def analyze_win_loss_ratio() -> dict[str, Any]:
    """
    Analyze the win/loss ratio of opportunities.
    
    Use this tool when:
    - The user asks for win rates, lost opportunities, or success rates.
    """
    logger.info("MCP Tool Called: analyze_win_loss_ratio")
    odoo_repo, _ = server._get_tenant_service()
    try:
        won_leads = odoo_repo.search_read_records("crm.lead", [["probability", "=", 100]], ["id"], limit=1000)
        lost_leads = odoo_repo.search_read_records("crm.lead", [["active", "=", False], ["probability", "=", 0]], ["id"], limit=1000)
        
        won_count = len(won_leads)
        lost_count = len(lost_leads)
        total = won_count + lost_count
        win_rate = (won_count / total * 100) if total > 0 else 0
        
        return {
            "status": "success",
            "won_count": won_count,
            "lost_count": lost_count,
            "win_rate_percentage": round(win_rate, 2)
        }
    except Exception as e:
        logger.error("analyze_win_loss_ratio error", error=str(e))
        return {"status": "error", "message": str(e)}


@mcp.tool()
@secure_tool()
def update_lead_stage(lead_id: int, stage_id: int) -> dict[str, Any]:
    """
    Move a lead to a different pipeline stage.
    
    Use this tool when:
    - The user explicitly asks to move, progress, or update a lead's stage.
    """
    logger.info("MCP Tool Called: update_lead_stage", lead_id=lead_id, stage_id=stage_id)
    odoo_repo, _ = server._get_tenant_service()
    
    # Validation step
    leads = odoo_repo.search_read_records("crm.lead", [["id", "=", lead_id]], ["name"], limit=1)
    if not leads:
        return {"status": "error", "message": f"Lead with ID {lead_id} does not exist."}
        
    stages = odoo_repo.search_read_records("crm.stage", [["id", "=", stage_id]], ["name"], limit=1)
    if not stages:
        return {"status": "error", "message": f"Stage with ID {stage_id} does not exist."}
        
    try:
        odoo_repo.update_record("crm.lead", lead_id, {"stage_id": stage_id})
        return {"status": "success", "message": f"Lead '{leads[0]['name']}' moved to stage '{stages[0]['name']}'."}
    except Exception as e:
        logger.error("update_lead_stage error", error=str(e))
        return {"status": "error", "message": str(e)}
