from fastapi import APIRouter, Depends, Form, HTTPException, Request, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from core.encryption import encrypt
from core.logger import get_logger
from core.supabase import get_supabase

logger = get_logger(__name__)
router = APIRouter()
templates = Jinja2Templates(directory="templates")

def get_user_token(request: Request) -> str:
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=303, headers={"Location": "/login"})
    return token

@router.get("/", response_class=HTMLResponse)
def get_landing_page(request: Request):
    """Render the landing page."""
    return templates.TemplateResponse(request, "index.html", {"request": request})

@router.get("/login", response_class=HTMLResponse)
def get_login(request: Request):
    """Render the login/registration page."""
    return templates.TemplateResponse(request, "login.html", {"request": request, "error": None})

@router.post("/login/otp")
async def post_login_otp(request: Request, email: str = Form(...)):
    """Request an OTP for the given email via Supabase."""
    supabase = get_supabase()
    try:
        # Request OTP using Supabase Auth
        res = supabase.auth.sign_in_with_otp({
            "email": email,
            "options": {
                "should_create_user": True  # Automatically register new users
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
        # Verify the OTP
        res = supabase.auth.verify_otp({
            "email": email,
            "token": token,
            "type": "email"
        })
        
        if not res or not res.session:
            raise Exception("Invalid or expired OTP.")
            
        # Return success with a redirect URL so the frontend can redirect
        response = Response(content='{"status": "success", "redirect": "/admin"}', media_type="application/json")
        response.set_cookie("access_token", res.session.access_token, httponly=True)
        return response
    except Exception as e:
        logger.error("OTP Verify Error", error=str(e))
        return {"status": "error", "message": str(e)}

@router.get("/logout")
def logout():
    redirect = RedirectResponse(url="/login", status_code=303)
    redirect.delete_cookie("access_token")
    return redirect

@router.get("/admin", response_class=HTMLResponse)
def get_admin_dashboard(request: Request, token: str = Depends(get_user_token)):
    """Render the tenant's admin dashboard configuration page."""
    supabase = get_supabase(token)
    
    try:
        user_response = supabase.auth.get_user(token)
        if not user_response or not user_response.user:
            raise Exception("Invalid token")
        user_id = user_response.user.id
    except Exception:
        raise HTTPException(status_code=401, detail="Session expired or invalid")
    
    # Fetch existing workspace from Supabase
    workspace_response = supabase.table("user_workspaces").select("*").eq("user_id", user_id).execute()
    workspace = workspace_response.data[0] if workspace_response.data else None
    
    # Generate the connection URL for Claude Connectors
    connection_url = f"{request.base_url}sse"
    
    return templates.TemplateResponse(request, "admin.html", {
        "request": request, 
        "workspace": workspace,
        "token": token,
        "connection_url": connection_url
    })

@router.post("/admin/save")
def save_config(
    request: Request,
    token: str = Depends(get_user_token),
    odoo_url: str = Form(...),
    odoo_db: str = Form(...),
    odoo_username: str = Form(...),
    odoo_password: str = Form(...)
):
    """Save the updated configuration to the Supabase database."""
    supabase = get_supabase(token)
    try:
        user_response = supabase.auth.get_user(token)
        if not user_response or not user_response.user:
            raise ValueError("Invalid user response")
        user_id = user_response.user.id
    except Exception:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    # Check if exists
    existing = supabase.table("user_workspaces").select("*").eq("user_id", user_id).execute()
    
    if odoo_password == "********" and existing.data:
        from typing import cast, Any
        existing_data = cast(list[dict[str, Any]], existing.data)
        final_password = existing_data[0].get("odoo_password")
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
        if existing.data:
            supabase.table("user_workspaces").update(payload).eq("user_id", user_id).execute()
        else:
            supabase.table("user_workspaces").insert(payload).execute()
        return {"status": "success", "message": "Configuration saved successfully."}
    except Exception as e:
        logger.error("DB Save Error", error=str(e))
        return {"status": "error", "message": str(e)}
