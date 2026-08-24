import os
import logging
from core.context import current_token, current_workspace_id
current_token.set("mock_token")
current_workspace_id.set("mock_ws")

from config.settings import get_settings
from odoo.xmlrpc import XmlRpcOdooConnector
from repositories.odoo import OdooRepository
from services.production import ProductionService

logging.basicConfig(level=logging.DEBUG)

settings = get_settings()
connector = XmlRpcOdooConnector(settings)
repo = OdooRepository(connector)
service = ProductionService(repo)

try:
    print("Testing get_bom_hierarchy(bom_id=1)...")
    res = service.get_bom_hierarchy(bom_id=1, limit=50)
    print("Result:", res)
except Exception as e:
    print("Error:", str(e))
    import traceback
    traceback.print_exc()
