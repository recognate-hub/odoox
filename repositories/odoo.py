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

    def get_active_leads(self, name_query: str | None = None, stage_id: int | None = None, limit: int = 100) -> list[OdooLead]:
        domain: list[Any] = [["type", "=", "opportunity"]]
        if name_query:
            domain.append(["name", "ilike", name_query])
        if stage_id:
            domain.append(["stage_id", "=", stage_id])
        return self.connector.get_leads(domain=domain, limit=limit)

    def get_lead_by_id(self, lead_id: int) -> OdooLead | None:
        domain = [["id", "=", lead_id]]
        leads = self.connector.get_leads(domain=domain, limit=1)
        return leads[0] if leads else None

    def search_contacts_by_name(self, name_query: str, limit: int = 20) -> list[OdooContact]:
        domain = [["name", "ilike", name_query]]
        return self.connector.search_contacts(domain=domain, limit=limit)

    def create_contact(self, name: str, email: str | None = None, phone: str | None = None, is_company: bool = False) -> int:
        data = {"name": name, "is_company": is_company}
        if email:
            data["email"] = email
        if phone:
            data["phone"] = phone
        return self.connector.create_contact(data)


    def search_products(self, query: str, limit: int = 20) -> list[OdooProduct]:
        domain = [["name", "ilike", query]]
        return self.connector.get_products(domain=domain, limit=limit)

    def create_product(self, name: str, list_price: float, default_code: str | None = None, type_code: str = "service") -> int:
        data = {"name": name, "list_price": list_price, "detailed_type": type_code}
        if default_code:
            data["default_code"] = default_code
        return self.connector.create_product(data)


    def get_recent_quotes(self, partner_id: int | None = None, limit: int = 10) -> list[OdooQuote]:
        domain = []
        if partner_id:
            domain.append(["partner_id", "=", partner_id])
        return self.connector.get_quotes(domain=domain, limit=limit)

    def create_quote(self, partner_id: int, order_lines: list[dict]) -> int:
        formatted_lines = []
        for line in order_lines:
            line_dict = {
                "product_id": line["product_id"],
                "product_uom_qty": line["quantity"],
            }
            if line.get("price_unit") is not None:
                line_dict["price_unit"] = line["price_unit"]
            # Odoo uses [0, 0, dict] for creating new related records
            formatted_lines.append([0, 0, line_dict])
            
        data = {
            "partner_id": partner_id,
            "order_line": formatted_lines
        }
        return self.connector.create_quote(data)


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
        data = {
            "model": res_model,
            "res_id": res_id,
            "body": summary,
            "message_type": "comment",
            "subtype_id": 2
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

    def create_invoice(self, partner_id: int, amount: float, description: str) -> int:
        data = {
            "partner_id": partner_id,
            "move_type": "out_invoice",
            "invoice_line_ids": [
                [0, 0, {
                    "name": description,
                    "price_unit": amount,
                    "quantity": 1
                }]
            ]
        }
        return self.connector.create_invoice(data)

    def send_email(self, email_to: str, subject: str, body: str) -> int:
        data = {
            "email_to": email_to,
            "subject": subject,
            "body_html": body,
            "state": "outgoing"
        }
        return self.connector.send_email(data)
