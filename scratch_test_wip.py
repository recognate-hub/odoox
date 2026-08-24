import sys
import os

# Add project root to path
sys.path.append(os.path.abspath("."))

from core.dependency_injection import get_odoo_connector
from repositories.odoo import OdooRepository
from core.domain_builder import Domain

def main():
    connector = get_odoo_connector()
    repo = OdooRepository(connector)
    
    d = Domain().in_("state", ["pending", "waiting", "ready", "progress"])
    fields = [
        "name",
        "production_id",
        "workcenter_id",
        "product_id",
        "state",
        "qty_producing",
        "qty_production",
        "qty_remaining",
    ]
    
    records = repo.search_read_records("mrp.workorder", domain=d.build(), fields=fields, limit=10)
    print("Work Orders:")
    for r in records:
        print(r)
        
    if records:
        # Get product ids
        product_ids = [r['product_id'][0] for r in records if r.get('product_id')]
        if product_ids:
            prod_records = repo.search_read_records("product.product", domain=[("id", "in", product_ids)], fields=["name", "standard_price"])
            print("\nProducts:")
            for p in prod_records:
                print(p)

if __name__ == "__main__":
    main()
