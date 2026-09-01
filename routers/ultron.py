from typing import Any, Dict, Optional
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from core.logger import get_logger
from services.ultron import UltronService

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1/ultron", tags=["ULTRON Recovery"])


class FailedPaymentEventRequest(BaseModel):
    payment_id: str = Field(..., description="Provider reference or transaction ID")
    order_id: str = Field(..., description="Sale order name or reference (e.g., SO00142)")
    amount_paise: int = Field(..., description="Amount in paise (e.g. INR 499.00 -> 49900)")
    currency: str = Field(default="INR", description="ISO currency code (e.g., INR, USD)")
    reason_code: str = Field(default="PAYMENT_FAILED", description="Failure reason code or message")
    customer_id: Optional[str] = Field(default=None, description="Customer partner identifier")
    customer_email: Optional[str] = Field(default=None, description="Customer email address")
    customer_phone: Optional[str] = Field(default=None, description="Customer phone or mobile")
    event_id: Optional[str] = Field(default=None, description="Optional custom idempotent event ID")


@router.post("/events/failed-payment", status_code=status.HTTP_200_OK)
async def ingest_failed_payment_endpoint(payload: FailedPaymentEventRequest) -> Dict[str, Any]:
    """
    Ingest a failed payment event from Odoo into the ULTRON recovery pipeline.
    """
    service = UltronService()
    try:
        result = await service.ingest_failed_payment(
            payment_id=payload.payment_id,
            order_id=payload.order_id,
            amount_paise=payload.amount_paise,
            currency=payload.currency,
            reason_code=payload.reason_code,
            customer_id=payload.customer_id,
            customer_email=payload.customer_email,
            customer_phone=payload.customer_phone,
            event_id=payload.event_id,
        )
        return {"status": "success", "data": result}
    except Exception as e:
        logger.error(f"Failed to ingest payment failure to ULTRON: {e}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"ULTRON ingestion error: {str(e)}",
        )


@router.get("/opportunities", status_code=status.HTTP_200_OK)
async def get_opportunities_endpoint() -> Dict[str, Any]:
    """
    Fetch all active recovery opportunities and IVEN economic scoring from ULTRON.
    """
    service = UltronService()
    try:
        data = await service.get_recovery_opportunities()
        return {"status": "success", "data": data}
    except Exception as e:
        logger.error(f"Failed to fetch ULTRON opportunities: {e}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"ULTRON service error: {str(e)}",
        )


@router.get("/execution-records", status_code=status.HTTP_200_OK)
async def get_execution_records_endpoint() -> Dict[str, Any]:
    """
    Fetch generated Razorpay recovery links and execution statuses from ULTRON.
    """
    service = UltronService()
    try:
        data = await service.get_execution_records()
        return {"status": "success", "data": data}
    except Exception as e:
        logger.error(f"Failed to fetch ULTRON execution records: {e}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"ULTRON service error: {str(e)}",
        )
