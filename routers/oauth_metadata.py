from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

router = APIRouter()

@router.get("/.well-known/oauth-protected-resource")
def get_protected_resource_metadata(request: Request):
    """
    RFC 9728: Protected Resource Metadata
    Tells the client where the authorization server is.
    """
    base_url = str(request.base_url).rstrip("/")
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
    base_url = str(request.base_url).rstrip("/")
    return JSONResponse({
        "issuer": base_url,
        "authorization_endpoint": f"{base_url}/oauth/authorize",
        "token_endpoint": f"{base_url}/oauth/token",
        "registration_endpoint": f"{base_url}/oauth/register",
        "response_types_supported": ["code"],
        "grant_types_supported": ["authorization_code"],
        "code_challenge_methods_supported": ["S256", "plain"],
        "token_endpoint_auth_methods_supported": ["client_secret_post", "client_secret_basic", "none"]
    })
