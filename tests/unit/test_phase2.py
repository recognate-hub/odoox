import time
from unittest.mock import patch

import pytest

from core.exceptions import OdooConnectionError, CircuitBreakerOpenError
from core.idempotency import IdempotencyCache, _idempotency_state
from odoo.xmlrpc import (
    TimeoutSafeTransport,
    TimeoutTransport,
    XmlRpcOdooConnector,
    get_transport,
)


def test_timeout_transport():
    transport = get_transport("http://localhost", timeout=5)
    assert isinstance(transport, TimeoutTransport)
    assert transport.timeout == 5

    secure_transport = get_transport("https://localhost", timeout=5)
    assert isinstance(secure_transport, TimeoutSafeTransport)
    assert secure_transport.timeout == 5


def test_circuit_breaker():
    from config.settings import get_settings
    # Pass settings properly
    connector = XmlRpcOdooConnector(get_settings())
    # Override redis_client to None to test local circuit breaker
    with patch("odoo.xmlrpc.redis_client", None):
        db_name = "test_db"
        
        # Simulate 2 failures
        for _ in range(2):
            connector._record_failure(db_name)
        
        # Should not raise
        connector._check_circuit_breaker(db_name)
        
        # 3rd failure
        connector._record_failure(db_name)
        
        with pytest.raises(CircuitBreakerOpenError, match="Circuit breaker open"):
            connector._check_circuit_breaker(db_name)
            
        # Simulate time passing (half-open)
        with patch("time.time", return_value=time.time() + 31):
            # Should not raise, and should reset failures to 0
            connector._check_circuit_breaker(db_name)
            assert connector._circuit_breakers[db_name][0] == 0


def test_idempotency_cache():
    _idempotency_state.clear()
    
    tenant = "tenant_1"
    tool = "create_lead"
    payload = {"name": "Test Lead"}
    
    executions = 0
    def mock_execute():
        nonlocal executions
        executions += 1
        return 123
        
    # First call should execute
    res1 = IdempotencyCache.check_or_execute(tenant, tool, payload, mock_execute)
    assert res1 == 123
    assert executions == 1
    
    # Second identical call should hit cache
    res2 = IdempotencyCache.check_or_execute(tenant, tool, payload, mock_execute)
    assert res2 == 123
    assert executions == 1 # Execution count didn't increase!
    
    # Call with different payload should execute
    res3 = IdempotencyCache.check_or_execute(tenant, tool, {"name": "Other Lead"}, mock_execute)
    assert res3 == 123
    assert executions == 2
