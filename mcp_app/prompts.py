"""
MCP Prompts Registry for OdooX.
Provides standard, reusable AI workflows and executive prompt templates for Claude, Cursor, and other LLMs.
"""

from typing import Any
from mcp_app.server import mcp


@mcp.prompt()
def daily_business_briefing(
    include_crm: bool = True,
    include_manufacturing: bool = True,
    include_invoicing: bool = True,
) -> str:
    """
    Generate an executive morning briefing across CRM, Manufacturing, and Invoicing.
    """
    sections = []
    if include_crm:
        sections.append("- Call `analyze_pipeline_metrics` and `get_sales_dashboard` to summarize current revenue, active deals, and conversion rates.")
    if include_manufacturing:
        sections.append("- Call `analyze_production_metrics` and `get_active_workorders` to highlight manufacturing bottlenecks and delayed production orders.")
    if include_invoicing:
        sections.append("- Call `analyze_inventory_financials` and `get_unpaid_invoices` to report outstanding customer receivables and cash flow risks.")

    steps = "\n".join(sections)
    return (
        "You are the executive AI Chief Operating Officer for this business.\n"
        "Please conduct a comprehensive Daily Business Briefing by executing the following tool calls:\n\n"
        f"{steps}\n\n"
        "Synthesize the results into a clean, actionable markdown executive summary with:\n"
        "1. 📊 Key Operational KPIs\n"
        "2. 🚨 Critical Alerts & Bottlenecks\n"
        "3. 🎯 Top 3 Recommended Strategic Actions for Today"
    )


@mcp.prompt()
def crm_lead_prioritization(min_expected_revenue: float = 1000.0) -> str:
    """
    Perform deep lead prioritization and deal triage for sales reps.
    """
    return (
        f"You are a Sales Strategy & Revenue Operations AI Specialist.\n"
        f"1. Call `get_active_leads(limit=50)` and filter for leads with expected revenue >= {min_expected_revenue}.\n"
        "2. Analyze deal stages, win probabilities, and recent customer interactions using `get_customer_details` where needed.\n"
        "3. Rank the top 5 highest-priority opportunities and generate a concrete 3-step closing plan for each lead."
    )


@mcp.prompt()
def manufacturing_bottleneck_audit() -> str:
    """
    Audit shop floor operations, identify workcenter overloads, and propose rescheduling.
    """
    return (
        "You are a Lean Manufacturing and Industrial Engineering AI Expert.\n"
        "1. Call `analyze_production_metrics` and `get_active_workorders(limit=50)`.\n"
        "2. Query machine health using `get_equipment_status` and active maintenance requests using `get_maintenance_requests`.\n"
        "3. Identify work centers operating at or near 100% capacity or suffering from unhandled downtime.\n"
        "4. Output a bottleneck resolution matrix with concrete workorder rescheduling recommendations."
    )


@mcp.prompt()
def financial_health_audit() -> str:
    """
    Perform a financial health check on unpaid invoices, cashflow risks, and vendor payables.
    """
    return (
        "You are a Corporate Finance & CFO AI Advisory Agent.\n"
        "1. Call `analyze_inventory_financials` and `get_unpaid_invoices(limit=50)`.\n"
        "2. Call `get_overdue_payments` and inspect high-risk aging accounts receivable.\n"
        "3. Calculate the total overdue balance, categorize default risk, and draft polite payment reminder strategies for overdue accounts."
    )


@mcp.prompt()
def inventory_reorder_recommendation() -> str:
    """
    Analyze stock levels against safety stock thresholds and recommend purchase orders.
    """
    return (
        "You are a Supply Chain & Inventory Optimization AI Agent.\n"
        "1. Call `get_low_stock_products` and inspect warehouse stock levels.\n"
        "2. For items with critical stock depletion, check existing vendor relations and purchase lead times.\n"
        "3. Generate a recommended Purchase Order batch summary specifying recommended reorder quantities and estimated lead times."
    )
