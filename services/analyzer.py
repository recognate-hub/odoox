from typing import Any

from core.logger import get_logger
from repositories.odoo import OdooRepository

logger = get_logger(__name__)


class AnalyzerService:
    """
    A unified service that fetches high-level structural and metric aggregations
    across the entire Odoo system using read_group to prevent large payload timeouts.
    """
    def __init__(self, odoo_repo: OdooRepository):
        self.odoo = odoo_repo

    def analyze_system_structure(self) -> dict[str, Any]:
        """Returns installed apps and core company metadata."""
        try:
            installed_apps = self.odoo.search_read_records(
                "ir.module.module",
                domain=[("state", "=", "installed")],
                fields=["name", "shortdesc", "version", "category_id"],
                limit=200
            )
            apps_list = [
                {"name": app["name"], "desc": app.get("shortdesc"), "category": app.get("category_id")}
                for app in installed_apps
            ]
        except Exception as e:
            logger.warning(f"Failed to fetch installed apps: {e}")
            installed_apps = []
            apps_list = [{"error": "Insufficient permissions to read installed apps"}]

        try:
            users_count = self.odoo.execute_method("res.users", "search_count", [[]])
        except Exception as e:
            logger.warning(f"Failed to fetch users count: {e}")
            users_count = 0

        try:
            companies = self.odoo.search_read_records(
                "res.company", 
                domain=[], 
                fields=["name", "currency_id"], 
                limit=10
            )
        except Exception as e:
            logger.warning(f"Failed to fetch companies: {e}")
            companies = [{"error": "Insufficient permissions to read companies"}]

        return {
            "installed_apps_count": len(installed_apps),
            "installed_apps": apps_list,
            "active_users_count": users_count,
            "companies": companies
        }

    def analyze_pipeline_metrics(self) -> dict[str, Any]:
        """Aggregates CRM leads and Sales orders."""
        try:
            crm_pipeline = self.odoo.read_group(
                "crm.lead",
                domain=[("active", "=", True)],
                fields=["stage_id", "expected_revenue"],
                groupby=["stage_id"]
            )
        except Exception:
            crm_pipeline = {"error": "CRM module not installed or accessible"}

        try:
            sales_pipeline = self.odoo.read_group(
                "sale.order",
                domain=[],
                fields=["state", "amount_total"],
                groupby=["state"]
            )
        except Exception:
            sales_pipeline = {"error": "Sales module not installed or accessible"}

        return {
            "crm_pipeline_by_stage": crm_pipeline,
            "sales_orders_by_state": sales_pipeline
        }

    def analyze_production_metrics(self) -> dict[str, Any]:
        """Aggregates active Work Orders and MOs."""
        try:
            # Active MOs by state
            mo_by_state = self.odoo.read_group(
                "mrp.production",
                domain=[("state", "not in", ["cancel", "done"])],
                fields=["state", "product_qty"],
                groupby=["state"]
            )
        except Exception:
            mo_by_state = {"error": "MRP module not installed or accessible"}

        try:
            # WIP by Workcenter
            wip_by_workcenter = self.odoo.read_group(
                "mrp.workorder",
                domain=[("state", "in", ["pending", "waiting", "ready", "progress"])],
                fields=["workcenter_id", "qty_production"],
                groupby=["workcenter_id"]
            )
        except Exception:
            wip_by_workcenter = {"error": "MRP module not installed or accessible"}

        return {
            "active_manufacturing_orders_by_state": mo_by_state,
            "wip_by_workcenter": wip_by_workcenter
        }

    def analyze_inventory_financials(self) -> dict[str, Any]:
        """Aggregates stock valuation and invoicing metrics."""
        try:
            # Total Stock Valuation
            valuation_total = self.odoo.read_group(
                "stock.valuation.layer",
                domain=[],
                fields=["value"],
                groupby=[]
            )
        except Exception:
            valuation_total = {"error": "Stock valuation not accessible"}

        try:
            # Invoicing by state
            invoicing_by_state = self.odoo.read_group(
                "account.move",
                domain=[("move_type", "in", ["out_invoice", "in_invoice"])],
                fields=["state", "amount_total"],
                groupby=["state"]
            )
        except Exception:
            invoicing_by_state = {"error": "Account module not installed or accessible"}

        return {
            "stock_valuation_total": valuation_total,
            "invoices_by_state": invoicing_by_state
        }
