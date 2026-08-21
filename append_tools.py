import os

TOOLS_DIR = "mcp_app/tools"

HEADER = """from typing import Any
from mcp_app.server import mcp, _span, _get_tenant_service
from mcp_app.security import secure_tool
from mcp_app.validation import validate_write_input
from mcp_app.schemas import *
from core.logger import get_logger

logger = get_logger(__name__)

"""

discuss_append = """
@mcp.tool()
@secure_tool()
@validate_write_input(PostMessageInput)
def post_message(res_model: str, res_id: int, body: str, message_type: str = "comment") -> dict[str, Any]:
    with _span("mcp.post_message"):
        odoo_repo, _ = _get_tenant_service()
        from services.discuss import DiscussService
        service = DiscussService(odoo_repo)
        return service.post_message(res_model, res_id, body, message_type)

@mcp.tool()
@secure_tool()
@validate_write_input(CreateChannelInput)
def create_channel(name: str, channel_type: str = "channel") -> dict[str, Any]:
    with _span("mcp.create_channel"):
        odoo_repo, _ = _get_tenant_service()
        from services.discuss import DiscussService
        service = DiscussService(odoo_repo)
        return service.create_channel(name, channel_type)
"""

with open(os.path.join(TOOLS_DIR, "discuss.py"), "a", encoding="utf-8") as f:
    f.write(discuss_append)

purchase_content = (
    HEADER
    + """
@mcp.tool()
@secure_tool()
@validate_write_input(CreatePurchaseOrderInput)
def create_purchase_order(partner_id: int, order_lines: list[dict]) -> dict[str, Any]:
    with _span("mcp.create_purchase_order"):
        odoo_repo, _ = _get_tenant_service()
        from services.purchase import PurchaseService
        service = PurchaseService(odoo_repo)
        return service.create_purchase_order(partner_id, order_lines)

@mcp.tool()
@secure_tool()
def get_purchase_orders(partner_id: int | None = None, limit: int = 20) -> list[dict[str, Any]]:
    with _span("mcp.get_purchase_orders"):
        odoo_repo, _ = _get_tenant_service()
        from services.purchase import PurchaseService
        service = PurchaseService(odoo_repo)
        return service.get_purchase_orders(partner_id, limit)
"""
)

with open(os.path.join(TOOLS_DIR, "purchase.py"), "w", encoding="utf-8") as f:
    f.write(purchase_content)


production_content = (
    HEADER
    + """
@mcp.tool()
@secure_tool()
@validate_write_input(CreateManufacturingOrderInput)
def create_manufacturing_order(product_id: int, product_qty: float) -> dict[str, Any]:
    with _span("mcp.create_manufacturing_order"):
        odoo_repo, _ = _get_tenant_service()
        from services.production import ProductionService
        service = ProductionService(odoo_repo)
        return service.create_manufacturing_order(product_id, product_qty)

@mcp.tool()
@secure_tool()
def get_manufacturing_orders(limit: int = 20) -> list[dict[str, Any]]:
    with _span("mcp.get_manufacturing_orders"):
        odoo_repo, _ = _get_tenant_service()
        from services.production import ProductionService
        service = ProductionService(odoo_repo)
        return service.get_manufacturing_orders(limit)
"""
)

with open(os.path.join(TOOLS_DIR, "production.py"), "w", encoding="utf-8") as f:
    f.write(production_content)

quality_content = (
    HEADER
    + """
@mcp.tool()
@secure_tool()
@validate_write_input(CreateQualityAlertInput)
def create_quality_alert(name: str, product_id: int, team_id: int | None = None, priority: str = "0") -> dict[str, Any]:
    with _span("mcp.create_quality_alert"):
        odoo_repo, _ = _get_tenant_service()
        from services.quality import QualityService
        service = QualityService(odoo_repo)
        return service.create_quality_alert(name, product_id, team_id, priority)

@mcp.tool()
@secure_tool()
def get_quality_checks(product_id: int | None = None, limit: int = 20) -> list[dict[str, Any]]:
    with _span("mcp.get_quality_checks"):
        odoo_repo, _ = _get_tenant_service()
        from services.quality import QualityService
        service = QualityService(odoo_repo)
        return service.get_quality_checks(product_id, limit)
"""
)

with open(os.path.join(TOOLS_DIR, "quality.py"), "w", encoding="utf-8") as f:
    f.write(quality_content)


inventory_append = """
@mcp.tool()
@secure_tool()
@validate_write_input(CreateStockMoveInput)
def create_stock_move(name: str, product_id: int, product_uom_qty: float, location_id: int, location_dest_id: int) -> dict[str, Any]:
    with _span("mcp.create_stock_move"):
        odoo_repo, _ = _get_tenant_service()
        from services.inventory import InventoryService
        service = InventoryService(odoo_repo)
        return service.create_stock_move(name, product_id, product_uom_qty, location_id, location_dest_id)

@mcp.tool()
@secure_tool()
def get_inventory_valuation(product_id: int | None = None) -> list[dict[str, Any]]:
    with _span("mcp.get_inventory_valuation"):
        odoo_repo, _ = _get_tenant_service()
        from services.inventory import InventoryService
        service = InventoryService(odoo_repo)
        return service.get_inventory_valuation(product_id)
"""

with open(os.path.join(TOOLS_DIR, "inventory.py"), "a", encoding="utf-8") as f:
    f.write(inventory_append)

reports_content = (
    HEADER
    + """
@mcp.tool()
@secure_tool()
@validate_write_input(ReadGroupInput)
def generate_report(model: str, domain: list[Any], fields: list[str], groupby: list[str]) -> list[dict[str, Any]]:
    with _span("mcp.generate_report"):
        odoo_repo, _ = _get_tenant_service()
        from services.reports import ReportsService
        service = ReportsService(odoo_repo)
        return service.generate_report(model, domain, fields, groupby)
"""
)

with open(os.path.join(TOOLS_DIR, "reports.py"), "w", encoding="utf-8") as f:
    f.write(reports_content)

print("done appending and creating tools.")
