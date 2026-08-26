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
            return [{
                "status": "module_not_installed",
                "module_required": "project",
                "message": f"Project module error or not installed: {e}",
                "suggestion": "Install the 'project' module from Odoo Apps to manage and track projects."
            }]


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
        return [{
            "status": "module_not_installed",
            "module_required": "project",
            "message": f"Project module error or not installed: {e}",
            "suggestion": "Install the 'project' module from Odoo Apps to analyze task bottlenecks."
        }]


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
        return {
            "status": "module_not_installed",
            "module_required": "project",
            "message": f"Project module error or not installed: {e}",
            "suggestion": "Install the 'project' and 'hr_timesheet' modules from Odoo Apps to track project burn rates."
        }


@mcp.tool()
@secure_tool()
def get_project_tasks(
    project_id: int | None = None, limit: int = 50, summarize: bool = False
) -> list[dict[str, Any]] | dict[str, Any]:
    """
    Retrieve tasks for a specific project or all open tasks.

    Use this tool when:
    - The user asks for a list of tasks.
    - The user wants to see what needs to be done on a project.
    """
    logger.info("MCP Tool Called: get_project_tasks", project_id=project_id, limit=limit)
    odoo_repo, _ = server._get_tenant_service()
    try:
        domain = [["is_closed", "=", False]]
        if project_id:
            domain.append(["project_id", "=", project_id])
            
        fields = ["name", "project_id", "user_ids", "stage_id", "date_deadline", "priority"]
        tasks = odoo_repo.search_read_records("project.task", domain, fields, limit=limit)
        
        if summarize:
            return {
                "metadata": {"total_returned": len(tasks), "project_id": project_id},
                "data": tasks,
                "summary": f"Found {len(tasks)} open tasks."
            }
        return tasks
    except Exception as e:
        logger.error("get_project_tasks error", error=str(e))
        return [{
            "status": "module_not_installed",
            "module_required": "project",
            "message": f"Project module error or not installed: {e}",
            "suggestion": "Install the 'project' module from Odoo Apps to view project tasks."
        }]


@mcp.tool()
@secure_tool()
@validate_write_input(CreateProjectTaskInput)
def create_project_task(
    name: str, 
    project_id: int, 
    description: str | None = None, 
    user_ids: list[int] | None = None,
    date_deadline: str | None = None
) -> dict[str, Any]:
    """
    Create a new task in a specific project.
    
    Use this tool when:
    - The user explicitly asks to create a task or add something to a project board.
    """
    logger.info("MCP Tool Called: create_project_task", name=name, project_id=project_id)
    odoo_repo, _ = server._get_tenant_service()
    
    # ID Validation Step (as per user request)
    projects = odoo_repo.search_read_records("project.project", [["id", "=", project_id]], ["name"], limit=1)
    if not projects:
        return {"status": "error", "message": f"Project with ID {project_id} does not exist. Please use get_active_projects to find a valid project ID."}
        
    data = {
        "name": name,
        "project_id": project_id,
    }
    if description:
        data["description"] = description
    if user_ids:
        data["user_ids"] = [(6, 0, user_ids)]
    if date_deadline:
        data["date_deadline"] = date_deadline
        
    try:
        task_id = odoo_repo.create_record("project.task", data)
        return {"status": "success", "task_id": task_id, "project": projects[0]["name"]}
    except Exception as e:
        logger.error("create_project_task error", error=str(e))
        return {"status": "error", "message": str(e)}


@mcp.tool()
@secure_tool()
def get_timesheet_entries(project_id: int | None = None, employee_id: int | None = None, limit: int = 100) -> list[dict[str, Any]]:
    """
    Retrieve employee timesheets and logged hours for tasks/projects.
    """
    logger.info("MCP Tool Called: get_timesheet_entries")
    odoo_repo, _ = server._get_tenant_service()
    try:
        domain = []
        if project_id: domain.append(["project_id", "=", project_id])
        if employee_id: domain.append(["employee_id", "=", employee_id])
        return odoo_repo.search_read_records("account.analytic.line", domain, ["name", "date", "employee_id", "project_id", "task_id", "unit_amount"], limit=limit)
    except Exception as e:
        return [{
            "status": "module_not_installed",
            "module_required": "hr_timesheet",
            "message": f"Timesheet module error or not installed: {e}",
            "suggestion": "Install the 'hr_timesheet' module from Odoo Apps to track timesheet entries."
        }]


@mcp.tool()
@secure_tool()
def get_milestones(project_id: int | None = None, limit: int = 50) -> list[dict[str, Any]]:
    """
    Retrieve project milestones.
    """
    logger.info("MCP Tool Called: get_milestones")
    odoo_repo, _ = server._get_tenant_service()
    try:
        domain = [["project_id", "=", project_id]] if project_id else []
        return odoo_repo.search_read_records("project.milestone", domain, ["name", "project_id", "deadline", "is_reached", "reached_date"], limit=limit)
    except Exception as e:
        return [{
            "status": "module_not_installed",
            "module_required": "project",
            "message": f"Project module error or not installed: {e}",
            "suggestion": "Install the 'project' module from Odoo Apps to track milestones."
        }]
