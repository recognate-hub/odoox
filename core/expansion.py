from typing import Any, Dict, List
from core.logger import get_logger

logger = get_logger(__name__)

class RelationExpander:
    """
    Intelligently expands relational fields (Many2one, One2many, Many2many) in Odoo records.
    Instead of returning raw IDs (e.g. `partner_id: [1, "Azure"]`), it fetches the full 
    sub-record data and embeds it directly into the parent record.
    """

    def __init__(self, connector):
        self.connector = connector
        # Expected from the connector, usually available through connector.schema_engine
        self.schema_engine = getattr(connector, "schema_engine", None)

    def expand_records(self, model: str, records: List[Dict[str, Any]], expand_fields: List[str]) -> List[Dict[str, Any]]:
        """
        Takes a list of records and recursively expands requested relational fields.
        
        Args:
            model: The base Odoo model of the records.
            records: A list of dictionaries representing the fetched records.
            expand_fields: A list of field paths to expand (e.g., ["order_line", "order_line.product_id", "partner_id"]).
        """
        if not records or not expand_fields:
            return records
            
        # Parse expand specs into a tree. 
        # e.g. ["order_line.product_id", "partner_id"] -> {"order_line": {"product_id": {}}, "partner_id": {}}
        expand_tree = self._build_expand_tree(expand_fields)
        
        self._expand_level(model, records, expand_tree)
        return records

    def _build_expand_tree(self, fields: List[str]) -> Dict[str, Any]:
        tree = {}
        for field_path in fields:
            parts = field_path.split(".")
            current = tree
            for part in parts:
                if part not in current:
                    current[part] = {}
                current = current[part]
        return tree

    def _expand_level(self, model: str, records: List[Dict[str, Any]], expand_tree: Dict[str, Any]):
        if not self.schema_engine:
            logger.warning("SchemaEngine not found on connector. Cannot expand relations.")
            return

        fields_info = self.schema_engine.get_model_fields_cached(model)
        if not fields_info:
            return

        for field_name, sub_tree in expand_tree.items():
            if field_name not in fields_info:
                continue
                
            field_type = fields_info[field_name].get("type")
            target_model = fields_info[field_name].get("relation")
            
            if not target_model or field_type not in ("many2one", "one2many", "many2many"):
                continue

            # Gather all unique target IDs across all records for batch fetching
            target_ids = set()
            for rec in records:
                val = rec.get(field_name)
                if not val:
                    continue
                    
                if field_type == "many2one":
                    # Many2one value is usually [id, "name"] or just id
                    target_id = val[0] if isinstance(val, (list, tuple)) else val
                    if isinstance(target_id, int):
                        target_ids.add(target_id)
                elif field_type in ("one2many", "many2many"):
                    # value is a list of IDs
                    if isinstance(val, list):
                        target_ids.update([v for v in val if isinstance(v, int)])

            if not target_ids:
                continue

            # Batch fetch related records
            raw_sub_records = self.connector.search_read_records(
                model=target_model,
                domain=[["id", "in", list(target_ids)]],
                fields=None, # Fetch available fields
                limit=len(target_ids)
            )
            
            # Prune binary images, giant base64 payloads, and internal noise to keep responses lightweight and fast
            sub_records = []
            for r in raw_sub_records:
                clean_r = {}
                for k, v in r.items():
                    if (
                        k.startswith("image_")
                        or k.startswith("avatar_")
                        or k.endswith("_image")
                        or k in ("datas", "db_datas", "icon_image_base64")
                    ):
                        continue
                    if isinstance(v, str) and len(v) > 2000 and " " not in v:
                        continue
                    clean_r[k] = v
                sub_records.append(clean_r)

            # Sub-expand if there are further nodes in the tree
            if sub_tree and sub_records:
                self._expand_level(target_model, sub_records, sub_tree)

            # Map results by ID for fast lookup
            sub_records_map = {r["id"]: r for r in sub_records if "id" in r}

            # Re-attach expanded records back to the original payload
            for rec in records:
                val = rec.get(field_name)
                if not val:
                    continue
                    
                if field_type == "many2one":
                    target_id = val[0] if isinstance(val, (list, tuple)) else val
                    if target_id in sub_records_map:
                        rec[field_name] = sub_records_map[target_id]
                elif field_type in ("one2many", "many2many"):
                    if isinstance(val, list):
                        rec[field_name] = [sub_records_map[v] for v in val if v in sub_records_map]
