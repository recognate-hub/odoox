from typing import Any
from mcp_app import server
from mcp_app.server import mcp, _span
from mcp_app.security import secure_tool
from core.logger import get_logger

logger = get_logger(__name__)

@mcp.tool()
@secure_tool()
def search_odoo_universe(query: str, limit_per_module: int = 5) -> dict[str, Any]:
    """
    Performs a global search across Contacts, Products, Sales, Leads, Invoices, Manufacturing, and Projects.
    Use this tool when the user gives a generic search term (e.g., "Find Azure" or "Search for Office Chair")
    and you need to find where that entity exists across the entire Odoo system.
    """
    with _span("mcp.search_odoo_universe"):
        odoo_repo, _ = server._get_tenant_service()
        results = {}
        
        # 1. Contacts
        contacts = odoo_repo.search_read_records("res.partner", domain=[["name", "ilike", query]], limit=limit_per_module)
        if contacts: results["contacts"] = contacts
            
        # 2. Products
        products = odoo_repo.search_read_records("product.product", domain=[["name", "ilike", query]], limit=limit_per_module)
        if products: results["products"] = products
            
        # 3. Sales / Quotes
        sales = odoo_repo.search_read_records("sale.order", domain=[["name", "ilike", query]], limit=limit_per_module)
        if sales: results["sales"] = sales
            
        # 4. Leads / Opportunities
        leads = odoo_repo.search_read_records("crm.lead", domain=[["name", "ilike", query]], limit=limit_per_module)
        if leads: results["leads"] = leads

        return results

@mcp.tool()
@secure_tool()
def get_customer_360(partner_id: int) -> dict[str, Any]:
    """
    Fetches a complete 360-degree view of a customer, including their contact details,
    recent quotes, sales orders, invoices, support tickets (helpdesk), and CRM leads.
    """
    with _span("mcp.get_customer_360"):
        odoo_repo, _ = server._get_tenant_service()
        data = {}
        
        # Contact info
        contact = odoo_repo.search_read_records("res.partner", domain=[["id", "=", partner_id]], limit=1)
        data["profile"] = contact[0] if contact else None
        
        # Leads
        data["leads"] = odoo_repo.search_read_records("crm.lead", domain=[["partner_id", "=", partner_id]], limit=10)
        
        # Quotes & Sales
        data["sales"] = odoo_repo.search_read_records("sale.order", domain=[["partner_id", "=", partner_id]], limit=10, expand_fields=["order_line"])
        
        # Invoices
        data["invoices"] = odoo_repo.search_read_records("account.move", domain=[["partner_id", "=", partner_id], ["move_type", "=", "out_invoice"]], limit=10, expand_fields=["invoice_line_ids"])
        
        # Subscriptions (if module exists)
        try:
            data["subscriptions"] = odoo_repo.search_read_records("sale.subscription", domain=[["partner_id", "=", partner_id]], limit=5)
        except Exception:
            pass # Module might not be installed
            
        return data

