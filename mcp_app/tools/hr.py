from typing import Any
from core.logger import get_logger
from mcp_app import server
from mcp_app.security import secure_tool
from mcp_app.server import _span, mcp

logger = get_logger(__name__)


@mcp.tool()
@secure_tool()
def get_employee_directory(
    name_query: str | None = None, department_id: int | None = None, limit: int = 100
) -> list[dict[str, Any]]:
    """
    Search the company employee directory.

    Use this tool to fetch a list of employees, optionally filtered by name or department.

    Args:
        name_query (Optional[str]): Search by employee name (case-insensitive partial match).
        department_id (Optional[int]): Filter by a specific department ID.
        limit (int): The maximum number of employees to return. Default is 100.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries representing employees with their basic details.
    """
    with _span("mcp.get_employee_directory") as span:
        logger.info(
            "MCP Tool Called: get_employee_directory",
            limit=limit,
            query=name_query,
            department_id=department_id,
        )
        odoo_repo, _ = server._get_tenant_service()
        
        domain = []
        if name_query:
            domain.append(["name", "ilike", name_query])
        if department_id:
            domain.append(["department_id", "=", department_id])
            
        fields = ["name", "job_title", "department_id", "work_email", "work_phone", "manager_id"]
        
        try:
            return odoo_repo.search_read_records("hr.employee", domain, fields, limit=limit)
        except Exception as e:
            logger.error("get_employee_directory error", error=str(e))
            return [{"status": "error", "message": str(e)}]


@mcp.tool()
@secure_tool()
def analyze_leave_trends() -> list[dict[str, Any]]:
    """
    Analyze employee leave and time-off trends.

    Use this tool to identify departments or leave types with high absence rates by aggregating approved time-off requests.

    Returns:
        List[Dict[str, Any]]: Aggregated leave metrics grouped by department and leave type.
    """
    logger.info("MCP Tool Called: analyze_leave_trends")
    odoo_repo, _ = server._get_tenant_service()
    try:
        domain = [["state", "=", "validate"]]
        fields = ["department_id", "holiday_status_id", "number_of_days"]
        groupby = ["department_id", "holiday_status_id"]
        lines = odoo_repo.search_read_records("hr.leave", domain, fields, limit=5000)
        
        # Manual grouping since read_group might fail or not exist
        summary = {}
        for line in lines:
            dept = line.get("department_id")
            dept_name = dept[1] if isinstance(dept, (list, tuple)) and len(dept) > 1 else str(dept)
            
            leave = line.get("holiday_status_id")
            leave_name = leave[1] if isinstance(leave, (list, tuple)) and len(leave) > 1 else str(leave)
            
            key = f"{dept_name} - {leave_name}"
            days = line.get("number_of_days", 0)
            
            if key not in summary:
                summary[key] = {
                    "department": dept_name,
                    "leave_type": leave_name,
                    "total_days": 0,
                    "count": 0
                }
            summary[key]["total_days"] += days
            summary[key]["count"] += 1
            
        return list(summary.values())
    except Exception as e:
        logger.error("analyze_leave_trends error", error=str(e))
        return [{"status": "error", "message": str(e)}]


@mcp.tool()
@secure_tool()
def get_timesheet_utilization(
    employee_id: int | None = None, limit: int = 100
) -> list[dict[str, Any]]:
    """
    Retrieve timesheet utilization records to analyze workforce productivity.

    Use this tool to track the hours logged by employees on specific projects or tasks.

    Args:
        employee_id (Optional[int]): Filter timesheets by a specific employee ID.
        limit (int): The maximum number of timesheet entries to return. Default is 100.

    Returns:
        List[Dict[str, Any]]: Timesheet entries including employee, project, task, and duration.
    """
    logger.info("MCP Tool Called: get_timesheet_utilization", employee_id=employee_id)
    odoo_repo, _ = server._get_tenant_service()
    try:
        domain = []
        if employee_id:
            domain.append(["employee_id", "=", employee_id])
            
        fields = ["employee_id", "project_id", "task_id", "unit_amount", "date", "name"]
        return odoo_repo.search_read_records("account.analytic.line", domain, fields, limit=limit)
    except Exception as e:
        logger.error("get_timesheet_utilization error", error=str(e))
        return [{"status": "error", "message": str(e)}]
