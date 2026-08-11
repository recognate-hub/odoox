import pytest
from fastapi import Request, HTTPException
from unittest.mock import patch, MagicMock
from core.auth import get_tenant_context
from core.context import current_token, current_workspace_id

@pytest.mark.asyncio
async def test_get_tenant_context_with_bearer_token():
    scope = {
        "type": "http",
        "headers": [(b"authorization", b"Bearer mytoken")],
        "query_string": b"workspace_id=ws123",
    }
    request = Request(scope)
    
    with patch("core.auth.get_workspace_credentials") as mock_get_creds:
        await get_tenant_context(request)
        
        mock_get_creds.assert_called_once_with("mytoken", "ws123")
        assert current_token.get() == "mytoken"
        assert current_workspace_id.get() == "ws123"

@pytest.mark.asyncio
async def test_get_tenant_context_with_query_token():
    scope = {
        "type": "http",
        "headers": [],
        "query_string": b"token=querytoken&workspace_id=ws456",
    }
    request = Request(scope)
    
    with patch("core.auth.get_workspace_credentials") as mock_get_creds:
        await get_tenant_context(request)
        
        mock_get_creds.assert_called_once_with("querytoken", "ws456")
        assert current_token.get() == "querytoken"
        assert current_workspace_id.get() == "ws456"

@pytest.mark.asyncio
async def test_get_tenant_context_missing_token():
    scope = {
        "type": "http",
        "headers": [],
        "query_string": b"",
    }
    request = Request(scope)
    
    with pytest.raises(HTTPException) as exc_info:
        await get_tenant_context(request)
        
    assert exc_info.value.status_code == 401
    assert "Missing Authorization header" in str(exc_info.value.detail)

@pytest.mark.asyncio
async def test_get_tenant_context_auth_failure():
    scope = {
        "type": "http",
        "headers": [(b"authorization", b"Bearer mytoken")],
        "query_string": b"",
    }
    request = Request(scope)
    
    with patch("core.auth.get_workspace_credentials") as mock_get_creds:
        mock_get_creds.side_effect = Exception("Invalid creds")
        
        with pytest.raises(HTTPException) as exc_info:
            await get_tenant_context(request)
            
        assert exc_info.value.status_code == 401
        assert "Authentication failed" in str(exc_info.value.detail)
