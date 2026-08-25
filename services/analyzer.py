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
            crm_leads = self.odoo.search_read_records(
                "crm.lead",
                domain=[("active", "=", True)],
                fields=["stage_id", "expected_revenue"],
                limit=5000
            )
            crm_summary = {}
            for lead in crm_leads:
                stage = lead.get("stage_id")
                if not stage:
                    continue
                stage_id = stage[0] if isinstance(stage, (list, tuple)) else stage
                if stage_id not in crm_summary:
                    crm_summary[stage_id] = {
                        "stage_id": stage,
                        "stage_id_count": 0,
                        "expected_revenue": 0.0
                    }
                crm_summary[stage_id]["stage_id_count"] += 1
                crm_summary[stage_id]["expected_revenue"] += lead.get("expected_revenue", 0.0)
            crm_pipeline = list(crm_summary.values())
        except Exception:
            crm_pipeline = {"error": "CRM module not installed or accessible"}

        try:
            sales_orders = self.odoo.search_read_records(
                "sale.order",
                domain=[],
                fields=["state", "amount_total"],
                limit=5000
            )
            sales_summary = {}
            for so in sales_orders:
                state = so.get("state")
                if not state:
                    continue
                if state not in sales_summary:
                    sales_summary[state] = {
                        "state": state,
                        "state_count": 0,
                        "amount_total": 0.0
                    }
                sales_summary[state]["state_count"] += 1
                sales_summary[state]["amount_total"] += so.get("amount_total", 0.0)
            sales_pipeline = list(sales_summary.values())
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
            mos = self.odoo.search_read_records(
                "mrp.production",
                domain=[("state", "not in", ["cancel", "done"])],
                fields=["state", "product_qty"],
                limit=5000
            )
            mo_summary = {}
            for mo in mos:
                state = mo.get("state")
                if not state:
                    continue
                if state not in mo_summary:
                    mo_summary[state] = {
                        "state": state,
                        "state_count": 0,
                        "product_qty": 0.0
                    }
                mo_summary[state]["state_count"] += 1
                mo_summary[state]["product_qty"] += mo.get("product_qty", 0.0)
            mo_by_state = list(mo_summary.values())
        except Exception:
            mo_by_state = {"error": "MRP module not installed or accessible"}

        try:
            # WIP by Workcenter
            wos = self.odoo.search_read_records(
                "mrp.workorder",
                domain=[("state", "in", ["pending", "waiting", "ready", "progress"])],
                fields=["workcenter_id", "qty_production"],
                limit=5000
            )
            wip_summary = {}
            for wo in wos:
                wc = wo.get("workcenter_id")
                if not wc:
                    continue
                wc_id = wc[0] if isinstance(wc, (list, tuple)) else wc
                if wc_id not in wip_summary:
                    wip_summary[wc_id] = {
                        "workcenter_id": wc,
                        "workcenter_id_count": 0,
                        "qty_production": 0.0
                    }
                wip_summary[wc_id]["workcenter_id_count"] += 1
                wip_summary[wc_id]["qty_production"] += wo.get("qty_production", 0.0)
            wip_by_workcenter = list(wip_summary.values())
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
            layers = self.odoo.search_read_records(
                "stock.valuation.layer",
                domain=[],
                fields=["value"],
                limit=5000
            )
            total_value = sum(layer.get("value", 0.0) for layer in layers)
            valuation_total = [{"value": total_value, "value_count": len(layers)}]
        except Exception:
            valuation_total = {"error": "Stock valuation not accessible"}

        try:
            # Invoicing by state
            invoices = self.odoo.search_read_records(
                "account.move",
                domain=[("move_type", "in", ["out_invoice", "in_invoice"])],
                fields=["state", "amount_total"],
                limit=5000
            )
            inv_summary = {}
            for inv in invoices:
                state = inv.get("state")
                if not state:
                    continue
                if state not in inv_summary:
                    inv_summary[state] = {
                        "state": state,
                        "state_count": 0,
                        "amount_total": 0.0
                    }
                inv_summary[state]["state_count"] += 1
                inv_summary[state]["amount_total"] += inv.get("amount_total", 0.0)
            invoicing_by_state = list(inv_summary.values())
        except Exception:
            invoicing_by_state = {"error": "Account module not installed or accessible"}

        return {
            "stock_valuation_total": valuation_total,
            "invoices_by_state": invoicing_by_state
        }
