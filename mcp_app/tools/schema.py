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
def search_flexible_records(model: str, query: str | None = None, limit: int = 50) -> list[dict[str, Any]]:
    """
    A universal, error-tolerant query tool that automatically tries to search standard 
    'name' or 'display_name' fields on any model. If you don't know the exact schema, 
    use this to fetch a sampling of records from any model.
    """
    repo, _ = _get_tenant_service()
    
    # Introspect fields to find the display name
    fields_info = repo.get_model_fields(model)
    search_field = "display_name" if "display_name" in fields_info else "name"
    if search_field not in fields_info:
        # Fallback to no domain if there's no name field
        domain = []
    else:
        domain = [[search_field, "ilike", query]] if query else []
        
    return repo.search_read_records(model, domain=domain, limit=limit)

@mcp.tool()
@secure_tool()
def explore_model_relations(model: str, record_id: int, relation_field: str | None = None) -> dict[str, Any]:
    """
    Navigates linked records (Many2one, One2many, Many2many) across arbitrary tables.
    If relation_field is omitted, returns the record and a summary of all relational fields available on this record.
    If relation_field is provided, it reads the related records automatically.
    """
    repo, _ = _get_tenant_service()
    fields_info = repo.get_model_fields(model)
    
    # Just reading the single record
    records = repo.search_read_records(model, domain=[["id", "=", record_id]], limit=1)
    if not records:
        return {"status": "error", "message": f"Record {record_id} not found in model {model}"}
        
    record = records[0]
    
    if not relation_field:
        # Summarize available relations
        relations = {}
        for fname, finfo in fields_info.items():
            ftype = finfo.get("type")
            if ftype in ("many2one", "one2many", "many2many"):
                val = record.get(fname)
                relations[fname] = {
                    "type": ftype,
                    "target_model": finfo.get("relation"),
                    "value": val
                }
        return {
            "record": record,
            "available_relations": relations,
            "suggestion": "Call explore_model_relations again with a specific relation_field to fetch the linked records."
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
        # val is typically [id, "name"]
        target_id = val[0] if isinstance(val, (list, tuple)) else val
        return {"status": "success", "data": repo.search_read_records(target_model, domain=[["id", "=", target_id]], limit=1)}
        
    elif ftype in ("one2many", "many2many"):
        # val is a list of IDs
        return {"status": "success", "data": repo.search_read_records(target_model, domain=[["id", "in", val]], limit=50)}
        
    return {"status": "error", "message": "Unhandled relation type"}
