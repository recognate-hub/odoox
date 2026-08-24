from typing import Any
from core.logger import get_logger
from mcp_app import server
from mcp_app.security import secure_tool
from mcp_app.server import _span, mcp
import datetime

logger = get_logger(__name__)


@mcp.tool()
@secure_tool()
def get_aged_receivables(limit: int = 100) -> list[dict[str, Any]]:
    """
    Retrieve outstanding and overdue customer invoices (aged receivables).

    Use this tool to track pending payments and cash flow bottlenecks.

    Args:
        limit (int): Maximum number of unpaid invoices to return. Default is 100.

    Returns:
        List[Dict[str, Any]]: Unpaid customer invoices with amounts and due dates.
    """
    with _span("mcp.get_aged_receivables") as span:
        logger.info("MCP Tool Called: get_aged_receivables", limit=limit)
        odoo_repo, _ = server._get_tenant_service()
        
        # In Odoo, invoices are account.move with move_type='out_invoice' and payment_state in ('not_paid', 'partial')
        domain = [
            ["move_type", "=", "out_invoice"],
            ["payment_state", "in", ["not_paid", "partial"]],
            ["state", "=", "posted"]
        ]
        fields = ["name", "partner_id", "invoice_date", "invoice_date_due", "amount_total", "amount_residual"]
        
        try:
            invoices = odoo_repo.search_read("account.move", domain, fields, limit=limit)
            
            today = datetime.date.today()
            for inv in invoices:
                due_date_str = inv.get("invoice_date_due")
                if due_date_str:
                    try:
                        # Odoo returns dates as strings YYYY-MM-DD
                        due_date = datetime.datetime.strptime(due_date_str, "%Y-%m-%d").date()
                        days_overdue = (today - due_date).days
                        inv["days_overdue"] = max(0, days_overdue)
                        
                        # Bucket aging
                        if days_overdue <= 0:
                            inv["aging_bucket"] = "Current"
                        elif days_overdue <= 30:
                            inv["aging_bucket"] = "1-30 Days"
                        elif days_overdue <= 60:
                            inv["aging_bucket"] = "31-60 Days"
                        elif days_overdue <= 90:
                            inv["aging_bucket"] = "61-90 Days"
                        else:
                            inv["aging_bucket"] = "90+ Days"
                    except Exception:
                        inv["days_overdue"] = 0
                        inv["aging_bucket"] = "Unknown"
                else:
                    inv["days_overdue"] = 0
                    inv["aging_bucket"] = "No Due Date"
                    
            return invoices
        except Exception as e:
            logger.error("get_aged_receivables error", error=str(e))
            return [{"status": "error", "message": str(e)}]


@mcp.tool()
@secure_tool()
def get_profit_and_loss_summary() -> list[dict[str, Any]]:
    """
    Calculate a high-level Profit & Loss summary.

    Use this tool to analyze income vs expenses across accounting accounts.

    Returns:
        List[Dict[str, Any]]: Aggregated financial metrics grouped by account internal type.
    """
    logger.info("MCP Tool Called: get_profit_and_loss_summary")
    odoo_repo, _ = server._get_tenant_service()
    try:
        # We query account.move.line where account type is Income or Expense
        # This requires matching the internal types for Income/Expense in Odoo
        domain = [
            ["account_id.internal_group", "in", ["income", "expense"]],
            ["parent_state", "=", "posted"]
        ]
        fields = ["account_id", "balance", "debit", "credit"]
        groupby = ["account_id"]
        
        return odoo_repo.read_group("account.move.line", domain, fields, groupby)
    except Exception as e:
        logger.error("get_profit_and_loss_summary error", error=str(e))
        return [{"status": "error", "message": str(e)}]


@mcp.tool()
@secure_tool()
def analyze_expense_trends() -> list[dict[str, Any]]:
    """
    Track the fastest-growing or largest expense accounts.

    Use this tool to find out where the company is spending the most money.

    Returns:
        List[Dict[str, Any]]: Aggregated expense metrics by account.
    """
    logger.info("MCP Tool Called: analyze_expense_trends")
    odoo_repo, _ = server._get_tenant_service()
    try:
        # Query only expense accounts
        domain = [
            ["account_id.internal_group", "=", "expense"],
            ["parent_state", "=", "posted"]
        ]
        fields = ["account_id", "balance"]
        groupby = ["account_id"]
        
        return odoo_repo.read_group("account.move.line", domain, fields, groupby)
    except Exception as e:
        logger.error("analyze_expense_trends error", error=str(e))
        return [{"status": "error", "message": str(e)}]
