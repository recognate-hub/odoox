import functools
import time
from collections.abc import Callable
from typing import Any

from pydantic import BaseModel

from core.context import get_current_token, get_workspace_credentials
from core.exceptions import PermissionDeniedError, RateLimitExceededError
from core.logger import get_logger
from core.policy import PolicyEngine
from services.finops import FinOpsService

# Dedicated audit logger
audit_logger = get_logger("audit")

class UserContext(BaseModel):
    user_id: str
    role: str

def get_current_user_context() -> UserContext:
    """
    Resolves the user context dynamically from the active JWT token.
    Defaulting to 'Admin' role as requested by the user.
    """
    try:
        token = get_current_token()
        workspace = get_workspace_credentials(token)
        return UserContext(user_id=workspace.user_id, role="Admin")
    except Exception as e:
        audit_logger.error("Failed to resolve user context", error=str(e))
        raise PermissionDeniedError("Could not verify identity for execution.")

# In-memory rate limiting state: {user_id: [timestamps]}
_rate_limit_state: dict[str, list[float]] = {}
RATE_LIMIT_MAX_CALLS = 100
RATE_LIMIT_WINDOW_SEC = 60

# Global FinOps instance
finops_service = FinOpsService()

def _check_rate_limit(user_id: str) -> None:
    now = time.time()
    if user_id not in _rate_limit_state:
        _rate_limit_state[user_id] = []
    
    # Filter timestamps within the window
    _rate_limit_state[user_id] = [t for t in _rate_limit_state[user_id] if now - t < RATE_LIMIT_WINDOW_SEC]
    
    if len(_rate_limit_state[user_id]) >= RATE_LIMIT_MAX_CALLS:
        raise RateLimitExceededError(f"User {user_id} exceeded rate limit of {RATE_LIMIT_MAX_CALLS} calls per {RATE_LIMIT_WINDOW_SEC}s.")
        
    _rate_limit_state[user_id].append(now)


def secure_tool(action: str | None = None):
    """
    Decorator to enforce Policy-as-Code RBAC, audit logging, and rate limiting on an MCP tool.
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            user = get_current_user_context()
            
            # Determine the action name (default to function name)
            tool_action = action or func.__name__
            
            # 1. Audit Logging (Request)
            audit_logger.info(
                "Tool Invoked",
                tool=func.__name__,
                action=tool_action,
                user_id=user.user_id,
                role=user.role,
                kwargs_keys=list(kwargs.keys())
            )
            
            # 2. RBAC Verification via Policy Engine
            if not PolicyEngine.is_allowed(user.role, tool_action):
                audit_logger.warning("Permission Denied", tool=func.__name__, action=tool_action, user_id=user.user_id)
                raise PermissionDeniedError(f"Role {user.role} does not have permission to execute {tool_action}")
                
            # 3. Rate Limiting
            _check_rate_limit(user.user_id)
            
            # 4. FinOps Budget Check
            finops_service.record_invocation(user.user_id, func.__name__)
            
            # 5. Execution
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                
                # 6. Audit Logging (Success)
                audit_logger.info(
                    "Tool Succeeded",
                    tool=func.__name__,
                    user_id=user.user_id,
                    execution_time_ms=round((time.time() - start_time) * 1000, 2)
                )
                return result
            except Exception as e:
                # 6. Audit Logging (Failure)
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
