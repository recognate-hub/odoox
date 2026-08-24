import os
import time
import xmlrpc.client
from typing import Any

from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from config.settings import Settings, get_settings
from core.cache import redis_client
from core.context import WorkspaceContext, get_current_token, get_workspace_credentials
from core.encryption import decrypt
from core.exceptions import (
    CircuitBreakerOpenError,
    OdooAuthError,
    OdooConnectionError,
    OdooConnectorError,
)
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

try:
    from opentelemetry import trace

    tracer = trace.get_tracer(__name__)
except Exception:
    tracer = None

from contextlib import nullcontext


def _span(name: str):
    if tracer:
        return tracer.start_as_current_span(name)
    return nullcontext()


logger = get_logger(__name__)

import io

import requests

_sessions = {}


def _get_session(use_mtls=False):
    key = "mtls" if use_mtls else "standard"
    if key not in _sessions:
        session = requests.Session()
        if use_mtls:
            settings = get_settings()
            if settings.ODOO_CLIENT_CERT_PATH and settings.ODOO_CLIENT_KEY_PATH:
                if os.path.exists(settings.ODOO_CLIENT_CERT_PATH) and os.path.exists(
                    settings.ODOO_CLIENT_KEY_PATH
                ):
                    session.cert = (
                        settings.ODOO_CLIENT_CERT_PATH,
                        settings.ODOO_CLIENT_KEY_PATH,
                    )
                else:
                    logger.warning(
                        "mTLS certificates not found at specified paths. Falling back to default SSL."
                    )
        _sessions[key] = session
    return _sessions[key]


