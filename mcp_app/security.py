import time
import functools
from typing import List, Callable, Any, Dict
from pydantic import BaseModel

from core.exceptions import PermissionDeniedError, RateLimitExceededError
from core.logger import get_logger

# Dedicated audit logger
audit_logger = get_logger("audit")

class UserContext(BaseModel):
    user_id: str
    role: str

# Mock context since standard MCP over stdio lacks auth headers.
# In a production HTTP deployment, this would be set by middleware extracting JWTs.
_mock_context = UserContext(user_id="system_user", role="Admin")

# In-memory rate limiting state: {user_id: [timestamps]}
_rate_limit_state: Dict[str, List[float]] = {}
RATE_LIMIT_MAX_CALLS = 100
RATE_LIMIT_WINDOW_SEC = 60

def _check_rate_limit(user_id: str) -> None:
    now = time.time()
    if user_id not in _rate_limit_state:
        _rate_limit_state[user_id] = []
    
    # Filter timestamps within the window
    _rate_limit_state[user_id] = [t for t in _rate_limit_state[user_id] if now - t < RATE_LIMIT_WINDOW_SEC]
    
    if len(_rate_limit_state[user_id]) >= RATE_LIMIT_MAX_CALLS:
        raise RateLimitExceededError(f"User {user_id} exceeded rate limit of {RATE_LIMIT_MAX_CALLS} calls per {RATE_LIMIT_WINDOW_SEC}s.")
        
    _rate_limit_state[user_id].append(now)


def secure_tool(allowed_roles: List[str]):
    """
    Decorator to enforce RBAC, audit logging, and rate limiting on an MCP tool.
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            user = _mock_context
            
            # 1. Audit Logging (Request)
            audit_logger.info(
                "Tool Invoked",
                tool=func.__name__,
                user_id=user.user_id,
                role=user.role,
                kwargs_keys=list(kwargs.keys())
            )
            
            # 2. RBAC Verification
            if user.role not in allowed_roles and "Admin" not in user.role:
                audit_logger.warning("Permission Denied", tool=func.__name__, user_id=user.user_id)
                raise PermissionDeniedError(f"Role {user.role} does not have permission to execute {func.__name__}")
                
            # 3. Rate Limiting
            _check_rate_limit(user.user_id)
            
            # 4. Execution
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                
                # 5. Audit Logging (Success)
                audit_logger.info(
                    "Tool Succeeded",
                    tool=func.__name__,
                    user_id=user.user_id,
                    execution_time_ms=round((time.time() - start_time) * 1000, 2)
                )
                return result
            except Exception as e:
                # 5. Audit Logging (Failure)
                audit_logger.error(
                    "Tool Failed",
                    tool=func.__name__,
                    user_id=user.user_id,
                    error=str(e),
                    execution_time_ms=round((time.time() - start_time) * 1000, 2)
                )
                raise
                
        return wrapper
    return decorator
