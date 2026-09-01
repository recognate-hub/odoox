import time
from typing import Any, Dict, Optional
import httpx
import requests

from config.settings import get_settings
from core.logger import get_logger

logger = get_logger(__name__)


class UltronService:
    """
    Client service for interacting with the ULTRON Autonomous Failed-Payment Recovery engine.
    Supports both asynchronous (FastAPI/MCP) and synchronous (Odoo model/script) execution.
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        timeout: float = 5.0,
    ):
        settings = get_settings()
        self.base_url = (base_url or settings.ULTRON_API_URL or "http://localhost:3001").rstrip("/")
        self.api_key = api_key or settings.ULTRON_API_KEY or ""
        self.timeout = timeout

    @property
    def headers(self) -> Dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def _build_payload(
        self,
        payment_id: str,
        order_id: str,
        amount_paise: int,
        currency: str = "INR",
        reason_code: str = "PAYMENT_FAILED",
        customer_id: Optional[str] = None,
        customer_email: Optional[str] = None,
        customer_phone: Optional[str] = None,
        event_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Construct a validated event payload for ULTRON /v1/events."""
        evt_id = event_id or f"evt_odoo_{payment_id}_{int(time.time())}"
        return {
            "event_id": evt_id,
            "event_type": "payment.failed",
            "payment_id": payment_id,
            "order_id": order_id,
            "amount_paise": int(amount_paise),
            "currency": currency or "INR",
            "reason_code": reason_code or "PAYMENT_FAILED",
            "customer_id": customer_id,
            "customer_email": customer_email,
            "customer_phone": customer_phone,
        }

    async def ingest_failed_payment(
        self,
        payment_id: str,
        order_id: str,
        amount_paise: int,
        currency: str = "INR",
        reason_code: str = "PAYMENT_FAILED",
        customer_id: Optional[str] = None,
        customer_email: Optional[str] = None,
        customer_phone: Optional[str] = None,
        event_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Asynchronously sends a failed payment event from Odoo/OdooX to ULTRON's /v1/events.
        """
        payload = self._build_payload(
            payment_id=payment_id,
            order_id=order_id,
            amount_paise=amount_paise,
            currency=currency,
            reason_code=reason_code,
            customer_id=customer_id,
            customer_email=customer_email,
            customer_phone=customer_phone,
            event_id=event_id,
        )

        url = f"{self.base_url}/v1/events"
        logger.info(f"Ingesting failed payment event {payload['event_id']} to ULTRON ({url})")

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                resp = await client.post(url, json=payload, headers=self.headers)
                resp.raise_for_status()
                data = resp.json()
                logger.info(f"Successfully ingested event to ULTRON: {data}")
                return data
            except httpx.HTTPStatusError as exc:
                logger.warning(
                    f"ULTRON returned HTTP {exc.response.status_code}: {exc.response.text}"
                )
                raise
            except Exception as exc:
                logger.error(f"Failed to connect to ULTRON control plane: {exc}")
                raise

    def ingest_failed_payment_sync(
        self,
        payment_id: str,
        order_id: str,
        amount_paise: int,
        currency: str = "INR",
        reason_code: str = "PAYMENT_FAILED",
        customer_id: Optional[str] = None,
        customer_email: Optional[str] = None,
        customer_phone: Optional[str] = None,
        event_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Synchronously sends a failed payment event to ULTRON. Useful for Odoo models.
        """
        payload = self._build_payload(
            payment_id=payment_id,
            order_id=order_id,
            amount_paise=amount_paise,
            currency=currency,
            reason_code=reason_code,
            customer_id=customer_id,
            customer_email=customer_email,
            customer_phone=customer_phone,
            event_id=event_id,
        )

        url = f"{self.base_url}/v1/events"
        logger.info(f"Synchronously ingesting event {payload['event_id']} to ULTRON ({url})")
        resp = requests.post(url, json=payload, headers=self.headers, timeout=self.timeout)
        resp.raise_for_status()
        return resp.json()

    async def get_recovery_opportunities(self) -> Dict[str, Any]:
        """Fetch recovery opportunities from ULTRON."""
        url = f"{self.base_url}/v1/opportunities"
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.get(url, headers=self.headers)
            resp.raise_for_status()
            return resp.json()

    def get_recovery_opportunities_sync(self) -> Dict[str, Any]:
        """Fetch recovery opportunities synchronously."""
        url = f"{self.base_url}/v1/opportunities"
        resp = requests.get(url, headers=self.headers, timeout=self.timeout)
        resp.raise_for_status()
        return resp.json()

    async def get_execution_records(self) -> Dict[str, Any]:
        """Fetch generated Razorpay recovery links and execution records from ULTRON."""
        url = f"{self.base_url}/v1/execution/records"
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.get(url, headers=self.headers)
            resp.raise_for_status()
            return resp.json()

    def get_execution_records_sync(self) -> Dict[str, Any]:
        """Fetch generated execution records synchronously."""
        url = f"{self.base_url}/v1/execution/records"
        resp = requests.get(url, headers=self.headers, timeout=self.timeout)
        resp.raise_for_status()
        return resp.json()
