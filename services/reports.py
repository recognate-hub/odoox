from typing import Any

from core.logger import get_logger
from repositories.odoo import OdooRepository

logger = get_logger(__name__)


class ReportsService:
    def __init__(self, odoo_repo: OdooRepository):
        self.odoo = odoo_repo

    def generate_report(
        self, model: str, domain: list[Any], fields: list[str], groupby: list[str]
    ) -> list[dict[str, Any]]:
        # Odoo saas-19.4 XML-RPC does not reliably support read_group.
        # Fallback to fetching records and aggregating in Python.
        
        # Ensure we fetch the fields we need to group by
        fetch_fields = list(set(fields + groupby))
        
        # We limit to 5000 records to prevent OOM / timeouts
        records = self.odoo.search_read_records(model, domain, fetch_fields, limit=5000)
        
        if not groupby:
            return records
            
        # Perform a basic count/sum aggregation
        summary = {}
        for rec in records:
            # Create a tuple key of all group values
            group_key_parts = []
            for gb_field in groupby:
                val = rec.get(gb_field)
                # Handle many2one tuples (id, name)
                if isinstance(val, (list, tuple)) and len(val) > 0:
                    val = val[0]
                group_key_parts.append(str(val))
            
            group_key = tuple(group_key_parts)
            
            if group_key not in summary:
                # Initialize the summary row
                row = {f"{gb_field}": rec.get(gb_field) for gb_field in groupby}
                row["__count"] = 0
                for f in fields:
                    if f not in groupby:
                        row[f] = 0.0
                summary[group_key] = row
                
            summary[group_key]["__count"] += 1
            for f in fields:
                if f not in groupby:
                    try:
                        summary[group_key][f] += float(rec.get(f) or 0.0)
                    except (ValueError, TypeError):
                        pass
                        
        return list(summary.values())
