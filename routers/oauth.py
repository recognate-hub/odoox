import json
import time
import urllib.parse

from fastapi import APIRouter, Form, Query, Request
from fastapi.responses import JSONResponse, RedirectResponse
from supabase import create_client

from config.settings import get_settings
from core.context import get_workspace_credentials
from core.encryption import decrypt, encrypt
from core.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()

# Code Expiry (5 minutes)
CODE_EXPIRY_SEC = 300

# How many seconds before the access_token actually expires we tell the client.
# Supabase JWTs are valid for 3600 s. We report 3500 so Claude has time to
# refresh before the token actually expires.
ACCESS_TOKEN_LIFETIME_SEC = 3500

# Supabase refresh tokens are long-lived (weeks). Report a conservative value
# so Claude knows it can hold onto the refresh_token for a long time.
REFRESH_TOKEN_LIFETIME_SEC = 7 * 24 * 3600  # 7 days

@router.get("/authorize")
def authorize(
    request: Request,
    client_id: str = Query(...),
    redirect_uri: str = Query(...),
    response_type: str = Query("code"),
    state: str | None = Query(None),
    token: str | None = Query(None),
    refresh_token: str | None = Query(None)
):
    """
    Standard OAuth 2.0 Authorization Endpoint.
    Redirects to login if unauthenticated.
    Generates a short-lived auth code if authenticated.
    """
    cookie_token = request.cookies.get("access_token")
    cookie_refresh = request.cookies.get("refresh_token")
    
    actual_token = token or cookie_token
    actual_refresh = refresh_token or cookie_refresh
    
    # If the user is not logged in, redirect them to the ODOOX login page
    # passing the current OAuth URL as the `next` parameter so they come back here
    if not actual_token:
        settings = get_settings()
        frontend_url = settings.FRONTEND_URL.rstrip('/')
        
        # Use an absolute URL for the `next` param to ensure we return to the backend.
        # Since Next.js proxies the OAuth endpoints, the backend URL *is* the frontend URL
        # from the perspective of the public internet.
        relative_url = f"{request.url.path}?{request.url.query}" if request.url.query else request.url.path
        absolute_next_url = f"{frontend_url}{relative_url}"
        
        from urllib.parse import quote
        login_url = f"{frontend_url}/oauth/login?next={quote(absolute_next_url)}"
        return RedirectResponse(url=login_url)
        
    # If the user is logged in, generate an authorization code.
    # We use a stateless encrypted payload so we don't need a DB table.
    # Try to read the actual Supabase session expiry from the cookie so we can
    # embed it in the payload (used later to compute expires_in accurately).
    issued_at = int(time.time())
    payload = {
        "access_token": actual_token,
        "refresh_token": actual_refresh,
        "issued_at": issued_at,
        "exp": issued_at + CODE_EXPIRY_SEC
    }
    
    code = encrypt(json.dumps(payload))
    
    # Redirect back to the client application with the code and state
    sep = "&" if "?" in redirect_uri else "?"
    redirect_with_code = f"{redirect_uri}{sep}code={urllib.parse.quote(code)}"
    if state:
        redirect_with_code += f"&state={urllib.parse.quote(state)}"
        
    response = RedirectResponse(url=redirect_with_code, status_code=303)
    if token:
        response.set_cookie("access_token", token, max_age=3600, httponly=True, samesite="lax", secure=True)
    if refresh_token:
        response.set_cookie("refresh_token", refresh_token, max_age=7*24*3600, httponly=True, samesite="lax", secure=True)
    return response


