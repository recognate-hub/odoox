import time
import contextvars
from pydantic import BaseModel
from typing import Optional, Dict, Tuple
from fastapi import HTTPException
from core.supabase import get_supabase

from core.logger import get_logger

logger = get_logger(__name__)

class WorkspaceContext(BaseModel):
    odoo_url: str
    odoo_db: str
    odoo_username: str
    odoo_password: str
    user_id: str

# Context variable to hold the current request's JWT token
current_token: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    "current_token", default=None
)

# In-memory TTL Cache: { token: (WorkspaceContext, timestamp) }
_credentials_cache: Dict[str, Tuple[WorkspaceContext, float]] = {}
CACHE_TTL_SEC = 300  # 5 minutes

def get_current_token() -> str:
    token = current_token.get()
    if not token:
        raise RuntimeError("No auth token is currently active in context.")
    return token

def get_workspace_credentials(token: str, force_refresh: bool = False) -> WorkspaceContext:
    """Fetch credentials dynamically with an auto-refreshing TTL cache."""
    now = time.time()
    
    # Return from cache if valid and not forcing a refresh
    if not force_refresh and token in _credentials_cache:
        cached_workspace, timestamp = _credentials_cache[token]
        if now - timestamp < CACHE_TTL_SEC:
            return cached_workspace
            
    # Fetch from Supabase
    try:
        supabase = get_supabase(token)
        user_response = supabase.auth.get_user(token)
        if not user_response or not user_response.user:
            raise Exception("Invalid token")
            
        user_id = user_response.user.id
        
        workspace_response = supabase.table("user_workspaces").select("*").eq("user_id", user_id).single().execute()
        
        if not workspace_response.data:
            raise HTTPException(status_code=404, detail="Workspace not found for user")
            
        workspace_data = workspace_response.data
        
        workspace = WorkspaceContext(
            odoo_url=workspace_data["odoo_url"],
            odoo_db=workspace_data["odoo_db"],
            odoo_username=workspace_data["odoo_username"],
            odoo_password=workspace_data["odoo_password"],
            user_id=user_id
        )
        
        # Update cache
        _credentials_cache[token] = (workspace, now)
        logger.info("Fetched fresh credentials from database", user_id=user_id)
        return workspace
        
    except Exception as e:
        logger.error("Error fetching dynamic workspace credentials", error=str(e))
        raise RuntimeError(f"Could not fetch workspace credentials: {str(e)}")
