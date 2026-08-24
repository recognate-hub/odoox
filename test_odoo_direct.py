import xmlrpc.client
from config.settings import get_settings

settings = get_settings()

common = xmlrpc.client.ServerProxy(f'{settings.ODOO_URL}/xmlrpc/2/common')
uid = common.authenticate(settings.ODOO_DB, settings.ODOO_USERNAME, settings.ODOO_PASSWORD, {})

models = xmlrpc.client.ServerProxy(f'{settings.ODOO_URL}/xmlrpc/2/object')

# 1. Fetch bom lines
bom_lines = models.execute_kw(
    settings.ODOO_DB, uid, settings.ODOO_PASSWORD,
    'mrp.bom.line', 'search_read',
    [[['bom_id', '=', 1]]],
    {'fields': ['bom_id', 'product_id', 'product_qty', 'product_uom_id'], 'limit': 50}
)
print("BOM lines:", bom_lines)

product_ids = [line['product_id'][0] for line in bom_lines if 'product_id' in line and isinstance(line['product_id'], list)]
print("Product IDs:", product_ids)

if product_ids:
    products = models.execute_kw(
        settings.ODOO_DB, uid, settings.ODOO_PASSWORD,
        'product.product', 'search_read',
        [[['id', 'in', product_ids]]],
        {'fields': ['name', 'standard_price', 'default_code'], 'limit': len(product_ids)}
    )
    print("Products:", products)
else:
    print("No products found")

