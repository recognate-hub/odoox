from typing import Any

from odoo.interface import OdooConnectorInterface
from schemas.odoo import (
    OdooContact,
    OdooLead,
    OdooProduct,
    OdooQuote,
    OdooSalesDashboard,
)


class OdooRepository:
    """
    Repository pattern over the Odoo Connector.
    Provides domain-specific query building and abstracts away raw Odoo domains.
    """

    def __init__(self, connector: OdooConnectorInterface):
        self.connector = connector

    def get_active_leads(self, limit: int = 100) -> list[OdooLead]:
        domain = [["type", "=", "opportunity"]]
        return self.connector.get_leads(domain=domain, limit=limit)

    def get_lead_by_id(self, lead_id: int) -> OdooLead | None:
        domain = [["id", "=", lead_id]]
        leads = self.connector.get_leads(domain=domain, limit=1)
        return leads[0] if leads else None

    def search_contacts_by_name(self, name_query: str, limit: int = 20) -> list[OdooContact]:
        domain = [["name", "ilike", name_query]]
        return self.connector.search_contacts(domain=domain, limit=limit)

    def search_products(self, query: str, limit: int = 20) -> list[OdooProduct]:
        domain = [["name", "ilike", query]]
        return self.connector.get_products(domain=domain, limit=limit)

    def get_recent_quotes(self, partner_id: int | None = None, limit: int = 10) -> list[OdooQuote]:
        domain = []
        if partner_id:
            domain.append(["partner_id", "=", partner_id])
        return self.connector.get_quotes(domain=domain, limit=limit)

    def create_lead(self, name: str, email: str | None = None, phone: str | None = None, description: str | None = None) -> int:
        data = {"name": name, "type": "opportunity"}
        if email:
            data["email_from"] = email
        if phone:
            data["phone"] = phone
        if description:
            data["description"] = description
        return self.connector.create_lead(data)

    def update_lead(self, lead_id: int, data: dict[str, Any]) -> bool:
        return self.connector.update_lead(lead_id, data)

    def log_activity(self, res_model: str, res_id: int, summary: str, activity_type_id: int = 4) -> int:
        # activity_type_id 4 is usually 'Todo' or 'Email' in Odoo, should be configurable in a real app
        data = {
            "res_model": res_model,
            "res_id": res_id,
            "summary": summary,
            "activity_type_id": activity_type_id
        }
        return self.connector.create_activity(data)

    def schedule_meeting(self, name: str, start: str, stop: str, partner_ids: list[int]) -> int:
        data = {
            "name": name,
            "start": start,
            "stop": stop,
            "partner_ids": [[6, 0, partner_ids]]  # Odoo Many2many syntax
        }
        return self.connector.schedule_meeting(data)

    def get_dashboard(self) -> OdooSalesDashboard:
        return self.connector.get_sales_dashboard()
