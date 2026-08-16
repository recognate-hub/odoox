from typing import Any

from core.logger import get_logger
from repositories.odoo import OdooRepository

logger = get_logger(__name__)

class ContactsService:
    def __init__(self, odoo_repo: OdooRepository):
        self.odoo = odoo_repo

    def create_contact(self, name: str, email: str | None = None, phone: str | None = None, is_company: bool = False) -> dict[str, Any]:
        contact_id = self.odoo.create_contact(name, email, phone, is_company)
        return {"status": "success", "contact_id": contact_id}
        
    def search_contacts(self, name_query: str) -> list[dict[str, Any]]:
        contacts = self.odoo.search_contacts_by_name(name_query)
        return [c.model_dump() for c in contacts]
