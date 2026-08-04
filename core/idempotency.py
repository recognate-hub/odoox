import hashlib
import json
import time
from collections.abc import Callable
from typing import Any

from core.logger import get_logger

logger = get_logger(__name__)

# In-memory dictionary to store idempotency keys and their result (record_id)
# Format: { idempotency_key: (record_id, timestamp) }
_idempotency_state: dict[str, tuple[Any, float]] = {}

IDEMPOTENCY_TTL_SEC = 900  # 15 minutes

def _generate_key(tenant_db: str, tool_name: str, payload: Any) -> str:
    """Generate a unique idempotency key based on tenant, tool, and payload."""
    payload_str = json.dumps(payload, sort_keys=True)
    raw_key = f"{tenant_db}:{tool_name}:{payload_str}"
    return hashlib.sha256(raw_key.encode('utf-8')).hexdigest()

class IdempotencyCache:
    """
    Provides a simple Check-then-Act idempotency mechanism for writes 
    that lack native idempotency keys (like Odoo's XML-RPC `create`).
    """
    
    @staticmethod
    def check_or_execute(tenant_db: str, tool_name: str, payload: Any, execute_fn: Callable[[], Any]) -> Any:
        now = time.time()
        
        # 1. Clean up expired keys proactively to prevent memory bloat
        expired_keys = [k for k, (res, ts) in _idempotency_state.items() if now - ts > IDEMPOTENCY_TTL_SEC]
        for k in expired_keys:
            del _idempotency_state[k]
            
        # 2. Check if this request is a duplicate retry
        idem_key = _generate_key(tenant_db, tool_name, payload)
        if idem_key in _idempotency_state:
            cached_result, ts = _idempotency_state[idem_key]
            logger.info("Idempotency cache hit. Returning cached result to prevent duplicate write.", tool=tool_name, tenant=tenant_db)
            return cached_result
            
        # 3. Execute the function
        result = execute_fn()
        
        # 4. Cache the result for future retries within the TTL
        _idempotency_state[idem_key] = (result, now)
        return result
