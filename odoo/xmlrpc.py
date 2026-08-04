import xmlrpc.client
from typing import List, Dict, Any, Optional
import socket

from config.settings import Settings
from core.exceptions import OdooAuthError, OdooConnectionError, OdooConnectorError
from core.logger import get_logger
from core.context import get_current_workspace
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

logger = get_logger(__name__)


class XmlRpcOdooConnector(OdooConnectorInterface):
    """
    Odoo Connector implementation using the XML-RPC protocol.
    Provides typed methods and robust error translation.
    """

    def __init__(self, settings: Settings = None):
        # We no longer cache credentials globally since this is a multi-tenant application.
        # Credentials will be fetched dynamically via get_current_workspace() on each request.
        pass

    @property
    def url(self) -> str:
        return str(get_current_workspace().odoo_url).rstrip("/")

    @property
    def db(self) -> str:
        return get_current_workspace().odoo_db

    @property
    def username(self) -> str:
        return get_current_workspace().odoo_username

    @property
    def password(self) -> str:
        return get_current_workspace().odoo_password

    @property
    def common(self):
        return xmlrpc.client.ServerProxy(f"{self.url}/xmlrpc/2/common")

    @property
    def models(self):
        return xmlrpc.client.ServerProxy(f"{self.url}/xmlrpc/2/object")

    def _authenticate(self) -> int:
        """Authenticate and get user ID dynamically for the current tenant."""
        try:
            uid = self.common.authenticate(self.db, self.username, self.password, {})
            if not uid:
                raise OdooAuthError(f"Authentication failed for user {self.username} on database {self.db}")
            logger.info("Successfully authenticated with Odoo via XML-RPC for tenant", db=self.db)
            return uid
        except (xmlrpc.client.ProtocolError, xmlrpc.client.Fault, socket.error) as e:
            logger.error("Odoo authentication exception", error=str(e))
            raise OdooConnectionError(f"Failed to connect or authenticate with Odoo: {str(e)}") from e

    def _execute(self, model: str, method: str, *args, **kwargs) -> Any:
        """Execute a method on an Odoo model."""
        uid = self._authenticate()
        try:
            return self.models.execute_kw(self.db, uid, self.password, model, method, args, kwargs)
        except (xmlrpc.client.ProtocolError, xmlrpc.client.Fault, socket.error) as e:
            logger.error("Odoo execute_kw exception", model=model, method=method, error=str(e))
            raise OdooConnectorError(f"Error executing {method} on {model}: {str(e)}") from e

    def get_leads(self, domain: Optional[List[Any]] = None, limit: int = 100) -> List[OdooLead]:
        domain = domain or []
        records = self._execute(
            "crm.lead", "search_read",
            domain,
            fields=["name", "email_from", "phone", "partner_id", "stage_id", "expected_revenue", "probability", "description"],
            limit=limit
        )
        return [OdooLead(**record) for record in records]

    def create_lead(self, data: Dict[str, Any]) -> int:
        record_id = self._execute("crm.lead", "create", [data])
        return record_id

    def update_lead(self, lead_id: int, data: Dict[str, Any]) -> bool:
        result = self._execute("crm.lead", "write", [[lead_id], data])
        return bool(result)

    def delete_lead(self, lead_id: int) -> bool:
        result = self._execute("crm.lead", "unlink", [[lead_id]])
        return bool(result)

    def search_contacts(self, domain: Optional[List[Any]] = None, limit: int = 100) -> List[OdooContact]:
        domain = domain or []
        records = self._execute(
            "res.partner", "search_read",
            domain,
            fields=["name", "email", "phone", "is_company", "company_id"],
            limit=limit
        )
        return [OdooContact(**record) for record in records]

    def get_products(self, domain: Optional[List[Any]] = None, limit: int = 100) -> List[OdooProduct]:
        domain = domain or []
        records = self._execute(
            "product.product", "search_read",
            domain,
            fields=["name", "list_price", "default_code", "qty_available"],
            limit=limit
        )
        return [OdooProduct(**record) for record in records]

    def get_quotes(self, domain: Optional[List[Any]] = None, limit: int = 100) -> List[OdooQuote]:
        domain = domain or []
        # In Odoo, sale.order handles both quotes and confirmed orders
        records = self._execute(
            "sale.order", "search_read",
            domain,
            fields=["name", "partner_id", "state", "amount_total", "date_order"],
            limit=limit
        )
        return [OdooQuote(**record) for record in records]

    def create_activity(self, data: Dict[str, Any]) -> int:
        record_id = self._execute("mail.activity", "create", [data])
        return record_id

    def schedule_meeting(self, data: Dict[str, Any]) -> int:
        record_id = self._execute("calendar.event", "create", [data])
        return record_id

    def get_sales_dashboard(self) -> OdooSalesDashboard:
        # A simple dashboard implementation by aggregating data from Odoo
        # 1. Active Leads Count (probability < 100 and > 0, typical for 'active' but not won/lost)
        # 2. Quotes count
        # 3. Total revenue from Won sale orders
        
        active_leads = self._execute("crm.lead", "search_count", [["type", "=", "opportunity"]])
        quotes = self._execute("sale.order", "search_count", [["state", "in", ["draft", "sent"]]])
        
        # Calculate win rate and total revenue from sale.order
        won_orders = self._execute(
            "sale.order", "search_read",
            [["state", "in", ["sale", "done"]]],
            fields=["amount_total"]
        )
        total_revenue = sum(order.get("amount_total", 0.0) for order in won_orders)
        
        all_orders_count = self._execute("sale.order", "search_count", [])
        win_rate = (len(won_orders) / all_orders_count * 100.0) if all_orders_count > 0 else 0.0

        return OdooSalesDashboard(
            total_revenue=total_revenue,
            active_leads_count=active_leads,
            quotes_count=quotes,
            win_rate_percentage=win_rate
        )
