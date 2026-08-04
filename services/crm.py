from typing import Any

from core.exceptions import OdooResourceNotFoundError
from core.logger import get_logger
from repositories.odoo import OdooRepository

logger = get_logger(__name__)


class CRMService:
    """
    Business logic layer that orchestrates the Odoo Repository.
    Returns raw data structures to the MCP Client.
    """

    def __init__(self, odoo_repo: OdooRepository):
        self.odoo = odoo_repo

    def get_lead_context(self, lead_id: int) -> dict[str, Any]:
        """Fetch a lead from Odoo and return context for analysis."""
        lead = self.odoo.get_lead_by_id(lead_id)
        if not lead:
            raise OdooResourceNotFoundError(f"Lead with ID {lead_id} not found.")

        return lead.model_dump()

    def get_customer_summary_data(self, partner_id: int) -> dict[str, Any]:
        """Fetch customer details and recent quotes."""
        contacts = self.odoo.connector.search_contacts(domain=[["id", "=", partner_id]], limit=1)
        if not contacts:
            raise OdooResourceNotFoundError(f"Contact with ID {partner_id} not found.")
        
        contact = contacts[0]
        quotes = self.odoo.get_recent_quotes(partner_id=partner_id, limit=5)
        
        return {
            "contact": contact.model_dump(),
            "recent_quotes": [q.model_dump() for q in quotes]
        }

    def get_pipeline_data(self) -> list[dict[str, Any]]:
        """Fetch active leads for sales forecasting."""
        leads = self.odoo.get_active_leads(limit=50)
        return [lead.model_dump() for lead in leads]

    def create_meeting(self, name: str, start: str, stop: str, partner_ids: list[int], notes: str) -> dict[str, Any]:
        """Create a meeting in Odoo and log the notes."""
        meeting_id = self.odoo.schedule_meeting(name, start, stop, partner_ids)
        
        # Log the raw notes as an activity in Odoo
        if notes:
            self.odoo.log_activity("calendar.event", meeting_id, f"Meeting Notes: {notes}")
        
        return {
            "status": "success",
            "meeting_id": meeting_id
        }
