import xmlrpc.client
from config.settings import get_settings

settings = get_settings()

common = xmlrpc.client.ServerProxy(f'{settings.ODOO_URL}/xmlrpc/2/common')
uid = common.authenticate(settings.ODOO_DB, settings.ODOO_USERNAME, settings.ODOO_PASSWORD, {})

models = xmlrpc.client.ServerProxy(f'{settings.ODOO_URL}/xmlrpc/2/object')

try:
    bom_lines = models.execute_kw(
        settings.ODOO_DB, uid, settings.ODOO_PASSWORD,
        'mrp.bom.line', 'search_read',
        [[['bom_id', '=', 1]]],
        {'fields': ['bom_id', 'product_id', 'product_qty', 'product_uom_id'], 'limit': 50}
    )
    print("BOM lines:", bom_lines)
except Exception as e:
    print("Error:", e)