@router.post("/token")
def token(
    request: Request,
    grant_type: str = Form(...),
    code: str | None = Form(None),
    refresh_token: str | None = Form(None),
    client_id: str | None = Form(None),
    client_secret: str | None = Form(None),
    redirect_uri: str | None = Form(None)
):
    """
    Standard OAuth 2.0 Token Endpoint.
    Exchanges the short-lived authorization code for the actual Bearer access_token.
    """
    if grant_type == "refresh_token":
        if not refresh_token:
            return JSONResponse(status_code=400, content={"error": "invalid_request", "error_description": "refresh_token is required"})
        
        try:
            # Our OAuth refresh_token is the encrypted Supabase refresh_token.
            # Decrypt it to get the raw Supabase refresh token.
            try:
                supabase_refresh = decrypt(refresh_token)
            except Exception:
                raise ValueError("Failed to decrypt refresh token")
            if not supabase_refresh or supabase_refresh == refresh_token:
                # decrypt() returns the raw value unchanged when decryption fails;
                # treat that case as an invalid token.
                raise ValueError("Invalid or undecryptable refresh token")
            
            # Use the service-role client for token refresh — this avoids RLS
            # issues that can arise when the old access token has already expired.
            _settings = get_settings()
            admin_client = create_client(_settings.SUPABASE_URL, _settings.SUPABASE_SERVICE_ROLE_KEY)
            res = admin_client.auth.refresh_session(supabase_refresh)
            
            if not res or not res.session:
                raise ValueError("Supabase failed to refresh session")
            
            new_access_token = res.session.access_token
            new_refresh_token = res.session.refresh_token
            
            logger.info("OAuth token refreshed successfully")
            return JSONResponse(content={
                "access_token": new_access_token,
                "token_type": "Bearer",
                "expires_in": ACCESS_TOKEN_LIFETIME_SEC,
                "refresh_token": encrypt(new_refresh_token) if new_refresh_token else refresh_token
            })
        except Exception as e:  # noqa: BLE001
            logger.error("OAuth Token Refresh Failed", error=str(e))
            return JSONResponse(status_code=400, content={"error": "invalid_grant", "error_description": "Token refresh failed. Please re-authenticate."})

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
            
        # Convert the short-lived Supabase JWT into a permanent odx_ API key
        # so Claude Desktop never needs to refresh it. This avoids race conditions
        # with the browser rotating the refresh token.
        workspace = get_workspace_credentials(access_token)
        odx_token = "odx_" + encrypt(workspace.model_dump_json())
        
        # We don't return a refresh_token, and we set a 10 year expiry.
        # This completely eliminates the need for Claude Desktop to refresh the token,
        # solving the "Connection Expired" issues permanently.
        response_body: dict = {
            "access_token": odx_token,
            "token_type": "Bearer",
            "expires_in": 315360000,
        }
        logger.info("OAuth authorization code exchanged for permanent odx_ key")
        return JSONResponse(content=response_body)
        
    except Exception as e:  # noqa: BLE001
        logger.error("OAuth Token Exchange Failed", error=str(e))
        return JSONResponse(status_code=400, content={"error": "invalid_grant", "error_description": "invalid authorization code"})


@router.post("/register")
async def register(request: Request):
    """
    RFC 7591: OAuth 2.0 Dynamic Client Registration
    Allows Claude Desktop or other MCP clients to register dynamically.
    """
    import uuid
    
    try:
        data = await request.json()
    except Exception as e:  # noqa: BLE001
        logger.error(f"Failed to parse registration body: {e}")
        data = {}

    client_id = f"client_{uuid.uuid4().hex}"
    
    auth_method = data.get("token_endpoint_auth_method", "client_secret_basic")

    provided_grant_types = data.get("grant_types", ["authorization_code", "refresh_token"])
    if "refresh_token" not in provided_grant_types:
        provided_grant_types.append("refresh_token")

    response_content = {
        "client_id": client_id,
        "client_id_issued_at": int(time.time()),
        "redirect_uris": data.get("redirect_uris", []),
        "grant_types": provided_grant_types,
        "response_types": data.get("response_types", ["code"]),
        "client_name": data.get("client_name", "Dynamic MCP Client"),
        "token_endpoint_auth_method": auth_method
    }

    response_content["client_secret"] = f"secret_{uuid.uuid4().hex}"
    response_content["client_secret_expires_at"] = 0

    if "scope" in data:
        response_content["scope"] = data["scope"]

    return JSONResponse(
        status_code=201,
        content=response_content
    )
