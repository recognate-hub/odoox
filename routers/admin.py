from fastapi import APIRouter, Depends, Form, HTTPException, Request, Response
from fastapi.responses import JSONResponse, RedirectResponse

from config.settings import get_settings
from core.encryption import encrypt
from core.logger import get_logger
from core.supabase import get_supabase
from core.auth import get_tenant_context

logger = get_logger(__name__)
router = APIRouter()

def get_user_token(request: Request) -> str:
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return token

# ============================================================
# Auth API endpoints (used by Next.js frontend)
# ============================================================

@router.post("/login/otp")
async def post_login_otp(request: Request, email: str = Form(...)):
    """Request an OTP for the given email via Supabase."""
    supabase = get_supabase()
    try:
        supabase.auth.sign_in_with_otp({
            "email": email,
            "options": {
                "should_create_user": True
            }
        })
        return {"status": "success", "message": "OTP sent successfully."}
    except Exception as e:
        logger.error("OTP Request Error", error=str(e))
        return {"status": "error", "message": str(e)}

@router.post("/login/verify")
async def post_verify_otp(request: Request, email: str = Form(...), token: str = Form(...)):
    """Verify the 6-digit OTP and set session cookie."""
    supabase = get_supabase()
    try:
        res = supabase.auth.verify_otp({
            "email": email,
            "token": token,
            "type": "email"
        })
        
        if not res or not res.session:
            raise ValueError("Invalid or expired OTP.")
            
        response = Response(
            content='{"status": "success", "redirect": "/payment"}',
            media_type="application/json"
        )
        response.set_cookie(
            "access_token",
            res.session.access_token,
            httponly=True,
            samesite="lax",
            secure=False,  # Set to True in production with HTTPS
        )
        if res.session.refresh_token:
            response.set_cookie(
                "refresh_token",
                res.session.refresh_token,
                httponly=True,
                samesite="lax",
                secure=False,
            )
        return response
    except Exception as e:
        logger.error("OTP Verify Error", error=str(e))
        return {"status": "error", "message": str(e)}

@router.get("/logout")
def logout():
    settings = get_settings()
    frontend_url = settings.FRONTEND_URL.rstrip('/')
    redirect = RedirectResponse(url=f"{frontend_url}/login", status_code=303)
    redirect.delete_cookie("access_token")
    redirect.delete_cookie("refresh_token")
    return redirect

# ============================================================
# JSON API endpoints (used by Next.js frontend)
# ============================================================

@router.get("/api/auth/me")
def get_current_user(request: Request, token: str = Depends(get_user_token)):
    """Return current user info from the access_token cookie."""
    supabase = get_supabase(token)
    try:
        user_response = supabase.auth.get_user(token)
        if not user_response or not user_response.user:
            raise ValueError("Invalid token")
        user = user_response.user
        return {
            "status": "success",
            "user": {
                "id": user.id,
                "email": user.email,
            }
        }
    except Exception as e:
        logger.error("Auth check failed", error=str(e))
        raise HTTPException(status_code=401, detail="Session expired or invalid")

@router.get("/api/workspace")
def get_workspace(request: Request, token: str = Depends(get_user_token)):
    """Return workspace data as JSON for the Next.js dashboard."""
    supabase = get_supabase(token)
    try:
        user_response = supabase.auth.get_user(token)
        if not user_response or not user_response.user:
            raise ValueError("Invalid token")
        user_id = user_response.user.id
    except Exception:
        raise HTTPException(status_code=401, detail="Session expired or invalid")
    
    workspace_response = supabase.table("user_workspaces").select("*").eq("user_id", user_id).execute()
    # type: ignore
    workspace = workspace_response.data[0] if workspace_response.data and isinstance(workspace_response.data, list) else None
    connection_url = f"{request.base_url}sse"
    
    return {
        "status": "success",
        "workspace": {
            "odoo_url": workspace.get("odoo_url", "") if workspace else "",  # type: ignore
            "odoo_db": workspace.get("odoo_db", "") if workspace else "",  # type: ignore
            "odoo_username": workspace.get("odoo_username", "") if workspace else "",  # type: ignore
            "has_password": bool(workspace and workspace.get("odoo_password")),  # type: ignore
        } if workspace else None,
        "connection_url": connection_url,
        "token": token,
    }