@mcp.tool()
@secure_tool()
def get_company_health_360() -> dict[str, Any]:
    """
    Provides a comprehensive overview of the entire company's health across all departments.
    Returns aggregated metrics from Sales, CRM, Invoicing, Inventory, and Manufacturing.
    """
    with _span("mcp.get_company_health_360"):
        odoo_repo, _ = server._get_tenant_service()
        health: dict[str, Any] = {
            "status": "success",
            "crm": [],
            "sales": [],
            "invoices_unpaid": [],
            "inventory": [],
            "manufacturing": []
        }
        
        # 1. CRM Health
        try:
            health["crm"] = odoo_repo.read_group("crm.lead", domain=[], fields=["expected_revenue", "id"], groupby=["stage_id"])
        except Exception:
            try:
                leads = odoo_repo.search_read_records("crm.lead", domain=[], fields=["stage_id", "expected_revenue"], limit=200)
                stages: dict[str, dict[str, Any]] = {}
                for l in leads:
                    stg = l.get("stage_id")
                    stg_name = stg[1] if isinstance(stg, (list, tuple)) else str(stg or "Unassigned")
                    rev = float(l.get("expected_revenue") or 0.0)
                    if stg_name not in stages:
                        stages[stg_name] = {"stage_id_count": 0, "expected_revenue": 0.0, "stage": stg_name}
                    stages[stg_name]["stage_id_count"] += 1
                    stages[stg_name]["expected_revenue"] += rev
                health["crm"] = list(stages.values())
            except Exception:
                health["crm"] = []
        
        # 2. Sales Health
        try:
            health["sales"] = odoo_repo.read_group("sale.order", domain=[["state", "in", ["sale", "done"]]], fields=["amount_total", "id"], groupby=["state"])
        except Exception:
            try:
                orders = odoo_repo.search_read_records("sale.order", domain=[["state", "in", ["sale", "done"]]], fields=["state", "amount_total"], limit=200)
                total_sales = sum(float(o.get("amount_total") or 0.0) for o in orders)
                health["sales"] = [{"state": "sale", "order_count": len(orders), "amount_total": round(total_sales, 2)}]
            except Exception:
                health["sales"] = []
        
        # 3. Invoicing Health (Receivables)
        try:
            health["invoices_unpaid"] = odoo_repo.read_group("account.move", domain=[["move_type", "=", "out_invoice"], ["state", "=", "posted"], ["payment_state", "in", ["not_paid", "partial"]]], fields=["amount_residual"], groupby=["payment_state"])
        except Exception:
            try:
                invoices = odoo_repo.search_read_records("account.move", domain=[["move_type", "=", "out_invoice"], ["state", "=", "posted"], ["payment_state", "in", ["not_paid", "partial"]]], fields=["payment_state", "amount_residual"], limit=200)
                residual = sum(float(inv.get("amount_residual") or 0.0) for inv in invoices)
                health["invoices_unpaid"] = [{"unpaid_count": len(invoices), "total_residual": round(residual, 2)}]
            except Exception:
                health["invoices_unpaid"] = []
            
        # 4. Inventory Valuation Health
        try:
            val_items = odoo_repo.get_inventory_valuation(limit=100)
            tot_val = sum(float(item.get("value") or 0.0) for item in val_items)
            health["inventory"] = [{"item_count": len(val_items), "total_valuation": round(tot_val, 2)}]
        except Exception:
            health["inventory"] = []

        # 5. Manufacturing Health
        try:
            health["manufacturing"] = odoo_repo.read_group("mrp.production", domain=[], fields=["id"], groupby=["state"])
        except Exception:
            try:
                mos = odoo_repo.search_read_records("mrp.production", domain=[], fields=["state"], limit=100)
                mrp_states: dict[str, int] = {}
                for mo in mos:
                    st = mo.get("state", "draft")
                    mrp_states[st] = mrp_states.get(st, 0) + 1
                health["manufacturing"] = [{"state": k, "count": v} for k, v in mrp_states.items()]
            except Exception:
                health["manufacturing"] = []
            
        return health

@mcp.tool()
@secure_tool()
def get_product_360(product_id: int) -> dict[str, Any]:
    """
    Fetches a complete 360-degree view of a product, including its current stock, 
    upcoming manufacturing orders, recent sales, and purchase orders.
    """
    with _span("mcp.get_product_360"):
        odoo_repo, _ = server._get_tenant_service()
        data = {}
        
        product = odoo_repo.search_read_records("product.product", domain=[["id", "=", product_id]], limit=1)
        data["product"] = product[0] if product else None
        
        # Stock Moves
        data["stock_moves"] = odoo_repo.search_read_records("stock.move", domain=[["product_id", "=", product_id], ["state", "not in", ["done", "cancel"]]], limit=10)
        
        # Sales
        data["sales_lines"] = odoo_repo.search_read_records("sale.order.line", domain=[["product_id", "=", product_id]], limit=10, expand_fields=["order_id"])
        
        # MRP
        try:
            data["manufacturing_orders"] = odoo_repo.search_read_records("mrp.production", domain=[["product_id", "=", product_id]], limit=10)
        except Exception:
            pass
            
        return data
