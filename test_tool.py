import os
from mcp_app.security import tenant_context

tenant_context.set("mock_token")

from mcp_app.server import _get_tenant_service
from services.production import ProductionService
import logging

logging.basicConfig(level=logging.DEBUG)

repo, _ = _get_tenant_service()
service = ProductionService(repo)
try:
    print("Calling get_bom_hierarchy...")
    res = service.get_bom_hierarchy(bom_id=1)
    print("Result:", res)
except Exception as e:
    print("Error:", e)
    import traceback
    traceback.print_exc()
