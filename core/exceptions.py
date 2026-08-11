class BaseAppError(Exception):
    """Base exception for all application errors."""


# --- Configuration Errors ---
class ConfigurationError(BaseAppError):
    """Raised when application configuration is invalid or missing."""


# --- Odoo Errors ---
class OdooConnectorError(BaseAppError):
    """Base exception for Odoo connector errors."""

class OdooAuthError(OdooConnectorError):
    """Raised when authentication with Odoo fails."""

class OdooConnectionError(OdooConnectorError):
    """Raised when connection to Odoo server fails or times out."""

class CircuitBreakerOpenError(OdooConnectorError):
    """Raised when the circuit breaker is open and blocks connection attempts."""

class OdooResourceNotFoundError(OdooConnectorError):
    """Raised when a requested resource is not found in Odoo."""


# --- Claude Errors ---
class ClaudeAPIError(BaseAppError):
    """Base exception for Claude API errors."""

class ClaudeTimeoutError(ClaudeAPIError):
    """Raised when a request to Claude times out."""


# --- Access & Security Errors ---
class PermissionDeniedError(BaseAppError):
    """Raised when a user/role does not have permission for an action."""

class RateLimitExceededError(BaseAppError):
    """Raised when a user/role has exceeded their rate limit."""


# --- Validation Errors ---
class ValidationError(BaseAppError):
    """Raised when data validation fails (outside of Pydantic)."""

# --- FinOps Errors ---
class FinOpsBudgetExceededException(BaseAppError):
    """Raised when a tenant exceeds their allowed API budget."""
