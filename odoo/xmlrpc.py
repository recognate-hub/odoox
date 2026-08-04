import xmlrpc.client
from typing import List, Dict, Any, Optional
import socket

from config.settings import Settings
from core.exceptions import OdooAuthError, OdooConnectionError, OdooConnectorError
from core.logger import get_logger
from core.context import get_current_token, get_workspace_credentials, WorkspaceContext
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
    Provides dynamic credential fetching, auto-recovery on Auth errors, and tenant uid caching.
    """

    def __init__(self, settings: Settings = None):
        # Cache for authenticated uids to avoid redundant auth calls: {token: uid}
        self._uids: Dict[str, int] = {}

    def _get_workspace(self, force_refresh: bool = False) -> WorkspaceContext:
        token = get_current_token()
        return get_workspace_credentials(token, force_refresh=force_refresh)

    def _get_common(self, workspace: WorkspaceContext):
        url = str(workspace.odoo_url).rstrip("/")
        return xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common")

    def _get_models(self, workspace: WorkspaceContext):
        url = str(workspace.odoo_url).rstrip("/")
        return xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object")

    def _authenticate(self, force_refresh: bool = False) -> int:
        """Authenticate and get user ID dynamically for the current tenant.
        Implements an auto-retry mechanism if authentication fails due to stale cached credentials.
        """
        token = get_current_token()
        
        # If not forcing a refresh and we already authenticated this token, reuse the uid
        if not force_refresh and token in self._uids:
            return self._uids[token]
            
        workspace = self._get_workspace(force_refresh=force_refresh)
        common = self._get_common(workspace)
        
        try:
            uid = common.authenticate(workspace.odoo_db, workspace.odoo_username, workspace.odoo_password, {})
            if not uid:
                # If we haven't forced a refresh yet, try refreshing the credentials from DB
                if not force_refresh:
                    logger.warning("Odoo Auth failed with cached credentials. Forcing refresh from database.")
                    return self._authenticate(force_refresh=True)
                raise OdooAuthError(f"Authentication failed for user {workspace.odoo_username} on database {workspace.odoo_db}")
                
            logger.info("Successfully authenticated with Odoo via XML-RPC for tenant", db=workspace.odoo_db)
            self._uids[token] = uid
            return uid
            
        except (xmlrpc.client.ProtocolError, xmlrpc.client.Fault, socket.error) as e:
            logger.error("Odoo authentication exception", error=str(e))
            raise OdooConnectionError(f"Failed to connect or authenticate with Odoo: {str(e)}") from e

    def _execute(self, model: str, method: str, *args, **kwargs) -> Any:
        """Execute a method on an Odoo model."""
        uid = self._authenticate()
        workspace = self._get_workspace()
        models = self._get_models(workspace)
        
        try:
            return models.execute_kw(workspace.odoo_db, uid, workspace.odoo_password, model, method, args, kwargs)
        except xmlrpc.client.Fault as e:
            # If Odoo throws an Access Denied / Auth fault during execute, we should also try to recover
            if "Access Denied" in str(e) or "AuthenticationError" in str(e):
                logger.warning("Odoo execute_kw failed with Access Denied. Forcing auth refresh.")
                uid = self._authenticate(force_refresh=True)
                workspace = self._get_workspace()
                return models.execute_kw(workspace.odoo_db, uid, workspace.odoo_password, model, method, args, kwargs)
            raise OdooConnectorError(f"Error executing {method} on {model}: {str(e)}") from e
        except (xmlrpc.client.ProtocolError, socket.error) as e:
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
        active_leads = self._execute("crm.lead", "search_count", [["type", "=", "opportunity"]])
        quotes = self._execute("sale.order", "search_count", [["state", "in", ["draft", "sent"]]])
        
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
