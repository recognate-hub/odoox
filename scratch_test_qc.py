import sys
import os
import asyncio

sys.path.append(os.path.abspath("."))

from odoo.client import OdooClient
from config.settings import settings
from repositories.odoo import OdooRepository

def main():
    client = OdooClient(
        url=settings.ODOO_URL,
        db=settings.ODOO_DB,
        username=settings.ODOO_USERNAME,
        password=settings.ODOO_PASSWORD
    )
    repo = OdooRepository(client)
    
    try:
        fields = repo.get_model_fields("quality.check")
        print("Fields in quality.check:")
        for fname, fdesc in fields.items():
            if fname in ['name', 'product_id', 'test_type_id', 'quality_state', 'measure', 'norm', 'workorder_id', 'point_id', 'note', 'title']:
                print(f" - {fname}: {fdesc.get('type')} ({fdesc.get('string')})")
        
        print("\nFetching some quality checks:")
        records = repo.search_read_records(
            "quality.check", 
            domain=[], 
            fields=['name', 'product_id', 'test_type', 'measure', 'norm', 'workorder_id', 'point_id', 'quality_state'], 
            limit=5
        )
        for r in records:
            print(r)
            
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    main()
