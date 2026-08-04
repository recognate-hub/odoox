from fastapi import Request, HTTPException, Depends
from core.supabase import get_supabase
from core.encryption import decrypt
from core.context import WorkspaceContext, current_workspace
from core.logger import get_logger

logger = get_logger(__name__)

async def get_tenant_context(request: Request):
    """
    Dependency to extract the JWT token, authenticate with Supabase,
    and populate the WorkspaceContext for the current request.
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
        # Verify the JWT token by fetching the user profile from Supabase
        supabase = get_supabase(token)
        user_response = supabase.auth.get_user(token)
        if not user_response or not user_response.user:
            raise Exception("Invalid token")
            
        user_id = user_response.user.id
        
        # Fetch the user's workspace config
        workspace_response = supabase.table("user_workspaces").select("*").eq("user_id", user_id).single().execute()
        
        if not workspace_response.data:
            raise HTTPException(status_code=404, detail="Workspace not found for user")
            
        workspace_data = workspace_response.data
        
        # Create and set the context
        workspace = WorkspaceContext(
            odoo_url=workspace_data["odoo_url"],
            odoo_db=workspace_data["odoo_db"],
            odoo_username=workspace_data["odoo_username"],
            odoo_password=decrypt(workspace_data["odoo_password"])
        )
        
        current_workspace.set(workspace)
        logger.info("Tenant context set", user_id=user_id)
        
    except Exception as e:
        logger.error("Tenant Auth Error", error=str(e))
        raise HTTPException(status_code=401, detail="Authentication failed")
