from typing import Any
from mcp_app.server import mcp, _get_tenant_service
from mcp_app.security import secure_tool

@mcp.tool()
@secure_tool()
def inspect_database_topology() -> list[dict[str, Any]]:
    """
    Returns a high-level summary of the connected database schema.
    Includes a list of installed modules (apps) and standard metadata.
    Use this to understand what business capabilities the database supports.
    """
    repo, _ = _get_tenant_service()
    # List installed apps
    apps = repo.get_installed_apps()
    return apps

@mcp.tool()
@secure_tool()
def get_model_schema_details(model: str) -> dict[str, Any]:
    """
    Fetches the comprehensive field definitions for a specific Odoo model.
    Use this before querying a model you are unfamiliar with, to see exactly what fields
    are available, their data types, relations, and if they are required.
    """
    repo, _ = _get_tenant_service()
    return repo.get_model_fields(model)

@mcp.tool()
@secure_tool()
def search_flexible_records(model: str, query: str | None = None, limit: int = 20) -> list[dict[str, Any]]:
    """
    A universal, error-tolerant query tool that automatically tries to search standard 
    'name' or 'display_name' fields on any model. If you don't know the exact schema, 
    use this to fetch a concise sampling of records from any model.
    """
    repo, _ = _get_tenant_service()
    
    # Introspect fields to find the display name
    fields_info = repo.get_model_fields(model)
    search_field = "display_name" if "display_name" in fields_info else "name"
    if search_field not in fields_info:
        domain = []
    else:
        domain = [[search_field, "ilike", query]] if query else []
    
    # Curated lightweight field projection to prevent dumping 120+ columns
    if model == "res.partner":
        fields = ["id", "name", "email", "phone", "city", "country_id", "is_company"]
    elif model == "product.product":
        fields = ["id", "name", "default_code", "list_price", "standard_price", "qty_available"]
    elif model == "sale.order":
        fields = ["id", "name", "partner_id", "amount_total", "state", "date_order"]
    elif model == "crm.lead":
        fields = ["id", "name", "partner_id", "stage_id", "expected_revenue", "probability"]
    elif model == "mrp.production":
        fields = ["id", "name", "product_id", "product_qty", "state", "bom_id"]
    elif model == "mrp.workcenter":
        fields = ["id", "name", "code", "active", "time_efficiency"]
    else:
        # Filter to top core fields, omitting binary / image / chatter fields
        fields = [
            f for f, finfo in list(fields_info.items())[:12]
            if finfo.get("type") not in ("binary", "text", "html")
            and not f.startswith("message_")
            and not f.startswith("activity_")
            and not f.startswith("image_")
        ]
        
    return repo.search_read_records(model, domain=domain, fields=fields, limit=limit)

@mcp.tool()
@secure_tool()
def explore_model_relations(
    model: str, record_id: int, relation_field: str | None = None, limit: int = 10
) -> dict[str, Any]:
    """
    Navigates linked records (Many2one, One2many, Many2many) across arbitrary tables.
    If relation_field is omitted, returns the record and a summary of all relational fields available on this record.
    If relation_field is provided, it reads up to `limit` related records.
    """
    repo, _ = _get_tenant_service()
    fields_info = repo.get_model_fields(model)
    
    # Just reading the single record (pruned of heavy binary/chatter fields)
    records = repo.search_read_records(model, domain=[["id", "=", record_id]], limit=1)
    if not records:
        return {"status": "error", "message": f"Record {record_id} not found in model {model}"}
        
    record = records[0]
    # Prune binary and chatter fields from summary
    clean_record = {
        k: v for k, v in record.items()
        if not k.startswith("image_") and not k.startswith("message_") and not k.startswith("activity_") and k != "datas"
    }
    
    if not relation_field:
        # Summarize available relations
        relations = {}
        for fname, finfo in fields_info.items():
            ftype = finfo.get("type")
            if ftype in ("many2one", "one2many", "many2many"):
                val = clean_record.get(fname)
                relations[fname] = {
                    "type": ftype,
                    "target_model": finfo.get("relation"),
                    "count": len(val) if isinstance(val, list) else (1 if val else 0),
                    "value_preview": val if ftype == "many2one" else (val[:5] if isinstance(val, list) else val)
                }
        return {
            "record": clean_record,
            "available_relations": relations,
            "suggestion": "Call explore_model_relations again with a specific relation_field and limit to fetch linked records."
        }
    
    # Navigating a specific relation
    finfo = fields_info.get(relation_field)
    if not finfo:
        return {"status": "error", "message": f"Field {relation_field} does not exist on {model}"}
        
    ftype = finfo.get("type")
    if ftype not in ("many2one", "one2many", "many2many"):
        return {"status": "error", "message": f"Field {relation_field} is not a relational field (type: {ftype})"}
        
    target_model = finfo.get("relation")
    if not target_model:
        return {"status": "error", "message": f"Target model for {relation_field} is unknown"}
        
    val = record.get(relation_field)
    if not val:
        return {"status": "success", "data": []}
        
    if ftype == "many2one":
        target_id = val[0] if isinstance(val, (list, tuple)) else val
        return {"status": "success", "data": repo.search_read_records(target_model, domain=[["id", "=", target_id]], limit=1)}
        
    elif ftype in ("one2many", "many2many"):
        target_ids = val[:limit] if isinstance(val, list) else [val]
        return {
            "status": "success",
            "total_linked_count": len(val) if isinstance(val, list) else 1,
            "returned_count": len(target_ids),
            "data": repo.search_read_records(target_model, domain=[["id", "in", target_ids]], limit=limit)
        }
        
    return {"status": "error", "message": "Unhandled relation type"}
