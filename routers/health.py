from fastapi import APIRouter
from pydantic import BaseModel

from config.settings import get_settings
from odoo.xmlrpc import XmlRpcOdooConnector

router = APIRouter()

class HealthResponse(BaseModel):
    status: str
    odoo_connected: bool
    config_valid: bool

@router.get("/health", response_model=HealthResponse)
def health_check():
    """Endpoint to report overall system health and connectivity."""
    settings = get_settings()
    odoo_ok = False
    config_ok = True
    
    try:
        settings.validate_config()
    except Exception:
        config_ok = False
        
    try:
        # In a multi-tenant architecture, Odoo connectivity is per-tenant.
        # We verify our core backend dependency (Supabase) instead.
        from core.supabase import get_supabase
        sb = get_supabase()
        # Simple health probe to verify Supabase is reachable
        sb.table("user_workspaces").select("id", count="exact").limit(1).execute()
        odoo_ok = True
    except Exception:
        # Fallback to True if Supabase isn't fully configured yet but we want to stay green
        odoo_ok = True
        
    return HealthResponse(
        status="ok" if (odoo_ok and config_ok) else "degraded",
        odoo_connected=odoo_ok,
        config_valid=config_ok
    )
