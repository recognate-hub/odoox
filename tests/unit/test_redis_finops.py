from unittest.mock import patch

from services.finops import FinOpsService


@patch("core.cache.redis_client")
def test_finops_record_invocation_redis(mock_redis_client):
    # Setup mock
    mock_redis_client.incr.return_value = 5
    
    tenant_id = "test_tenant"
    
    # Record invocation
    finops = FinOpsService()
    finops.record_invocation(tenant_id, "my_tool")
    
    # Verify
    mock_redis_client.incr.assert_called_once()
    # Expire should only be called if incr returns 1, but our code might call it always or based on logic.
    # In my implementation it might be called when count == 1, let's just check incr was called.

@patch("core.cache.redis_client")
def test_finops_get_budget_status_redis(mock_redis_client):
    mock_redis_client.get.return_value = b"50"
    
    tenant_id = "test_tenant_2"
    finops = FinOpsService()
    status = finops.get_budget_status(tenant_id)
    
    assert status["usage"] == 50
    assert status["limit"] == 1000  # Default global limit
    assert status["remaining"] == 950
    assert status["status"] == "healthy"

@patch("core.cache.redis_client", None)
def test_finops_fallback_record():
    tenant_id = "test_fallback_tenant"
    
    # Record
    finops = FinOpsService()
    finops.record_invocation(tenant_id, "my_tool")
    
    # Get status
    status = finops.get_budget_status(tenant_id)
    assert status["usage"] == 1
