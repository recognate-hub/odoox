from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

router = APIRouter()

def _get_base_url(request: Request) -> str:
    # Try various headers that proxies might set
    proto = request.headers.get("x-forwarded-proto", "https" if "https" in str(request.url) else "http")
    
    # Try to get the original host
    host = request.headers.get("x-forwarded-host")
    if not host:
        # Some proxies like localhost.run might not set x-forwarded-host, but the original host is in the Host header
        # However, FastAPI's request.headers["host"] might be overwritten.
        # Let's check if there's a 'Forwarded' header (RFC 7239)
        forwarded = request.headers.get("forwarded")
        if forwarded and "host=" in forwarded:
            host_part = [p for p in forwarded.split(";") if p.strip().startswith("host=")]
            if host_part:
                host = host_part[0].split("=")[1].strip('"')
                
    if not host:
        # If all else fails, use the host from the Host header, but strip port if it's 80/443
        host = request.headers.get("host", request.url.hostname)
        
    # Force HTTPS for loca.lt, lhr.life, ngrok
    if host and any(domain in host for domain in ["loca.lt", "lhr.life", "ngrok"]):
        proto = "https"
        
    return f"{proto}://{host}"

@router.get("/.well-known/oauth-protected-resource")
def get_protected_resource_metadata(request: Request):
    """
    RFC 9728: Protected Resource Metadata
    Tells the client where the authorization server is.
    """
    base_url = _get_base_url(request)
    return JSONResponse({
        "resource": base_url,
        "authorization_servers": [base_url]
    })


@router.get("/.well-known/oauth-authorization-server")
def get_authorization_server_metadata(request: Request):
    """
    RFC 8414: Authorization Server Metadata
    Tells the client about OAuth capabilities and endpoints.
    """
    base_url = _get_base_url(request)
    return JSONResponse({
        "issuer": base_url,
        "authorization_endpoint": f"{base_url}/oauth/authorize",
        "token_endpoint": f"{base_url}/oauth/token",
        "registration_endpoint": f"{base_url}/oauth/register",
        "response_types_supported": ["code"],
        "grant_types_supported": ["authorization_code", "refresh_token"],
        "code_challenge_methods_supported": ["S256", "plain"],
        "token_endpoint_auth_methods_supported": ["client_secret_post", "client_secret_basic", "none"]
    })
