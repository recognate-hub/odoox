from typing import Any, Optional

from core.logger import get_logger
from mcp_app.security import secure_tool
from mcp_app.server import _span, mcp
from services.ultron import UltronService

logger = get_logger(__name__)


@mcp.tool()
@secure_tool()
def notify_ultron_payment_failed(
    payment_id: str,
    order_id: str,
    amount_paise: int,
    currency: str = "INR",
    reason_code: str = "PAYMENT_FAILED",
    customer_id: Optional[str] = None,
    customer_email: Optional[str] = None,
    customer_phone: Optional[str] = None,
    event_id: Optional[str] = None,
) -> dict[str, Any]:
    """
    Trigger the ULTRON autonomous payment recovery pipeline for a failed transaction.
    Computes economic IVEN scoring and initiates Razorpay recovery links.
    
    :param payment_id: Transaction or gateway reference
    :param order_id: Associated Odoo sale order or quotation reference (e.g. SO00142)
    :param amount_paise: Transaction amount in lowest unit (e.g., INR 499.00 -> 49900 paise)
    :param currency: Currency code (e.g. INR)
    :param reason_code: Bank decline code or error reason
    :param customer_id: Customer/Partner ID
    :param customer_email: Customer email address
    :param customer_phone: Customer contact phone number
    :param event_id: Optional idempotent event ID
    """
    with _span("mcp.notify_ultron_payment_failed"):
        service = UltronService()
        result = service.ingest_failed_payment_sync(
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
        return {"status": "success", "result": result}


@mcp.tool()
@secure_tool()
def get_ultron_recovery_opportunities() -> dict[str, Any]:
    """
    Retrieve active failed-payment recovery opportunities and IVEN economic scores from ULTRON.
    """
    with _span("mcp.get_ultron_recovery_opportunities"):
        service = UltronService()
        opportunities = service.get_recovery_opportunities_sync()
        return {"status": "success", "opportunities": opportunities}


@mcp.tool()
@secure_tool()
def get_ultron_recovery_links() -> dict[str, Any]:
    """
    Retrieve generated Razorpay payment recovery links and autonomous execution statuses from ULTRON.
    """
    with _span("mcp.get_ultron_recovery_links"):
        service = UltronService()
        records = service.get_execution_records_sync()
        return {"status": "success", "records": records}
