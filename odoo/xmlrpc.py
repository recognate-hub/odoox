import os
import ssl
import time
import xmlrpc.client
from typing import Any

from config.settings import Settings, get_settings
from core.context import WorkspaceContext, get_current_token, get_workspace_credentials
from core.encryption import decrypt
from core.exceptions import OdooAuthError, OdooConnectionError, OdooConnectorError
from core.idempotency import IdempotencyCache
from core.logger import get_logger
from odoo.interface import OdooConnectorInterface
from schemas.odoo import (
    OdooContact,
    OdooLead,
    OdooProduct,
    OdooQuote,
    OdooSalesDashboard,
)

logger = get_logger(__name__)

class TimeoutTransport(xmlrpc.client.Transport):
    def __init__(self, timeout=10, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.timeout = timeout

    def make_connection(self, host):
        conn = super().make_connection(host)
        conn.timeout = self.timeout
        return conn

class TimeoutSafeTransport(xmlrpc.client.SafeTransport):
    def __init__(self, timeout=10, *args, **kwargs):
        settings = get_settings()
        if settings.ODOO_CLIENT_CERT_PATH and settings.ODOO_CLIENT_KEY_PATH:
            if os.path.exists(settings.ODOO_CLIENT_CERT_PATH) and os.path.exists(settings.ODOO_CLIENT_KEY_PATH):
                context = ssl.create_default_context()
                context.load_cert_chain(
                    certfile=settings.ODOO_CLIENT_CERT_PATH,
                    keyfile=settings.ODOO_CLIENT_KEY_PATH
                )
                kwargs["context"] = context
            else:
                logger.warning("mTLS certificates not found at specified paths. Falling back to default SSL context.")
                
        super().__init__(*args, **kwargs)
        self.timeout = timeout

    def make_connection(self, host):
        conn = super().make_connection(host)
        conn.timeout = self.timeout
        return conn

def get_transport(url: str, timeout: int = 10):
    if url.startswith("https:"):
        return TimeoutSafeTransport(timeout=timeout)
    return TimeoutTransport(timeout=timeout)


class XmlRpcOdooConnector(OdooConnectorInterface):
    """
    Odoo Connector implementation using the XML-RPC protocol.
    Provides dynamic credential fetching, auto-recovery on Auth errors, and tenant uid caching.
    """

    def __init__(self, settings: Settings | None = None):
        # Cache for authenticated uids to avoid redundant auth calls: {token: uid}
        self._uids: dict[str, int] = {}
        # Circuit Breaker state: {tenant_db: (failures, last_failure_time)}
        self._circuit_breakers: dict[str, tuple[int, float]] = {}


    def _get_workspace(self, force_refresh: bool = False) -> WorkspaceContext:
        token = get_current_token()
        return get_workspace_credentials(token, force_refresh=force_refresh)

    def _get_common(self, workspace: WorkspaceContext):
        url = str(workspace.odoo_url).rstrip("/")
        transport = get_transport(url, timeout=10)
        return xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common", transport=transport)

    def _get_models(self, workspace: WorkspaceContext):
        url = str(workspace.odoo_url).rstrip("/")
        transport = get_transport(url, timeout=10)
        return xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object", transport=transport)

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
            uid = common.authenticate(workspace.odoo_db, workspace.odoo_username, decrypt(workspace.odoo_password), {})
            if not uid:
                # If we haven't forced a refresh yet, try refreshing the credentials from DB
                if not force_refresh:
                    logger.warning("Odoo Auth failed with cached credentials. Forcing refresh from database.")
                    return self._authenticate(force_refresh=True)
                raise OdooAuthError(f"Authentication failed for user {workspace.odoo_username} on database {workspace.odoo_db}")
                
            logger.info("Successfully authenticated with Odoo via XML-RPC for tenant", db=workspace.odoo_db)
            self._uids[token] = uid
            return uid
            
        except (OSError, xmlrpc.client.ProtocolError, xmlrpc.client.Fault) as e:
            logger.error("Odoo authentication exception", error=str(e))
            raise OdooConnectionError(f"Failed to connect or authenticate with Odoo: {e!s}") from e

    def _check_circuit_breaker(self, db_name: str):
        if db_name in self._circuit_breakers:
            failures, last_failure = self._circuit_breakers[db_name]
            if failures >= 5:
                if time.time() - last_failure < 30:
                    raise OdooConnectionError(f"Circuit breaker open for {db_name}. Too many recent timeouts.")
                else:
                    # Half-open state: reset failures to allow a test request
                    self._circuit_breakers[db_name] = (0, time.time())

    def _record_failure(self, db_name: str):
        failures, _ = self._circuit_breakers.get(db_name, (0, 0))
        self._circuit_breakers[db_name] = (failures + 1, time.time())

    def _record_success(self, db_name: str):
        if db_name in self._circuit_breakers:
            del self._circuit_breakers[db_name]

    def _execute(self, model: str, method: str, *args, **kwargs) -> Any:
        """Execute a method on an Odoo model."""
        workspace = self._get_workspace()
        self._check_circuit_breaker(workspace.odoo_db)
        
        uid = self._authenticate()
        models = self._get_models(workspace)
        
        try:
            result = models.execute_kw(workspace.odoo_db, uid, decrypt(workspace.odoo_password), model, method, args, kwargs)
            self._record_success(workspace.odoo_db)
            return result
        except xmlrpc.client.Fault as e:
            self._record_success(workspace.odoo_db) # Fault means Odoo responded, not a timeout
            # If Odoo throws an Access Denied / Auth fault during execute, we should also try to recover
            if "Access Denied" in str(e) or "AuthenticationError" in str(e):
                logger.warning("Odoo execute_kw failed with Access Denied. Forcing auth refresh.")
                uid = self._authenticate(force_refresh=True)
                workspace = self._get_workspace()
                return models.execute_kw(workspace.odoo_db, uid, decrypt(workspace.odoo_password), model, method, args, kwargs)
            raise OdooConnectorError(f"Error executing {method} on {model}: {e!s}") from e
        except (OSError, xmlrpc.client.ProtocolError) as e:
            self._record_failure(workspace.odoo_db)
            logger.error("Odoo execute_kw exception", model=model, method=method, error=str(e))
            raise OdooConnectionError(f"Error executing {method} on {model}: {e!s}") from e

    def get_leads(self, domain: list[Any] | None = None, limit: int = 100) -> list[OdooLead]:
        domain = domain or []
        records = self._execute(
            "crm.lead", "search_read",
            domain,
            fields=["name", "email_from", "phone", "partner_id", "stage_id", "expected_revenue", "probability", "description"],
            limit=limit
        )
        return [OdooLead(**record) for record in records]

    def create_lead(self, data: dict[str, Any]) -> int:
        workspace = self._get_workspace()
        def _exec():
            return self._execute("crm.lead", "create", [data])
        return IdempotencyCache.check_or_execute(workspace.odoo_db, "create_lead", data, _exec)

    def update_lead(self, lead_id: int, data: dict[str, Any]) -> bool:
        result = self._execute("crm.lead", "write", [[lead_id], data])
        return bool(result)

    def delete_lead(self, lead_id: int) -> bool:
        result = self._execute("crm.lead", "unlink", [[lead_id]])
        return bool(result)

    def search_contacts(self, domain: list[Any] | None = None, limit: int = 100) -> list[OdooContact]:
        domain = domain or []
        records = self._execute(
            "res.partner", "search_read",
            domain,
            fields=["name", "email", "phone", "is_company", "company_id"],
            limit=limit
        )
        return [OdooContact(**record) for record in records]

    def get_products(self, domain: list[Any] | None = None, limit: int = 100) -> list[OdooProduct]:
        domain = domain or []
        records = self._execute(
            "product.product", "search_read",
            domain,
            fields=["name", "list_price", "default_code", "qty_available"],
            limit=limit
        )
        return [OdooProduct(**record) for record in records]

    def get_quotes(self, domain: list[Any] | None = None, limit: int = 100) -> list[OdooQuote]:
        domain = domain or []
        # In Odoo, sale.order handles both quotes and confirmed orders
        records = self._execute(
            "sale.order", "search_read",
            domain,
            fields=["name", "partner_id", "state", "amount_total", "date_order"],
            limit=limit
        )
        return [OdooQuote(**record) for record in records]

    def create_activity(self, data: dict[str, Any]) -> int:
        workspace = self._get_workspace()
        def _exec():
            return self._execute("mail.activity", "create", [data])
        return IdempotencyCache.check_or_execute(workspace.odoo_db, "create_activity", data, _exec)

    def schedule_meeting(self, data: dict[str, Any]) -> int:
        workspace = self._get_workspace()
        def _exec():
            return self._execute("calendar.event", "create", [data])
        return IdempotencyCache.check_or_execute(workspace.odoo_db, "schedule_meeting", data, _exec)

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
