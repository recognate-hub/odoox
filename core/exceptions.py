class BaseAppError(Exception):
    """Base exception for all application errors."""
    pass


# --- Configuration Errors ---
class ConfigurationError(BaseAppError):
    """Raised when application configuration is invalid or missing."""
    pass


# --- Odoo Errors ---
class OdooConnectorError(BaseAppError):
    """Base exception for Odoo connector errors."""
    pass

class OdooAuthError(OdooConnectorError):
    """Raised when authentication with Odoo fails."""
    pass

class OdooConnectionError(OdooConnectorError):
    """Raised when connection to Odoo server fails or times out."""
    pass

class OdooResourceNotFoundError(OdooConnectorError):
    """Raised when a requested resource is not found in Odoo."""
    pass


# --- Claude Errors ---
class ClaudeAPIError(BaseAppError):
    """Base exception for Claude API errors."""
    pass

class ClaudeTimeoutError(ClaudeAPIError):
    """Raised when a request to Claude times out."""
    pass


# --- Access & Security Errors ---
class PermissionDeniedError(BaseAppError):
    """Raised when a user/role does not have permission for an action."""
    pass

class RateLimitExceededError(BaseAppError):
    """Raised when a user/role has exceeded their rate limit."""
    pass


# --- Validation Errors ---
class ValidationError(BaseAppError):
    """Raised when data validation fails (outside of Pydantic)."""
    pass
