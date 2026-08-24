from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from typing import Any, Dict
import os

from core.auth import get_tenant_context
from core.logger import get_logger
from services.alerts import AlertService

logger = get_logger(__name__)

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])

class OdooEventPayload(BaseModel):
    event_type: str
    severity: str = "info"
    message: str
    payload: Dict[str, Any] = {}

# Simple secret key to prevent unauthorized pushing.
# In a real setup, this would be validated via HMAC signature from Odoo.
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "odoox_webhook_secret_key")

@router.post("/odoo/event")
async def receive_odoo_event(
    event: OdooEventPayload, 
    request: Request,
    tenant_ctx = Depends(get_tenant_context)
):
    """
    Receive proactive event triggers from Odoo.
    Requires the X-Webhook-Secret header to match the server configuration.
    Requires standard Authorization header to identify the tenant workspace.
    """
    secret = request.headers.get("X-Webhook-Secret")
    if secret != WEBHOOK_SECRET:
        logger.warning("Unauthorized webhook access attempt.")
        raise HTTPException(status_code=401, detail="Invalid webhook secret")
        
    tenant_db = tenant_ctx.get("odoo_db")
    if not tenant_db:
        raise HTTPException(status_code=400, detail="Tenant context missing DB")
        
    alert_service = AlertService(tenant_db=tenant_db)
    
    alert_id = alert_service.push_alert(
        event_type=event.event_type,
        severity=event.severity,
        message=event.message,
        payload=event.payload
    )
    
    return {"status": "success", "alert_id": alert_id}
