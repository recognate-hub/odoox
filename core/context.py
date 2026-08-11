import contextvars
import time

from fastapi import HTTPException
from pydantic import BaseModel

from core.cache import get_cached_workspace, set_cached_workspace
from core.logger import get_logger
from core.supabase import get_supabase

logger = get_logger(__name__)

class WorkspaceContext(BaseModel):
    odoo_url: str
    odoo_db: str
    odoo_username: str
    odoo_password: str
    user_id: str
    role: str = "Admin"  # Per-workspace RBAC role (Admin, Sales, Manager, Support)

# Context variable to hold the current request's JWT token
current_token: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "current_token", default=None
)
current_workspace_id: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "current_workspace_id", default=None
)

# In-memory TTL Cache: { (token, workspace_id): (WorkspaceContext, timestamp) }
_credentials_cache: dict[tuple[str, str | None], tuple[WorkspaceContext, float]] = {}
CACHE_TTL_SEC = 300  # 5 minutes

def get_current_token() -> str:
    token = current_token.get()
    if not token:
        raise RuntimeError("No auth token is currently active in context.")
    return token

def get_workspace_credentials(token: str, workspace_id: str | None = None, force_refresh: bool = False) -> WorkspaceContext:
    """Fetch credentials dynamically with an auto-refreshing TTL cache."""
    now = time.time()
    cache_key = (token, workspace_id)
    
    # Return from cache if valid and not forcing a refresh
    if not force_refresh:
        # Note: Redis cache currently doesn't support workspace_id keying easily unless we change the key format.
        # We'll skip redis for multi-workspace for now and rely on in-memory, or append workspace_id to token.
        redis_key = f"{token}:{workspace_id}" if workspace_id else token
        cached_workspace = get_cached_workspace(redis_key, WorkspaceContext)
        if cached_workspace:
            return cached_workspace
            
        # Fallback to in-memory TTL cache
        if cache_key in _credentials_cache:
            cached_workspace, timestamp = _credentials_cache[cache_key]
            if now - timestamp < CACHE_TTL_SEC:
                return cached_workspace
            
    # Stateless API Key support (Permanent Tokens)
    if token.startswith("odx_"):
        try:
            # Check if key is revoked — Redis cache first, then Supabase fallback
            from core.cache import get_cached_value, set_cached_value
            revoked_cache_key = f"revoked:{token[:64]}"  # Truncate for Redis key length
            cached_revocation = get_cached_value(revoked_cache_key)
            
            if cached_revocation == "1":
                logger.warning("Revoked API Key attempt (cached)", token=token[:20])
                raise HTTPException(status_code=401, detail="API Key has been revoked")
            
            if cached_revocation != "0":  # Not cached yet — check Supabase
                supabase_admin = get_supabase()
                try:
                    revoked_resp = supabase_admin.table("revoked_api_keys").select("id").eq("api_key", token).limit(1).execute()
                    if revoked_resp.data:
                        set_cached_value(revoked_cache_key, "1", ttl=86400)  # Cache for 24h
                        logger.warning("Revoked API Key attempt", token=token[:20])
                        raise HTTPException(status_code=401, detail="API Key has been revoked")
                    else:
                        set_cached_value(revoked_cache_key, "0", ttl=300)  # Cache "not revoked" for 5 min
                except Exception as db_err:
                    if "PGRST205" in str(db_err) or "does not exist" in str(db_err).lower():
                        logger.warning("revoked_api_keys table missing, skipping revocation check")
                        set_cached_value(revoked_cache_key, "0", ttl=300)
                    else:
                        raise

            from core.encryption import decrypt
            decrypted_json = decrypt(token[4:])
            workspace = WorkspaceContext.model_validate_json(decrypted_json)
            # Cache it anyway to save parsing time later
            _credentials_cache[cache_key] = (workspace, now)
            redis_key = f"{token}:{workspace_id}" if workspace_id else token
            set_cached_workspace(redis_key, workspace, ttl=CACHE_TTL_SEC)
            return workspace
        except HTTPException:
            raise
        except Exception as e:
            logger.error("Invalid API Key format", error=str(e))
            raise HTTPException(status_code=401, detail="Invalid API Key")

    # Fetch from Supabase (Standard JWT Auth)
    try:
        supabase = get_supabase(token)
        user_response = supabase.auth.get_user(token)
        if not user_response or not user_response.user:
            raise Exception("Invalid token")
            
        user_id = user_response.user.id
        
        query = supabase.table("user_workspaces").select("*").eq("user_id", user_id)
        if workspace_id:
            query = query.eq("id", workspace_id)
            
        workspace_response = query.limit(1).execute()
        
        if not workspace_response.data or len(workspace_response.data) == 0:
            raise HTTPException(status_code=404, detail="Workspace not found for user")
            
        from typing import Any, cast
        workspace_data = cast(dict[str, Any], workspace_response.data[0])
        
        workspace = WorkspaceContext(
            odoo_url=workspace_data["odoo_url"],
            odoo_db=workspace_data["odoo_db"],
            odoo_username=workspace_data["odoo_username"],
            odoo_password=workspace_data["odoo_password"],
            user_id=user_id,
            role=workspace_data.get("role", "Admin")  # Per-workspace RBAC role
        )
        
        # Update caches
        _credentials_cache[cache_key] = (workspace, now)
        redis_key = f"{token}:{workspace_id}" if workspace_id else token
        set_cached_workspace(redis_key, workspace, ttl=CACHE_TTL_SEC)
        
        logger.info("Fetched fresh credentials from database", user_id=user_id, workspace_id=workspace_id)
        return workspace
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error fetching dynamic workspace credentials", error=str(e))
        raise HTTPException(status_code=401, detail=f"Could not fetch workspace credentials: {e!s}")
