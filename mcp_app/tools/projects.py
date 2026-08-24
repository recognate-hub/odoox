from typing import Any
from core.logger import get_logger
from mcp_app import server
from mcp_app.security import secure_tool
from mcp_app.server import _span, mcp

logger = get_logger(__name__)


@mcp.tool()
@secure_tool()
def get_active_projects(limit: int = 50) -> list[dict[str, Any]]:
    """
    Retrieve active projects from Odoo.

    Use this tool to fetch ongoing projects, their managers, and overall status.

    Args:
        limit (int): Maximum number of projects to return. Default is 50.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries representing active projects.
    """
    with _span("mcp.get_active_projects") as span:
        logger.info("MCP Tool Called: get_active_projects", limit=limit)
        odoo_repo, _ = server._get_tenant_service()
        
        # In Odoo, active projects usually don't have a specific state, but they might not be archived (active=True).
        domain = [["active", "=", True]]
        fields = ["name", "partner_id", "user_id", "date_start", "date", "task_count"]
        
        try:
            return odoo_repo.search_read_records("project.project", domain, fields, limit=limit)
        except Exception as e:
            logger.error("get_active_projects error", error=str(e))
            return [{"status": "error", "message": str(e)}]


@mcp.tool()
@secure_tool()
def analyze_task_bottlenecks(project_id: int | None = None) -> list[dict[str, Any]]:
    """
    Identify task bottlenecks by analyzing tasks across project stages.

    Use this tool to find out which stages have the highest number of tasks or delays.

    Args:
        project_id (Optional[int]): Filter by a specific project ID.

    Returns:
        List[Dict[str, Any]]: Aggregated metrics of tasks grouped by stage.
    """
    logger.info("MCP Tool Called: analyze_task_bottlenecks", project_id=project_id)
    odoo_repo, _ = server._get_tenant_service()
    try:
        domain = [["is_closed", "=", False]]
        if project_id:
            domain.append(["project_id", "=", project_id])
            
        fields = ["stage_id", "project_id"]
        groupby = ["stage_id"]
        lines = odoo_repo.search_read_records("project.task", domain, fields, limit=5000)
        
        summary = {}
        for line in lines:
            stage = line.get("stage_id")
            stage_name = stage[1] if isinstance(stage, (list, tuple)) and len(stage) > 1 else str(stage)
            
            if stage_name not in summary:
                summary[stage_name] = {
                    "stage": stage_name,
                    "task_count": 0
                }
            summary[stage_name]["task_count"] += 1
            
        return list(summary.values())
    except Exception as e:
        logger.error("analyze_task_bottlenecks error", error=str(e))
        return [{"status": "error", "message": str(e)}]


@mcp.tool()
@secure_tool()
def get_project_burn_rate(project_id: int) -> dict[str, Any]:
    """
    Calculate the project burn rate based on logged timesheets and allocated hours.

    Use this tool to determine if a project is running over budget on hours.

    Args:
        project_id (int): The ID of the project to analyze.

    Returns:
        Dict[str, Any]: A dictionary containing total allocated hours, total logged hours, and the burn rate percentage.
    """
    logger.info("MCP Tool Called: get_project_burn_rate", project_id=project_id)
    odoo_repo, _ = server._get_tenant_service()
    try:
        # Fetch the project to see if it has allocated_hours (field exists in some versions/configs)
        projects = odoo_repo.search_read_records(
            "project.project", 
            [["id", "=", project_id]], 
            ["name", "allocated_hours"], 
            limit=1
        )
        if not projects:
            return {"status": "error", "message": "Project not found."}
            
        project = projects[0]
        allocated_hours = project.get("allocated_hours") or 0.0
        
        # Fetch total logged hours from tasks
        tasks = odoo_repo.search_read_records(
            "project.task",
            [["project_id", "=", project_id]],
            ["effective_hours"]
        )
        total_logged = sum(task.get("effective_hours", 0.0) for task in tasks)
        
        burn_rate = (total_logged / allocated_hours * 100) if allocated_hours > 0 else 0.0
        
        return {
            "status": "success",
            "project_name": project.get("name"),
            "allocated_hours": allocated_hours,
            "total_logged_hours": total_logged,
            "burn_rate_percentage": round(burn_rate, 2),
            "is_over_budget": total_logged > allocated_hours and allocated_hours > 0
        }
    except Exception as e:
        logger.error("get_project_burn_rate error", error=str(e))
        return {"status": "error", "message": str(e)}
