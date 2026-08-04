import json
import time
import urllib.parse

from fastapi import APIRouter, Form, Query, Request
from fastapi.responses import JSONResponse, RedirectResponse

from core.encryption import decrypt, encrypt
from core.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()

# Code Expiry (5 minutes)
CODE_EXPIRY_SEC = 300

@router.get("/authorize")
def authorize(
    request: Request,
    client_id: str = Query(...),
    redirect_uri: str = Query(...),
    response_type: str = Query("code"),
    state: str | None = Query(None)
):
    """
    Standard OAuth 2.0 Authorization Endpoint.
    Redirects to login if unauthenticated.
    Generates a short-lived auth code if authenticated.
    """
    token = request.cookies.get("access_token")
    
    # If the user is not logged in, redirect them to the ODOOX login page
    # passing the current OAuth URL as the `next` parameter so they come back here
    if not token:
        next_url = urllib.parse.quote_plus(str(request.url))
        return RedirectResponse(url=f"/login?next={next_url}", status_code=303)
        
    # If the user is logged in, generate an authorization code.
    # We use a stateless encrypted payload so we don't need a DB table.
    payload = {
        "access_token": token,
        "exp": time.time() + CODE_EXPIRY_SEC
    }
    
    code = encrypt(json.dumps(payload))
    
    # Redirect back to the client application with the code and state
    redirect_with_code = f"{redirect_uri}?code={urllib.parse.quote(code)}"
    if state:
        redirect_with_code += f"&state={urllib.parse.quote(state)}"
        
    return RedirectResponse(url=redirect_with_code, status_code=303)


@router.post("/token")
def token(
    request: Request,
    grant_type: str = Form(...),
    code: str = Form(None),
    client_id: str = Form(None),
    client_secret: str = Form(None),
    redirect_uri: str = Form(None)
):
    """
    Standard OAuth 2.0 Token Endpoint.
    Exchanges the short-lived authorization code for the actual Bearer access_token.
    """
    if grant_type != "authorization_code":
        return JSONResponse(status_code=400, content={"error": "unsupported_grant_type"})
        
    if not code:
        return JSONResponse(status_code=400, content={"error": "invalid_request", "error_description": "code is required"})
        
    try:
        decrypted_raw = decrypt(code)
        if decrypted_raw == code:  # Decryption failed or returned raw
            raise ValueError("Invalid code signature")
            
        payload = json.loads(decrypted_raw)
        
        if time.time() > payload.get("exp", 0):
            return JSONResponse(status_code=400, content={"error": "invalid_grant", "error_description": "code expired"})
            
        access_token = payload.get("access_token")
        if not access_token:
            raise ValueError("Missing access token in payload")
            
        # Return standard OAuth 2.0 response
        return JSONResponse(content={
            "access_token": access_token,
            "token_type": "Bearer",
            "expires_in": 3600  # Generic expiry for the token format
        })
        
    except Exception as e:
        logger.error("OAuth Token Exchange Failed", error=str(e))
        return JSONResponse(status_code=400, content={"error": "invalid_grant", "error_description": "invalid authorization code"})
