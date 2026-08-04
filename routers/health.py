from fastapi import APIRouter
from pydantic import BaseModel
from config.settings import get_settings
from odoo.xmlrpc import XmlRpcOdooConnector

router = APIRouter()

class HealthResponse(BaseModel):
    status: str
    odoo_connected: bool
    claude_connected: bool
    config_valid: bool

@router.get("/health", response_model=HealthResponse)
def health_check():
    """Endpoint to report overall system health and connectivity."""
    settings = get_settings()
    odoo_ok = False
    claude_ok = False
    config_ok = True
    
    try:
        settings.validate_config()
    except Exception:
        config_ok = False
        
    try:
        odoo = XmlRpcOdooConnector(settings)
        odoo._authenticate()
        odoo_ok = True
    except Exception:
        pass
        
    # For Claude, if config is ok, we assume API key is set.
    # To avoid API latency and costs, we skip generating a real response here.
    claude_ok = config_ok and bool(settings.ANTHROPIC_API_KEY)
        
    return HealthResponse(
        status="ok" if (odoo_ok and config_ok) else "degraded",
        odoo_connected=odoo_ok,
        claude_connected=claude_ok,
        config_valid=config_ok
    )
