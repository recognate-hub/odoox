from fastapi import Request, HTTPException, Depends
from core.context import current_token, get_workspace_credentials
from core.logger import get_logger

logger = get_logger(__name__)

async def get_tenant_context(request: Request):
    """
    Dependency to extract the JWT token, validate it by fetching the workspace,
    and populate the current_token for the current request context.
    """
    auth_header = request.headers.get("Authorization")
    token = None
    
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
    else:
        token = request.query_params.get("token")
        
    if not token:
        raise HTTPException(status_code=401, detail="Missing Authorization header or token query parameter")
    
    try:
        # Pre-warm the cache and validate the token immediately
        get_workspace_credentials(token)
        
        # Set the token in context for the lifetime of this SSE connection
        current_token.set(token)
        
    except Exception as e:
        logger.error("Tenant Auth Error", error=str(e))
        raise HTTPException(status_code=401, detail="Authentication failed")
