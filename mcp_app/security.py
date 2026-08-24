import functools
import time
from collections.abc import Callable
from typing import Any

from cachetools import TTLCache
from pydantic import BaseModel

from core.context import get_current_token, get_workspace_credentials
from core.exceptions import (
    FinOpsBudgetExceededException,
    OdooResourceNotFoundError,
    OdooValidationError,
    PermissionDeniedError,
    RateLimitExceededError,
    SessionExpiredError,
)
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
    Role is read from the workspace's per-workspace role field.
    """
    try:
        token = get_current_token()
    except RuntimeError:
        # current_token ContextVar is None — the SSE context was not propagated
        # into this thread. This is a server-side context propagation bug, not
        # a client auth failure. Log clearly so it's easy to distinguish.
        audit_logger.error(
            "Auth context not propagated into MCP tool thread. "
            "current_token ContextVar is None."
        )
        raise PermissionDeniedError(
            "Server auth context error: token not available in tool execution context."
        )
    try:
        from core.context import current_workspace_id

        workspace_id = current_workspace_id.get()
        workspace = get_workspace_credentials(token, workspace_id=workspace_id)
        return UserContext(user_id=workspace.user_id, role=workspace.role)
    except Exception as e:
        audit_logger.error("Failed to resolve user context", error=str(e))
        raise PermissionDeniedError("Could not verify identity for execution.")


RATE_LIMIT_MAX_CALLS = 100
RATE_LIMIT_WINDOW_SEC = 60
# In-memory rate limiting fallback: {user_id: [timestamps]} with auto-eviction
_rate_limit_state = TTLCache(maxsize=10000, ttl=RATE_LIMIT_WINDOW_SEC)

# Global FinOps instance
finops_service = FinOpsService()


def _check_rate_limit(user_id: str) -> None:
    """Enforce per-user rate limiting. Uses Redis when available, falls back to in-memory."""
    from core.cache import redis_client

    if redis_client:
        try:
            window_key = int(time.time()) // RATE_LIMIT_WINDOW_SEC
            redis_key = f"mcp_rate:{user_id}:{window_key}"
            current = redis_client.incr(redis_key)
            if current == 1:
                redis_client.expire(redis_key, RATE_LIMIT_WINDOW_SEC + 1)
            if current > RATE_LIMIT_MAX_CALLS:
                raise RateLimitExceededError(
                    f"User {user_id} exceeded rate limit of {RATE_LIMIT_MAX_CALLS} calls per {RATE_LIMIT_WINDOW_SEC}s."
                )
            return
        except RateLimitExceededError:
            raise
        except Exception as e:
            audit_logger.warning(
                "Redis rate limit failed, falling back to in-memory", error=str(e)
            )

    # In-memory fallback
    now = time.time()
    history = _rate_limit_state.get(user_id, [])

    # Prune old timestamps
    history = [t for t in history if now - t < RATE_LIMIT_WINDOW_SEC]

    if len(history) >= RATE_LIMIT_MAX_CALLS:
        # Save pruned history back before raising
        _rate_limit_state[user_id] = history
        raise RateLimitExceededError(
            f"User {user_id} exceeded rate limit of {RATE_LIMIT_MAX_CALLS} calls per {RATE_LIMIT_WINDOW_SEC}s."
        )

    history.append(now)
    _rate_limit_state[user_id] = history


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
                kwargs_keys=list(kwargs.keys()),
            )

            # 2. RBAC Verification via Policy Engine
            if not PolicyEngine.is_allowed(user.role, tool_action):
                audit_logger.warning(
                    "Permission Denied",
                    tool=func.__name__,
                    action=tool_action,
                    user_id=user.user_id,
                )
                raise PermissionDeniedError(
                    f"Role {user.role} does not have permission to execute {tool_action}"
                )

            # 2b. Model-Level RBAC Verification for Generic Tools
            if tool_action in [
                "search_read_records",
                "create_record",
                "update_record",
                "read_group_records",
                "archive_record",
                "execute_model_method",
            ]:
                model_name = kwargs.get("model")
                if model_name and not PolicyEngine.is_model_allowed(
                    user.role, tool_action, model_name
                ):
                    audit_logger.warning(
                        "Model Permission Denied",
                        tool=func.__name__,
                        action=tool_action,
                        model=model_name,
                        user_id=user.user_id,
                    )
                    raise PermissionDeniedError(
                        f"Role {user.role} does not have permission to access model {model_name}"
                    )

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
                    execution_time_ms=round((time.time() - start_time) * 1000, 2),
                )
                return result
            except SessionExpiredError:
                # JWT expired mid-session. Surface a clear reconnect prompt
                audit_logger.warning(
                    "Session expired during tool execution",
                    tool=func.__name__,
                    user_id=user.user_id,
                )
                return {
                    "status": "error",
                    "message": "⚠️ Your OdooX session has expired. Please disconnect and reconnect the 'odoox' server in Claude Desktop.",
                }
            except (
                FinOpsBudgetExceededException,
                PermissionDeniedError,
                RateLimitExceededError,
            ) as e:
                audit_logger.warning(
                    f"Policy rejection: {e}", tool=func.__name__, user_id=user.user_id
                )
                return {"status": "error", "message": str(e)}
            except (OdooResourceNotFoundError, OdooValidationError) as e:
                audit_logger.warning(
                    f"Odoo error: {e}", tool=func.__name__, user_id=user.user_id
                )
                return {"status": "error", "message": str(e)}
            except Exception as e:
                try:
                    from opentelemetry import trace

                    span = trace.get_current_span()
                    if span and span.is_recording():
                        span.record_exception(e)
                except Exception:
                    pass

                # 6. Audit Logging (Failure)
                audit_logger.error(
                    "Tool Failed",
                    tool=func.__name__,
                    user_id=user.user_id,
                    error=str(e),
                    execution_time_ms=round((time.time() - start_time) * 1000, 2),
                )

                from core.exceptions import OdooConnectionError, OdooAuthError
                
                if isinstance(e, (OdooConnectionError, OdooAuthError)):
                    return {
                        "status": "error",
                        "message": "Failed to connect to Odoo ERP. Please verify your credentials and connection URL in the Dashboard.",
                    }

                return {
                    "status": "error",
                    "message": f"Unexpected error during tool execution: {e!s}",
                }

        return wrapper

    return decorator