class RequestsTransport(xmlrpc.client.Transport):
    def __init__(self, protocol="http", timeout=120, use_mtls=False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.protocol = protocol
        self.timeout = timeout
        self.session = _get_session(use_mtls)

    def request(self, host, handler, request_body, verbose=False):
        self.verbose = verbose
        url = f"{self.protocol}://{host}{handler}"
        headers = {"User-Agent": "OdooX-Connector", "Content-Type": "text/xml"}
        try:
            response = self.session.post(
                url, data=request_body, headers=headers, timeout=self.timeout
            )
            response.raise_for_status()
            return self.parse_response(io.BytesIO(response.content))
        except requests.exceptions.RequestException as e:
            raise xmlrpc.client.ProtocolError(url, 500, str(e), {}) from e


def get_transport(url: str, timeout: int = 120):
    protocol = "https" if url.startswith("https:") else "http"
    return RequestsTransport(
        protocol=protocol, timeout=timeout, use_mtls=(protocol == "https")
    )


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
        from core.context import current_workspace_id

        workspace_id = current_workspace_id.get()
        return get_workspace_credentials(
            token, workspace_id=workspace_id, force_refresh=force_refresh
        )

    def _get_common(self, workspace: WorkspaceContext):
        url = str(workspace.odoo_url).rstrip("/")
        settings = get_settings()
        transport = get_transport(url, timeout=settings.ODOO_TIMEOUT)
        return xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common", transport=transport)

    def _get_models(self, workspace: WorkspaceContext):
        url = str(workspace.odoo_url).rstrip("/")
        settings = get_settings()
        transport = get_transport(url, timeout=settings.ODOO_TIMEOUT)
        return xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object", transport=transport)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(
            (OSError, xmlrpc.client.ProtocolError, OdooConnectionError)
        ),
    )
    def _authenticate(self, force_refresh: bool = False) -> int:
        """Authenticate and get user ID dynamically for the current tenant.
        Implements an auto-retry mechanism if authentication fails due to stale cached credentials.
        """
        token = get_current_token()

        # If not forcing a refresh and we already authenticated this token, reuse the uid
        if not force_refresh and redis_client:
            cached_uid = redis_client.get(f"odoo_uid:{token}")
            if cached_uid:
                return int(cached_uid)
        elif not force_refresh and token in self._uids:
            return self._uids[token]

        workspace = self._get_workspace(force_refresh=force_refresh)
        common = self._get_common(workspace)

        with _span("xmlrpc.authenticate") as span:
            try:
                uid = common.authenticate(
                    workspace.odoo_db,
                    workspace.odoo_username,
                    decrypt(workspace.odoo_password),
                    {},
                )
                if not uid:
                    if not force_refresh:
                        logger.warning(
                            "Odoo Auth failed with cached credentials. Forcing refresh from database."
                        )
                        return self._authenticate(force_refresh=True)
                    raise OdooAuthError(
                        f"Authentication failed for user {workspace.odoo_username} on database {workspace.odoo_db}"
                    )

                logger.info(
                    "Successfully authenticated with Odoo via XML-RPC for tenant",
                    db=workspace.odoo_db,
                )
                if redis_client:
                    redis_client.setex(f"odoo_uid:{token}", 86400, str(uid))
                else:
                    self._uids[token] = uid
                return uid

            except (OSError, xmlrpc.client.ProtocolError, xmlrpc.client.Fault) as e:
                if span:
                    span.record_exception(e)
                logger.error("Odoo authentication exception", error=str(e))
                raise OdooConnectionError(
                    f"Failed to connect or authenticate with Odoo: {e!s}"
                ) from e

    def _check_circuit_breaker(self, db_name: str):
        if redis_client:
            failures = redis_client.get(f"cb_fails:{db_name}")
            if failures and int(failures) >= 3:
                raise CircuitBreakerOpenError(
                    f"Circuit breaker open for {db_name}. Too many recent timeouts."
                )
        else:
            if db_name in self._circuit_breakers:
                local_failures, last_failure = self._circuit_breakers[db_name]
                if local_failures >= 3:
                    if time.time() - last_failure < 30:
                        raise CircuitBreakerOpenError(
                            f"Circuit breaker open for {db_name}. Too many recent timeouts."
                        )
                    else:
                        # Half-open state: reset failures to allow a test request
                        self._circuit_breakers[db_name] = (0, time.time())

    def _record_failure(self, db_name: str):
        if redis_client:
            pipe = redis_client.pipeline()
            pipe.incr(f"cb_fails:{db_name}")
            pipe.expire(f"cb_fails:{db_name}", 30)
            pipe.execute()
        else:
            local_failures, _ = self._circuit_breakers.get(db_name, (0, 0))
            self._circuit_breakers[db_name] = (local_failures + 1, time.time())

    def _record_success(self, db_name: str):
        if redis_client:
            redis_client.delete(f"cb_fails:{db_name}")
        else:
            if db_name in self._circuit_breakers:
                del self._circuit_breakers[db_name]

    @retry(
        stop=stop_after_attempt(1),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(
            (OSError, xmlrpc.client.ProtocolError, OdooConnectionError)
        ),
    )
    def _execute(self, model: str, method: str, *args, **kwargs) -> Any:
        """Execute a method on an Odoo model.

        Fault classification:
        - Access Denied / AuthenticationError → refresh credentials and retry once
        - ValidationError / MissingError / UserError → permanent, surface immediately
        - Network errors (OSError, ProtocolError) → retryable via @retry decorator
        """
        
        # --- PHASE 1: ISOLATION LAYER (READ-ONLY) ---
        ALLOWED_METHODS = {
            "search", "read", "search_read", "search_count", 
            "fields_get", "name_search", "default_get", "read_group"
        }
        if method not in ALLOWED_METHODS:
            logger.warning(f"Blocked mutating method '{method}' on model '{model}' due to strict Isolation Layer.")
            from core.exceptions import OdooReadOnlyError
            raise OdooReadOnlyError(
                f"Odoox MCP operates in a strict Read-Only Isolation Layer. Modification method '{method}' on '{model}' is blocked for enterprise data safety."
            )
        # ---------------------------------------------
        
        workspace = self._get_workspace()
        self._check_circuit_breaker(workspace.odoo_db)

        uid = self._authenticate()
        models = self._get_models(workspace)

        with _span(f"xmlrpc.execute.{model}.{method}") as span:
            if span:
                span.set_attribute("odoo.model", model)
                span.set_attribute("odoo.method", method)
                span.set_attribute("odoo.db", workspace.odoo_db)

            try:
                result = models.execute_kw(
                    workspace.odoo_db,
                    uid,
                    decrypt(workspace.odoo_password),
                    model,
                    method,
                    args,
                    kwargs,
                )
                self._record_success(workspace.odoo_db)
                return result
            except xmlrpc.client.Fault as e:
                self._record_success(
                    workspace.odoo_db
                )  # Fault means Odoo responded, not a timeout
                fault_str = str(e)
                if span:
                    span.record_exception(e)

                # ── Retryable: stale credentials ────────────────────────
                if "Access Denied" in fault_str or "AuthenticationError" in fault_str:
                    logger.warning(
                        "Odoo execute_kw failed with Access Denied. Forcing auth refresh."
                    )
                    uid = self._authenticate(force_refresh=True)
                    workspace = self._get_workspace()
                    models = self._get_models(workspace)
                    return models.execute_kw(
                        workspace.odoo_db,
                        uid,
                        decrypt(workspace.odoo_password),
                        model,
                        method,
                        args,
                        kwargs,
                    )

                # ── Permanent: Odoo validation / business logic errors ──
                permanent_markers = (
                    "ValidationError",
                    "MissingError",  # Record deleted mid-request
                    "UserError",  # Business-rule violation
                    "except_orm",  # Legacy Odoo ORM exception
                    "null value in column",  # PostgreSQL NOT NULL constraint
                )
                if any(marker in fault_str for marker in permanent_markers):
                    from core.exceptions import OdooValidationError

                    logger.warning(
                        "Permanent Odoo fault — not retrying",
                        model=model,
                        method=method,
                        fault=fault_str[:300],
                    )
                    raise OdooValidationError(
                        f"Odoo rejected {method} on {model}: {fault_str}"
                    ) from e

                # ── Unknown fault — surface as generic connector error ──
                raise OdooConnectorError(
                    f"Error executing {method} on {model}: {e!s}"
                ) from e
            except (OSError, xmlrpc.client.ProtocolError) as e:
                if span:
                    span.record_exception(e)
                self._record_failure(workspace.odoo_db)
                logger.error(
                    "Odoo execute_kw exception",
                    model=model,
                    method=method,
                    error=str(e),
                )
                raise OdooConnectionError(
                    f"Error executing {method} on {model}: {e!s}"
                ) from e

    def get_leads(
        self, domain: list[Any] | None = None, limit: int = 100
    ) -> list[OdooLead]:
        domain = domain or []
        records = self._execute(
            "crm.lead",
            "search_read",
            domain,
            fields=[
                "name",
                "email_from",
                "phone",
                "partner_id",
                "stage_id",
                "expected_revenue",
                "probability",
                "description",
            ],
            limit=limit,
        )
        return [OdooLead(**record) for record in records]

    def create_lead(self, data: dict[str, Any]) -> int:
        workspace = self._get_workspace()

        def _exec():
            return self._execute("crm.lead", "create", [data])

        return IdempotencyCache.check_or_execute(
            workspace.odoo_db, "create_lead", data, _exec
        )

    def update_lead(self, lead_id: int, data: dict[str, Any]) -> bool:
        result = self._execute("crm.lead", "write", [lead_id], data)
        return bool(result)

    def delete_lead(self, lead_id: int) -> bool:
        result = self._execute("crm.lead", "unlink", [lead_id])
        return bool(result)

    def search_contacts(
        self, domain: list[Any] | None = None, limit: int = 100
    ) -> list[OdooContact]:
        domain = domain or []
        records = self._execute(
            "res.partner",
            "search_read",
            domain,
            fields=["name", "email", "phone", "is_company", "company_id"],
            limit=limit,
        )
        return [OdooContact(**record) for record in records]

    def create_contact(self, data: dict[str, Any]) -> int:
        workspace = self._get_workspace()

        def _exec():
            return self._execute("res.partner", "create", [data])

        return IdempotencyCache.check_or_execute(
            workspace.odoo_db, "create_contact", data, _exec
        )

    def get_products(
        self, domain: list[Any] | None = None, limit: int = 100
    ) -> list[OdooProduct]:
        domain = domain or []
        try:
            records = self._execute(
                "product.product",
                "search_read",
                domain,
                fields=["name", "list_price", "default_code", "qty_available"],
                limit=limit,
            )
            return [OdooProduct(**record) for record in records]
        except OdooConnectorError as e:
            if "product.product" in str(e):
                logger.warning(
                    "Sales/Inventory module not installed (product.product missing). Returning empty products list."
                )
                return []
            raise

    def create_product(self, data: dict[str, Any]) -> int:
        workspace = self._get_workspace()

        def _exec():
            return self._execute("product.product", "create", [data])

        return IdempotencyCache.check_or_execute(
            workspace.odoo_db, "create_product", data, _exec
        )

    def get_quotes(
        self, domain: list[Any] | None = None, limit: int = 100
    ) -> list[OdooQuote]:
        domain = domain or []
        # In Odoo, sale.order handles both quotes and confirmed orders
        try:
            records = self._execute(
                "sale.order",
                "search_read",
                domain,
                fields=["name", "partner_id", "state", "amount_total", "date_order"],
                limit=limit,
            )
            return [OdooQuote(**record) for record in records]
        except OdooConnectorError as e:
            if "sale.order" in str(e):
                logger.warning(
                    "Sales module not installed (sale.order missing). Returning empty quotes list."
                )
                return []
            raise

    def create_quote(self, data: dict[str, Any]) -> int:
        workspace = self._get_workspace()

        def _exec():
            return self._execute("sale.order", "create", [data])

        return IdempotencyCache.check_or_execute(
            workspace.odoo_db, "create_quote", data, _exec
        )

    def create_activity(self, data: dict[str, Any]) -> int:
        workspace = self._get_workspace()

        def _exec():
            return self._execute("mail.message", "create", [data])

        return IdempotencyCache.check_or_execute(
            workspace.odoo_db, "create_activity", data, _exec
        )

    def schedule_meeting(self, data: dict[str, Any]) -> int:
        workspace = self._get_workspace()

        def _exec():
            return self._execute("calendar.event", "create", [data])

        return IdempotencyCache.check_or_execute(
            workspace.odoo_db, "schedule_meeting", data, _exec
        )

    def get_sales_dashboard(self) -> OdooSalesDashboard:
        active_leads = self._execute(
            "crm.lead", "search_count", [["type", "=", "opportunity"]]
        )

        try:
            quotes = self._execute(
                "sale.order", "search_count", [["state", "in", ["draft", "sent"]]]
            )

            won_orders = self._execute(
                "sale.order",
                "search_read",
                [["state", "in", ["sale", "done"]]],
                fields=["amount_total"],
            )
            total_revenue = sum(order.get("amount_total", 0.0) for order in won_orders)

            all_orders_count = self._execute("sale.order", "search_count", [])
            win_rate = (
                (len(won_orders) / all_orders_count * 100.0)
                if all_orders_count > 0
                else 0.0
            )
        except OdooConnectorError as e:
            if "sale.order" in str(e):
                logger.warning(
                    "Sales module not installed (sale.order missing). Dashboard will show 0 for sales metrics."
                )
                quotes = 0
                total_revenue = 0.0
                win_rate = 0.0
            else:
                raise

        return OdooSalesDashboard(
            total_revenue=total_revenue,
            active_leads_count=active_leads,
            quotes_count=quotes,
            win_rate_percentage=win_rate,
        )

    def create_invoice(self, data: dict[str, Any]) -> int:
        workspace = self._get_workspace()

        def _exec():
            return self._execute("account.move", "create", [data])

        return IdempotencyCache.check_or_execute(
            workspace.odoo_db, "create_invoice", data, _exec
        )

    def send_email(self, data: dict[str, Any]) -> int:
        workspace = self._get_workspace()

        def _exec():
            mail_id = self._execute("mail.mail", "create", [data])
            self._execute("mail.mail", "send", [mail_id])
            return mail_id

        return IdempotencyCache.check_or_execute(
            workspace.odoo_db, "send_email", data, _exec
        )

    def search_read_records(
        self,
        model: str,
        domain: list[Any] | None = None,
        fields: list[str] | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        domain = domain or []
        kwargs: dict[str, Any] = {"limit": limit, "offset": offset}
        if fields:
            kwargs["fields"] = fields
        return self._execute(model, "search_read", domain, **kwargs)

    def create_record(self, model: str, data: dict[str, Any]) -> int:
        workspace = self._get_workspace()

        def _exec():
            return self._execute(model, "create", [data])

        # Use idempotency key combining model and create
        return IdempotencyCache.check_or_execute(
            workspace.odoo_db, f"create_{model.replace('.', '_')}", data, _exec
        )

    def create_records(self, model: str, data_list: list[dict[str, Any]]) -> list[int]:
        workspace = self._get_workspace()

        def _exec():
            return self._execute(model, "create", [data_list])

        return self._run_with_retry(_exec, workspace.odoo_db)

    def update_record(self, model: str, record_id: int, data: dict[str, Any]) -> bool:
        result = self._execute(model, "write", [record_id], data)
        return bool(result)

    def get_installed_apps(self) -> list[dict[str, Any]]:
        workspace = self._get_workspace()
        cache_key = f"schema:{workspace.odoo_db}:installed_apps"

        import json

        from core.cache import get_cached_value, set_cached_value

        cached = get_cached_value(cache_key)
        if cached:
            return json.loads(cached)

        # Odoo stores installed modules in ir.module.module
        domain = [["state", "=", "installed"]]
        fields = ["name", "shortdesc", "application"]
        records = self._execute(
            "ir.module.module", "search_read", domain, fields=fields
        )

        set_cached_value(cache_key, json.dumps(records), ttl=86400)  # 24 hours
        return records

    def get_model_fields(self, model: str) -> dict[str, Any]:
        workspace = self._get_workspace()
        cache_key = f"schema:{workspace.odoo_db}:model_fields:{model}"

        import json

        from core.cache import get_cached_value, set_cached_value

        cached = get_cached_value(cache_key)
        if cached:
            return json.loads(cached)

        # fields_get returns a dict of {field_name: field_info}
        attributes = ["string", "type", "help", "selection", "relation"]
        fields_info = self._execute(model, "fields_get", [], attributes)

        set_cached_value(cache_key, json.dumps(fields_info), ttl=86400)  # 24 hours
        return fields_info

    def read_group(
        self, model: str, domain: list[Any], fields: list[str], groupby: list[str], **kwargs
    ) -> list[dict[str, Any]]:
        return self._execute(model, "read_group", domain, fields, groupby, **kwargs)

    def archive_record(self, model: str, record_id: int, archive: bool = True) -> bool:
        result = self._execute(model, "write", [record_id], {"active": not archive})
        return bool(result)

    def get_attachment(self, attachment_id: int) -> dict[str, Any]:
        records = self._execute(
            "ir.attachment",
            "search_read",
            [["id", "=", attachment_id]],
            fields=["name", "datas", "mimetype", "res_model", "res_id"],
            limit=1,
        )
        if not records:
            raise OdooConnectorError(f"Attachment {attachment_id} not found.")
        return records[0]

    def create_attachment(self, data: dict[str, Any]) -> int:
        workspace = self._get_workspace()

        def _exec():
            return self._execute("ir.attachment", "create", [data])

        return IdempotencyCache.check_or_execute(
            workspace.odoo_db, "create_attachment", data, _exec
        )

    def execute_method(
        self,
        model: str,
        method: str,
        args: list[Any] | None = None,
        kwargs: dict[str, Any] | None = None,
    ) -> Any:
        args = args or []
        kwargs = kwargs or {}
        return self._execute(model, method, *args, **kwargs)
