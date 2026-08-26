from typing import Any

from core.logger import get_logger
from repositories.odoo import OdooRepository

logger = get_logger(__name__)


class InvoicingService:
    def __init__(self, odoo_repo: OdooRepository):
        self.odoo = odoo_repo

    def create_invoice(
        self, partner_id: int, amount: float, description: str
    ) -> dict[str, Any]:
        invoice_id = self.odoo.create_invoice(partner_id, amount, description)
        return {"status": "success", "invoice_id": invoice_id}

    def get_invoices(
        self, partner_id: int | None = None, state: str | None = None, limit: int = 50, offset: int = 0, date_from: str | None = None, date_to: str | None = None, overdue_only: bool = False
    ) -> list[dict[str, Any]]:
        return self.odoo.get_invoices(partner_id, state, limit, offset, date_from, date_to, overdue_only=overdue_only)

    def post_invoice(self, invoice_id: int) -> dict[str, Any]:
        self.odoo.post_invoice(invoice_id)
        return {"status": "success", "message": f"Invoice {invoice_id} posted."}

    def register_payment(
        self, invoice_id: int, amount: float, journal_id: int
    ) -> dict[str, Any]:
        result = self.odoo.register_payment(invoice_id, amount, journal_id)
        return {"status": "success", "result": result}

    def get_payment_journals(self) -> list[dict[str, Any]]:
        return self.odoo.get_payment_journals()

    from core.cache import cache_response
    
    @cache_response(ttl_seconds=300)
    def predict_cashflow_shortages(self) -> dict[str, Any]:
        """
        Analyzes unpaid Accounts Receivable (AR) vs Accounts Payable (AP)
        to forecast if the company will run out of cash in the next 30 days.
        """
        import datetime
        from datetime import timedelta
        
        today = datetime.date.today()
        thirty_days = today + timedelta(days=30)
        
        # Fetch posted, unpaid invoices (AR and AP)
        invoices = self.odoo.search_read_records(
            "account.move",
            domain=[
                ("state", "=", "posted"),
                ("payment_state", "in", ["not_paid", "partial"]),
                ("move_type", "in", ["out_invoice", "in_invoice"])
            ],
            fields=["name", "move_type", "amount_residual", "invoice_date_due", "partner_id"],
            limit=500
        )
        
        ar_30_days = 0.0
        ap_30_days = 0.0
        
        for inv in invoices:
            due_str = inv.get("invoice_date_due")
            if not due_str:
                continue
            due_date = datetime.datetime.strptime(due_str, "%Y-%m-%d").date()
            
            # Only count invoices due within the next 30 days (or overdue)
            if due_date <= thirty_days:
                residual = float(inv.get("amount_residual", 0.0))
                if inv.get("move_type") == "out_invoice":
                    ar_30_days += residual
                elif inv.get("move_type") == "in_invoice":
                    ap_30_days += residual
                    
        # A simple proxy for cashflow health
        net_cashflow_30_days = ar_30_days - ap_30_days
        risk_level = "Healthy"
        if net_cashflow_30_days < 0:
            risk_level = "High Risk - Potential Shortage"
        elif net_cashflow_30_days < (ap_30_days * 0.2):
            risk_level = "Medium Risk - Tight Cashflow"
            
        return {
            "status": "success",
            "forecast_period": "30 Days",
            "accounts_receivable_due": round(ar_30_days, 2),
            "accounts_payable_due": round(ap_30_days, 2),
            "projected_net_cashflow": round(net_cashflow_30_days, 2),
            "risk_level": risk_level,
            "recommendation": "Follow up on overdue customer invoices immediately to improve liquidity." if risk_level != "Healthy" else "Cashflow looks stable."
        }
