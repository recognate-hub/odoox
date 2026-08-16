import os
import re

SERVER_FILE = "mcp_app/server.py"
TOOLS_DIR = "mcp_app/tools"

# Read the file
with open(SERVER_FILE, "r", encoding="utf-8") as f:
    content = f.read()

# Define mappings from function names to module names
TOOL_MAPPINGS = {
    "get_leads": "crm",
    "create_lead": "crm",
    "update_lead": "crm",
    "log_crm_note": "crm",
    "get_lead_context": "crm",
    
    "search_customer": "contacts",
    "create_contact": "contacts",
    "get_customer_details": "contacts",
    
    "get_products": "inventory",
    "create_product": "inventory",
    
    "get_recent_quotes": "sales",
    "create_quote": "sales",
    
    "revenue_report": "dashboards",
    "get_pipeline_forecast_data": "dashboards",
    
    "schedule_meeting": "calendar",
    
    "create_invoice": "invoicing",
    
    "send_email": "discuss",
    
    "search_read_records": "generic",
    "create_record": "generic",
    "update_record": "generic",
    "get_installed_apps": "generic",
    "get_model_fields": "generic",
    "read_group": "generic",
    "archive_record": "generic",
    "create_attachment": "generic",
    "read_attachment": "generic",
    "execute_model_method": "generic",
}

# The header for the new tool files
HEADER = """from typing import Any
from mcp_app.server import mcp, _span, _get_tenant_service
from mcp_app.security import secure_tool
from mcp_app.validation import validate_write_input
from mcp_app.schemas import *
from core.logger import get_logger

logger = get_logger(__name__)

"""

# Extract the fastMCP tools
pattern = r"(@mcp\.tool\(\).*?)(?=\n@mcp\.tool\(\)|\Z)"
tools = re.findall(pattern, content, re.DOTALL)

modules = {}

for tool_source in tools:
    # find def function_name
    match = re.search(r"def\s+([a-zA-Z0-9_]+)\s*\(", tool_source)
    if match:
        func_name = match.group(1)
        mod_name = TOOL_MAPPINGS.get(func_name, "generic")
        
        if mod_name not in modules:
            modules[mod_name] = HEADER
            
        modules[mod_name] += tool_source + "\n\n"

# Write the new module files
for mod_name, mod_content in modules.items():
    with open(os.path.join(TOOLS_DIR, f"{mod_name}.py"), "w", encoding="utf-8") as f:
        f.write(mod_content)

# Keep the beginning of server.py up to the first @mcp.tool()
first_tool_idx = content.find("@mcp.tool()")
new_server_content = content[:first_tool_idx]

# Add imports for all tool modules at the end
new_server_content += "\n# Register all tools\n"
for mod_name in modules:
    new_server_content += f"import mcp_app.tools.{mod_name}\n"

# Plus the new tools modules
new_server_content += """
import mcp_app.tools.purchase
import mcp_app.tools.production
import mcp_app.tools.quality
import mcp_app.tools.reports
"""

with open(SERVER_FILE, "w", encoding="utf-8") as f:
    f.write(new_server_content)

print("Split completed.")
