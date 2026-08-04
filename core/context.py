import contextvars
from pydantic import BaseModel
from typing import Optional

class WorkspaceContext(BaseModel):
    odoo_url: str
    odoo_db: str
    odoo_username: str
    odoo_password: str

# Context variable to hold the current request's workspace settings
current_workspace: contextvars.ContextVar[Optional[WorkspaceContext]] = contextvars.ContextVar(
    "current_workspace", default=None
)

def get_current_workspace() -> WorkspaceContext:
    """Retrieve the current workspace from context."""
    workspace = current_workspace.get()
    if not workspace:
        raise RuntimeError("No workspace context is currently active.")
    return workspace
