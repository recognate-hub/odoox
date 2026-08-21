import sys
import logging
from mcp_app.server import _get_tenant_service

logging.basicConfig(level=logging.DEBUG)

repo, _ = _get_tenant_service()
try:
    print("Fetching BOM lines...")
    lines = repo.connector.search_read_records("mrp.bom.line", domain=[], fields=["bom_id", "product_id"], limit=5)
    print("Found:", len(lines))
    print(lines)
except Exception as e:
    print("Error:", str(e))
