from typing import List, Dict, Any, Optional
from odoo.interface import OdooConnectorInterface
from schemas.odoo import (
    OdooLead,
    OdooContact,
    OdooProduct,
    OdooQuote,
    OdooActivity,
    OdooMeeting,
    OdooSalesDashboard
)


class OdooRepository:
    """
    Repository pattern over the Odoo Connector.
    Provides domain-specific query building and abstracts away raw Odoo domains.
    """

    def __init__(self, connector: OdooConnectorInterface):
        self.connector = connector

    def get_active_leads(self, limit: int = 100) -> List[OdooLead]:
        domain = [["type", "=", "opportunity"]]
        return self.connector.get_leads(domain=domain, limit=limit)

    def get_lead_by_id(self, lead_id: int) -> Optional[OdooLead]:
        domain = [["id", "=", lead_id]]
        leads = self.connector.get_leads(domain=domain, limit=1)
        return leads[0] if leads else None

    def search_contacts_by_name(self, name_query: str, limit: int = 20) -> List[OdooContact]:
        domain = [["name", "ilike", name_query]]
        return self.connector.search_contacts(domain=domain, limit=limit)

    def search_products(self, query: str, limit: int = 20) -> List[OdooProduct]:
        domain = [["name", "ilike", query]]
        return self.connector.get_products(domain=domain, limit=limit)

    def get_recent_quotes(self, partner_id: Optional[int] = None, limit: int = 10) -> List[OdooQuote]:
        domain = []
        if partner_id:
            domain.append(["partner_id", "=", partner_id])
        return self.connector.get_quotes(domain=domain, limit=limit)

    def create_lead(self, name: str, email: Optional[str] = None, phone: Optional[str] = None, description: Optional[str] = None) -> int:
        data = {"name": name, "type": "opportunity"}
        if email:
            data["email_from"] = email
        if phone:
            data["phone"] = phone
        if description:
            data["description"] = description
        return self.connector.create_lead(data)

    def log_activity(self, res_model: str, res_id: int, summary: str, activity_type_id: int = 4) -> int:
        # activity_type_id 4 is usually 'Todo' or 'Email' in Odoo, should be configurable in a real app
        data = {
            "res_model": res_model,
            "res_id": res_id,
            "summary": summary,
            "activity_type_id": activity_type_id
        }
        return self.connector.create_activity(data)

    def schedule_meeting(self, name: str, start: str, stop: str, partner_ids: List[int]) -> int:
        data = {
            "name": name,
            "start": start,
            "stop": stop,
            "partner_ids": [[6, 0, partner_ids]]  # Odoo Many2many syntax
        }
        return self.connector.schedule_meeting(data)

    def get_dashboard(self) -> OdooSalesDashboard:
        return self.connector.get_sales_dashboard()
