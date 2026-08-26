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

    Use this tool when:
    - The user wants a list of employees.
    - The user asks to find a specific employee by name.
    - The user asks for all employees in a specific department.

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
            
        fields = ["name", "job_title", "department_id", "work_email", "work_phone"]
        
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

    Use this tool when:
    - The user asks for a summary of employee time off.
    - The user wants to identify departments with high absence rates.
    
    Do NOT use this tool when:
    - You need a specific employee's time off request (use search_read_records).

    Returns:
        List[Dict[str, Any]]: Aggregated leave metrics grouped by department and leave type.
    """
    logger.info("MCP Tool Called: analyze_leave_trends")
    odoo_repo, _ = server._get_tenant_service()
    try:
        domain = [["state", "=", "validate"]]
        fields = ["department_id", "holiday_status_id", "number_of_days"]
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

    Use this tool when:
    - The user wants to track hours logged by employees.
    - The user asks how much time an employee spent on a project or task.

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


@mcp.tool()
@secure_tool()
def get_departments(limit: int = 50) -> list[dict[str, Any]]:
    """
    Retrieve a list of all company departments.
    
    Use this tool when:
    - The user asks for a list of departments or teams.
    - You need a department_id to filter employees.
    """
    logger.info("MCP Tool Called: get_departments")
    odoo_repo, _ = server._get_tenant_service()
    try:
        return odoo_repo.search_read_records("hr.department", [], ["name", "manager_id", "parent_id"], limit=limit, expand_fields=["manager_id", "parent_id"])
    except Exception as e:
        return [{"status": "error", "message": "Failed to fetch departments. " + str(e), "suggestion": "The HR module might not be fully configured."}]


@mcp.tool()
@secure_tool()
def get_department_structure() -> dict[str, Any]:
    """
    Retrieve the full hierarchical structure of the company's departments.
    """
    logger.info("MCP Tool Called: get_department_structure")
    odoo_repo, _ = server._get_tenant_service()
    try:
        departments = odoo_repo.search_read_records("hr.department", [], ["name", "parent_id", "manager_id"], limit=500, expand_fields=["manager_id"])
        
        # Build hierarchy tree
        tree = []
        dept_map = {d["id"]: d for d in departments if "id" in d}
        for d in departments:
            d["children"] = []
            
        for d in departments:
            parent = d.get("parent_id")
            if parent and isinstance(parent, list) and parent[0] in dept_map:
                dept_map[parent[0]]["children"].append(d)
            elif parent and isinstance(parent, dict) and parent.get("id") in dept_map:
                dept_map[parent["id"]]["children"].append(d)
            else:
                tree.append(d)
                
        return {"structure": tree}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@mcp.tool()
@secure_tool()
def get_leave_balances(employee_id: int | None = None) -> list[dict[str, Any]]:
    """
    Retrieve employee leave balances (allocations vs taken).
    """
    logger.info("MCP Tool Called: get_leave_balances")
    odoo_repo, _ = server._get_tenant_service()
    try:
        domain = [["employee_id", "=", employee_id]] if employee_id else []
        return odoo_repo.search_read_records("hr.leave.allocation", domain, ["name", "employee_id", "holiday_status_id", "number_of_days", "leaves_taken"], limit=100)
    except Exception as e:
        return [{"status": "error", "message": "Module missing or error. " + str(e)}]


@mcp.tool()
@secure_tool()
def get_attendance_records(employee_id: int | None = None, limit: int = 100) -> list[dict[str, Any]]:
    """
    Retrieve employee attendance logs (check-in / check-out times).
    
    Use this tool when:
    - The user asks about employee working hours or attendance.
    """
    logger.info("MCP Tool Called: get_attendance_records", employee_id=employee_id)
    odoo_repo, _ = server._get_tenant_service()
    domain = [["employee_id", "=", employee_id]] if employee_id else []
    try:
        return odoo_repo.search_read_records("hr.attendance", domain, ["employee_id", "check_in", "check_out", "worked_hours"], limit=limit)
    except Exception as e:
        return [{"status": "error", "message": "Module missing or error: hr.attendance. " + str(e), "suggestion": "The Attendance module (hr_attendance) must be installed.", "module_required": "hr_attendance"}]


@mcp.tool()
@secure_tool()
def get_open_jobs(limit: int = 50) -> list[dict[str, Any]]:
    """
    Retrieve active job positions (recruitment).
    
    Use this tool when:
    - The user asks about open roles, hiring, or jobs.
    """
    logger.info("MCP Tool Called: get_open_jobs")
    odoo_repo, _ = server._get_tenant_service()
    try:
        domain = [["state", "=", "recruit"]]
        return odoo_repo.search_read_records("hr.job", domain, ["name", "department_id", "no_of_recruitment", "no_of_employee"], limit=limit)
    except Exception as e:
        return [{"status": "error", "message": "Module missing or error: hr.job. " + str(e), "suggestion": "The Recruitment module (hr_recruitment) must be installed.", "module_required": "hr_recruitment"}]


@mcp.tool()
@secure_tool()
def get_job_applicants(job_id: int | None = None, limit: int = 50) -> list[dict[str, Any]]:
    """
    Retrieve candidates applying for open jobs.
    
    Use this tool when:
    - The user asks for a list of job applicants or candidates.
    """
    logger.info("MCP Tool Called: get_job_applicants", job_id=job_id)
    odoo_repo, _ = server._get_tenant_service()
    domain = [["job_id", "=", job_id]] if job_id else []
    try:
        return odoo_repo.search_read_records("hr.applicant", domain, ["name", "partner_name", "email_from", "job_id", "stage_id"], limit=limit)
    except Exception as e:
        return [{"status": "error", "message": "Module missing or error: hr.applicant. " + str(e), "suggestion": "The Recruitment module (hr_recruitment) must be installed.", "module_required": "hr_recruitment"}]


@mcp.tool()
@secure_tool()
def get_employee_contracts(employee_id: int | None = None, limit: int = 50) -> list[dict[str, Any]]:
    """
    Retrieve employee contracts (salary, wage, dates).
    
    Use this tool when:
    - The user asks for salary, wages, or contract details of an employee.
    """
    logger.info("MCP Tool Called: get_employee_contracts", employee_id=employee_id)
    odoo_repo, _ = server._get_tenant_service()
    domain = [["employee_id", "=", employee_id]] if employee_id else []
    try:
        return odoo_repo.search_read_records("hr.contract", domain, ["name", "employee_id", "job_id", "wage", "state", "date_start", "date_end"], limit=limit)
    except Exception as e:
        return [{"status": "error", "message": "Module missing or error: hr.contract. " + str(e), "suggestion": "The Contracts module (hr_contract) must be installed.", "module_required": "hr_contract"}]


@mcp.tool()
@secure_tool()
def get_employee_payslips(employee_id: int | None = None, limit: int = 50) -> list[dict[str, Any]]:
    """
    Retrieve employee payslips (payroll).
    
    Use this tool when:
    - The user asks about payslips, payroll, or compensation history.
    """
    logger.info("MCP Tool Called: get_employee_payslips", employee_id=employee_id)
    odoo_repo, _ = server._get_tenant_service()
    domain = [["employee_id", "=", employee_id]] if employee_id else []
    try:
        return odoo_repo.search_read_records("hr.payslip", domain, ["name", "employee_id", "date_from", "date_to", "state", "net_wage"], limit=limit)
    except Exception as e:
        return [{"status": "error", "message": "Module missing or error: hr.payslip. " + str(e), "suggestion": "The Payroll module (hr_payroll) must be installed.", "module_required": "hr_payroll"}]

