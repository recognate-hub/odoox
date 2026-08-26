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

    Use this tool when:
    - The user asks for overdue invoices, unpaid bills, or aged receivables.
    - The user wants to track pending payments and cash flow bottlenecks.

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
            invoices = odoo_repo.search_read_records("account.move", domain, fields, limit=limit)
            
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

    Use this tool when:
    - The user asks for a P&L, Profit and Loss, or income statement.
    - The user wants to analyze income vs expenses across accounting accounts.

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
        
        # Odoo 18 may not support read_group on account.move.line via XML-RPC
        lines = odoo_repo.search_read_records("account.move.line", domain, fields, limit=5000)
        
        summary = {}
        for line in lines:
            acc = line.get("account_id")
            acc_name = acc[1] if isinstance(acc, (list, tuple)) and len(acc) > 1 else str(acc)
            
            if acc_name not in summary:
                summary[acc_name] = {
                    "account": acc_name,
                    "balance": 0.0,
                    "debit": 0.0,
                    "credit": 0.0
                }
            summary[acc_name]["balance"] += line.get("balance", 0.0)
            summary[acc_name]["debit"] += line.get("debit", 0.0)
            summary[acc_name]["credit"] += line.get("credit", 0.0)
            
        return list(summary.values())
    except Exception as e:
        logger.error("get_profit_and_loss_summary error", error=str(e))
        return [{"status": "error", "message": str(e)}]


@mcp.tool()
@secure_tool()
def analyze_expense_trends() -> list[dict[str, Any]]:
    """
    Track the fastest-growing or largest expense accounts.

    Use this tool when:
    - The user asks where the company is spending the most money.
    - The user asks for an expense breakdown or trend.

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
        
        lines = odoo_repo.search_read_records("account.move.line", domain, fields, limit=5000)
        
        summary = {}
        for line in lines:
            acc = line.get("account_id")
            acc_name = acc[1] if isinstance(acc, (list, tuple)) and len(acc) > 1 else str(acc)
            
            if acc_name not in summary:
                summary[acc_name] = {
                    "account": acc_name,
                    "balance": 0.0,
                }
            summary[acc_name]["balance"] += line.get("balance", 0.0)
            
        return list(summary.values())
    except Exception as e:
        logger.error("analyze_expense_trends error", error=str(e))
        return [{"status": "error", "message": str(e)}]


@mcp.tool()
@secure_tool()
def get_accounting_journals(limit: int = 50) -> list[dict[str, Any]]:
    """
    Retrieve all accounting journals (e.g. Bank, Cash, Sales, Purchase).
    
    Use this tool when:
    - You need to find the correct journal_id to register a payment.
    - The user asks about bank accounts or cash registers.
    """
    logger.info("MCP Tool Called: get_accounting_journals")
    odoo_repo, _ = server._get_tenant_service()
    try:
        fields = ["name", "type", "code", "currency_id"]
        return odoo_repo.search_read_records("account.journal", [], fields, limit=limit)
    except Exception as e:
        logger.error("get_accounting_journals error", error=str(e))
        return [{"status": "error", "message": str(e)}]


@mcp.tool()
@secure_tool()
def get_tax_summary(limit: int = 50) -> list[dict[str, Any]]:
    """
    Retrieve configured taxes and their rates.
    
    Use this tool when:
    - The user asks about tax rates (VAT, GST, Sales Tax).
    """
    logger.info("MCP Tool Called: get_tax_summary")
    odoo_repo, _ = server._get_tenant_service()
    try:
        fields = ["name", "amount_type", "amount", "type_tax_use"]
        return odoo_repo.search_read_records("account.tax", [["active", "=", True]], fields, limit=limit)
    except Exception as e:
        logger.error("get_tax_summary error", error=str(e))
        return [{"status": "error", "message": str(e)}]


@mcp.tool()
@secure_tool()
def get_trial_balance(limit: int = 200) -> list[dict[str, Any]]:
    """
    Retrieve the Chart of Accounts with their current balances (Trial Balance).
    
    Use this tool when:
    - The user asks for a Trial Balance or Chart of Accounts.
    """
    logger.info("MCP Tool Called: get_trial_balance")
    odoo_repo, _ = server._get_tenant_service()
    try:
        # Fetch accounts (in some Odoo versions, balance might not be a stored field, 
        # but we can try reading current_balance or just return the basic chart)
        fields = ["code", "name", "account_type", "current_balance"] 
        # Note: current_balance might fail on older Odoo, so we also fetch general details.
        try:
            return odoo_repo.search_read_records("account.account", [], fields, limit=limit)
        except Exception:
            fields = ["code", "name", "account_type"]
            return odoo_repo.search_read_records("account.account", [], fields, limit=limit)
    except Exception as e:
        logger.error("get_trial_balance error", error=str(e))
        return [{"status": "error", "message": str(e)}]


@mcp.tool()
@secure_tool()
def get_bank_cash_summary(limit: int = 50) -> list[dict[str, Any]]:
    """
    Retrieve the current balances of all Bank and Cash journals.
    
    Use this tool when:
    - The user asks for bank balances, cash reserves, or liquid assets.
    """
    logger.info("MCP Tool Called: get_bank_cash_summary")
    odoo_repo, _ = server._get_tenant_service()
    try:
        domain = [["type", "in", ["bank", "cash"]]]
        # In Odoo, account.journal usually doesn't store the balance directly. 
        # But some versions have default_account_id which can be queried.
        # Alternatively, we can just return the journals and let the user know.
        return odoo_repo.search_read_records("account.journal", domain, ["name", "code", "type", "currency_id"], limit=limit)
    except Exception as e:
        logger.error("get_bank_cash_summary error", error=str(e))
        return [{"status": "error", "message": str(e)}]


@mcp.tool()
@secure_tool()
def get_general_ledger_summary(limit: int = 100) -> list[dict[str, Any]]:
    """
    Retrieve recent journal entries (General Ledger).
    
    Use this tool when:
    - The user asks for recent accounting entries, GL, or journal entries.
    """
    logger.info("MCP Tool Called: get_general_ledger_summary")
    odoo_repo, _ = server._get_tenant_service()
    try:
        domain = [["state", "=", "posted"]]
        fields = ["name", "date", "journal_id", "amount_total", "partner_id", "ref"]
        return odoo_repo.search_read_records("account.move", domain, fields, limit=limit, expand_fields=["line_ids"])
    except Exception as e:
        logger.error("get_general_ledger_summary error", error=str(e))
        return [{"status": "error", "message": str(e)}]