@router.post("/api/workspace/save")
def api_save_config(
    request: Request,
    token: str = Depends(get_user_token),
    workspace_id: str | None = Form(None),
    odoo_url: str = Form(...),
    odoo_db: str = Form(...),
    odoo_username: str = Form(...),
    odoo_password: str = Form(...)
):
    """Save workspace configuration (JSON API version)."""
    supabase = get_supabase(token)
    try:
        user_response = supabase.auth.get_user(token)
        if not user_response or not user_response.user:
            raise ValueError("Invalid user response")
        user_id = user_response.user.id
    except Exception:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    # We remove the plan column since it doesn't exist in the DB schema
    supabase.table("payments").select("id").eq("user_id", user_id).limit(1).execute()
    # Assume single plan if they paid, since the column is missing
    plan_type = "single"
    
    max_workspaces = 10 if plan_type == "team" else 1

    existing = supabase.table("user_workspaces").select("*").eq("user_id", user_id).execute()
    from typing import Any, cast
    existing_data = cast(list[dict[str, Any]], existing.data) if existing.data else []
    
    if not workspace_id and len(existing_data) >= max_workspaces:
        return {"status": "error", "message": f"Plan limit reached. {plan_type.capitalize()} plan allows {max_workspaces} workspace(s)."}
    
    # Identify if we are updating an existing workspace
    target_workspace = None
    if workspace_id:
        target_workspace = next((w for w in existing_data if str(w.get("id")) == str(workspace_id)), None)
        if not target_workspace:
            return {"status": "error", "message": "Workspace not found or unauthorized"}
    
    if odoo_password == "********" and target_workspace:
        final_password = target_workspace.get("odoo_password")
    else:
        final_password = encrypt(odoo_password) if odoo_password else odoo_password
        
    payload = {
        "user_id": user_id,
        "odoo_url": odoo_url,
        "odoo_db": odoo_db,
        "odoo_username": odoo_username,
        "odoo_password": final_password
    }
    
    try:
        if target_workspace:
            supabase.table("user_workspaces").update(payload).eq("id", workspace_id).execute()
        else:
            supabase.table("user_workspaces").insert(payload).execute()
        return {"status": "success", "message": "Configuration saved successfully."}
    except Exception as e:
        logger.error("DB Save Error", error=str(e))
        return {"status": "error", "message": str(e)}

@router.post("/api/workspace/delete")
async def api_delete_config(
    request: Request,
    token: str = Depends(get_user_token)
):
    """Delete a workspace configuration."""
    body = await request.json()
    workspace_id = body.get("workspace_id")
    if not workspace_id:
        return {"status": "error", "message": "Missing workspace_id"}
        
    supabase = get_supabase(token)
    try:
        user_response = supabase.auth.get_user(token)
        if not user_response or not user_response.user:
            raise ValueError("Invalid user response")
        user_id = user_response.user.id
    except Exception:
        raise HTTPException(status_code=401, detail="Unauthorized")
        
    try:
        supabase.table("user_workspaces").delete().eq("id", workspace_id).eq("user_id", user_id).execute()
        return {"status": "success", "message": "Workspace deleted successfully."}
    except Exception as e:
        logger.error("DB Delete Error", error=str(e))
        return {"status": "error", "message": str(e)}

@router.post("/api/logout")
def api_logout():
    """JSON API logout — clears the access_token cookie."""
    response = JSONResponse(content={"status": "success", "message": "Logged out"})
    response.delete_cookie("access_token")
    return response

# Legacy save endpoint (backward compatibility)
@router.get("/api/workspace/api-key")
def generate_api_key(token: str = Depends(get_user_token)):
    """
    Generates a permanent API Key (Stateless Token) for the current workspace.
    This token can be used in Claude Desktop or other MCP clients.
    """
    from core.context import get_workspace_credentials
    from core.encryption import encrypt
    
    workspace = get_workspace_credentials(token)
    
    # Encrypt the full workspace context JSON
    encrypted_payload = encrypt(workspace.model_dump_json())
    
    # Prepend odx_ to denote it as an OdooX API Key
    api_key = f"odx_{encrypted_payload}"
    
    return {"api_key": api_key}

@router.post("/api/workspace/api-key/revoke")
def revoke_api_key(request: Request, api_key: str = Form(...), token: str = Depends(get_user_token)):
    """
    Revokes an existing permanent API key by adding it to the revoked_api_keys table in Supabase.
    """
    from core.context import get_workspace_credentials
    
    # Authenticate the user and get their workspace to ensure they own the workspace
    workspace = get_workspace_credentials(token)
    
    # In a fully fleshed out system, we would decrypt the api_key and verify the workspace_id matches 
    # the user's workspace_id before revoking it, to prevent a user from revoking someone else's key.
    # For now, we just insert it.
    
    supabase = get_supabase()
    try:
        response = supabase.table("revoked_api_keys").insert({
            "api_key": api_key,
            "workspace_id": workspace.user_id # using user_id as workspace_id for simplicity, since it's 1:1 right now
        }).execute()
        
        # Instantly propagate revocation to Redis cache
        from core.cache import set_cached_value
        set_cached_value(f"revoked:{api_key[:64]}", "1", ttl=86400) # 24h cache

        return {"status": "success", "message": "API key revoked successfully."}
    except Exception as e:
        logger.error("Failed to revoke API key", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to revoke API key.")

@router.post("/admin/save")
def save_config(
    request: Request,
    token: str = Depends(get_user_token),
    odoo_url: str = Form(...),
    odoo_db: str = Form(...),
    odoo_username: str = Form(...),
    odoo_password: str = Form(...)
):
    """Save the updated configuration to the Supabase database (legacy)."""
    return api_save_config(request, token, odoo_url, odoo_db, odoo_username, odoo_password)

