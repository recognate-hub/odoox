from typing import Any
from core.logger import get_logger
from mcp_app import server
from mcp_app.schemas import *
from mcp_app.security import secure_tool
from mcp_app.server import _span, mcp
from mcp_app.validation import validate_write_input

logger = get_logger(__name__)


@mcp.tool()
@secure_tool()
def get_sales_dashboard() -> dict[str, Any]:
    """
    Get the current sales dashboard metrics.
    (Note: This tool provides identical data to revenue_report).

    Returns:
        Dict[str, Any]: A dictionary containing total_revenue, active_leads_count, quotes_count, and win_rate_percentage.
    """
    logger.info("MCP Tool Called: get_sales_dashboard")
    odoo_repo, _ = server._get_tenant_service()
    dashboard = odoo_repo.get_dashboard()
    return dashboard.model_dump()


@mcp.tool()
@secure_tool()
def search_read_records(
    model: str,
    domain: list[list[Any]] | None = None,
    fields: list[str] | None = None,
    limit: int = 50,
    offset: int = 0,
    summarize: bool = False,
    expand_fields: list[str] | None = None,
) -> list[dict[str, Any]] | dict[str, Any]:
    """
    Generic tool to read records from ANY Odoo module or model.
    
    Use this tool when:
    - The data needed is not covered by a specialized tool (like HR, Project, Manufacturing).
    - The user asks for data from a specific Odoo table/model.

    Args:
        model (str): The name of the Odoo model (e.g., 'hr.employee', 'project.task', 'mrp.production').
        domain (list): A list of search criteria to filter records. For example: [["name", "ilike", "John"]].
        fields (list): A list of fields to return. If omitted, returns all fields.
        limit (int): The maximum number of records to return (max 200).
        offset (int): The number of records to skip for pagination.
        expand_fields (list): Optional list of relational field paths to expand (e.g., ["order_line", "partner_id"]). 

    Returns:
        list: A list of dictionaries representing the records matching the domain.
    """
    logger.info("MCP Tool Called: search_read_records", model=model, domain=domain)
    odoo_repo, _ = server._get_tenant_service()
    limit = min(limit, 200)
    if model == "ir.attachment" and (not fields):
        fields = [
            "name",
            "res_model",
            "res_id",
            "type",
            "mimetype",
            "url",
            "file_size",
            "checksum",
            "create_date",
        ]
    if not fields and limit > 5:
        logger.warning(
            f"search_read_records on {model} called without fields. Reducing limit from {limit} to 5 to prevent Odoo timeouts."
        )
        limit = 5
    try:
        results = odoo_repo.search_read_records(
            model, domain=domain, fields=fields, limit=limit, offset=offset, expand_fields=expand_fields
        )
        if summarize:
            return {
                "metadata": {
                    "total_returned": len(results),
                    "model": model,
                    "domain": domain,
                },
                "data": results,
                "summary": f"Found {len(results)} records for model {model}.",
            }
        return results
    except Exception as e:
        logger.error("search_read_records error", error=str(e))
        raise RuntimeError(f"Odoo search_read_records failed: {e!s}") from e


@mcp.tool()
@secure_tool()
def count_records(model: str, domain: list[list[Any]] | None = None) -> dict[str, Any]:
    """
    Count records matching a domain without fetching them.

    Args:
        model (str): The name of the Odoo model.
        domain (list): A list of search criteria to filter records.

    Returns:
        dict: A dictionary containing the count of matching records.
    """
    logger.info("MCP Tool Called: count_records", model=model, domain=domain)
    odoo_repo, _ = server._get_tenant_service()
    try:
        count = odoo_repo.execute_method(model, "search_count", [domain or []])
        return {"status": "success", "count": count}
    except Exception as e:
        logger.error("count_records error", error=str(e))
        return {"status": "error", "message": str(e)}


@mcp.tool()
@secure_tool()
@validate_write_input(BatchCreateRecordInput)
def batch_create_records(model: str, records: list[dict[str, Any]]) -> dict[str, Any]:
    """
    Generic tool to create multiple records in ANY Odoo module or model in a single API call.

    Args:
        model (str): The name of the Odoo model.
        records (list): A list of dictionaries mapping field names to values for each record.

    Returns:
        dict: Status and IDs of the newly created records.
    """
    logger.info(
        "MCP Tool Called: batch_create_records", model=model, count=len(records)
    )
    odoo_repo, _ = server._get_tenant_service()
    try:
        record_ids = odoo_repo.batch_create_records(model, records)
        return {"status": "success", "record_ids": record_ids}
    except Exception as e:
        logger.error("batch_create_records error", error=str(e))
        return {"status": "error", "message": str(e)}


@mcp.tool()
@secure_tool()
@validate_write_input(BatchUpdateRecordInput)
def batch_update_records(
    model: str, record_ids: list[int], data: dict[str, Any]
) -> dict[str, Any]:
    """
    Generic tool to update multiple records with the SAME data in ANY Odoo module or model.

    Args:
        model (str): The name of the Odoo model.
        record_ids (list): A list of record IDs to update.
        data (dict): A dictionary of fields and values to apply to all specified records.

    Returns:
        dict: Status of the update operation.
    """
    logger.info(
        "MCP Tool Called: batch_update_records", model=model, count=len(record_ids)
    )
    odoo_repo, _ = server._get_tenant_service()
    try:
        success = odoo_repo.batch_update_records(model, record_ids, data)
        return (
            {"status": "success"}
            if success
            else {"status": "error", "message": "Batch update failed"}
        )
    except Exception as e:
        logger.error("batch_update_records error", error=str(e))
        return {"status": "error", "message": str(e)}


@mcp.tool()
@secure_tool()
def get_installed_apps() -> list[dict[str, Any]]:
    """
    Retrieve a list of installed applications/modules in the Odoo instance.

    Returns:
        List[Dict[str, Any]]: A list of installed apps.
    """
    with _span("mcp.get_installed_apps"):
        logger.info("MCP Tool Called: get_installed_apps")
        odoo_repo, _ = server._get_tenant_service()
        return odoo_repo.get_installed_apps()


@mcp.tool()
@secure_tool()
def check_stock_availability(product_id: int) -> list[dict[str, Any]]:
    """
    Check the stock availability for a specific product across all locations.

    Args:
        product_id (int): The ID of the product in Odoo.

    Returns:
        List[Dict[str, Any]]: A list of stock quantities per location.
    """
    with _span("mcp.check_stock_availability") as span:
        if span:
            span.set_attribute("product_id", product_id)
        logger.info("MCP Tool Called: check_stock_availability", product_id=product_id)
        odoo_repo, _ = server._get_tenant_service()
        return odoo_repo.get_product_stock(product_id)


@mcp.tool()
@secure_tool()
@validate_write_input(GetModelFieldsInput)
def get_model_fields(model: str) -> dict[str, Any]:
    """
    Get the schema and all available fields for a specific Odoo model (e.g., 'stock.lot', 'hr.employee').
    
    Use this tool when:
    - You need to know the correct field names before writing a domain filter or executing search_read_records.
    - The user asks what data fields are available for a given module.

    Args:
        model (str): The Odoo model name to inspect.

    Returns:
        dict: A dictionary mapping field names to their metadata (type, string label, selection options, etc.).
    """
    logger.info("MCP Tool Called: get_model_fields", model=model)
    odoo_repo, _ = server._get_tenant_service()
    try:
        return odoo_repo.get_model_fields(model)
    except Exception as e:
        logger.error("get_model_fields error", error=str(e))
        return {"status": "error", "message": str(e)}


@mcp.tool()
@secure_tool()
@validate_write_input(ReadGroupInput)
def read_group_records(
    model: str,
    domain: list[list[Any]] | None = None,
    fields: list[str] | None = None,
    groupby: list[str] | None = None,
) -> list[dict[str, Any]]:
    """
    Perform a read_group operation on an Odoo model for aggregation (e.g., sum, count).

    Args:
        model (str): The Odoo model name.
        domain (list): Search criteria.
        fields (list): Fields to fetch/aggregate.
        groupby (list): Fields to group by.

    Returns:
        list: A list of aggregated records.
    """
    logger.info("MCP Tool Called: read_group_records", model=model, groupby=groupby)
    odoo_repo, _ = server._get_tenant_service()
    try:
        return odoo_repo.read_group(
            model, domain=domain or [], fields=fields or [], groupby=groupby or []
        )
    except Exception as e:
        logger.error("read_group_records error", error=str(e))
        return [{"status": "error", "message": f"read_group on {model} failed: {e}"}]


@mcp.tool()
@secure_tool()
def get_attachment(attachment_id: int) -> dict[str, Any]:
    """
    Fetch an attachment from Odoo (ir.attachment).
    Base64 data is truncated if it's too large to prevent context limits.

    Args:
        attachment_id (int): The ID of the attachment.

    Returns:
        dict: The attachment data including base64 content.
    """
    logger.info("MCP Tool Called: get_attachment", attachment_id=attachment_id)
    odoo_repo, _ = server._get_tenant_service()
    try:
        attachment = odoo_repo.get_attachment(attachment_id)
        if attachment.get("datas") and len(attachment["datas"]) > 100000:
            attachment["datas"] = attachment["datas"][:100000] + "...[TRUNCATED]"
            attachment["_truncated"] = True
        return attachment
    except Exception as e:
        logger.error("get_attachment error", error=str(e))
        return {"status": "error", "message": str(e)}


@mcp.tool()
@secure_tool()
@validate_write_input(ExecuteMethodInput)
def execute_model_method(
    model: str,
    method: str,
    args: list[Any] | None = None,
    kwargs: dict[str, Any] | None = None,
) -> Any:
    """
    Execute any arbitrary method on an Odoo model.
    This allows you to trigger Odoo workflows (e.g. 'action_confirm' on a sales order, 'action_post' on an invoice).
    """
    logger.info("MCP Tool Called: execute_model_method", model=model, method=method)
    odoo_repo, _ = server._get_tenant_service()
    try:
        return odoo_repo.execute_method(model, method, args, kwargs)
    except Exception as e:
        logger.error("execute_model_method error", error=str(e))
        raise RuntimeError(f"Failed to execute method {method} on {model}: {e}")


@mcp.tool()
@secure_tool()
@validate_write_input(BatchImportCsvInput)
def batch_import_csv(model: str, csv_data: str) -> dict[str, Any]:
    """
    Import data into Odoo by parsing CSV data and creating records in bulk.
    The first row of the CSV must contain the exact Odoo field names.
    """
    import csv
    import io

    logger.info("MCP Tool Called: batch_import_csv", model=model)
    odoo_repo, _ = server._get_tenant_service()
    try:
        f = io.StringIO(csv_data.strip())
        reader = csv.DictReader(f)
        records = list(reader)
        if not records:
            return {
                "status": "error",
                "message": "CSV data is empty or missing headers.",
            }
        record_ids = odoo_repo.batch_create_records(model, records)
        return {
            "status": "success",
            "imported_count": len(record_ids),
            "record_ids": record_ids,
        }
    except Exception as e:
        logger.error("batch_import_csv error", error=str(e))
        return {"status": "error", "message": str(e)}


@mcp.tool()
@secure_tool()
def get_tool_guide() -> dict[str, Any]:
    """
    Retrieve the exact tool guide and prompt instructions for this MCP server.
    
    Use this tool when you need a refresher on how to chain tools together,
    which tools to use for specific scenarios, or how to handle module errors.
    """
    import os
    from config.settings import get_settings
    
    logger.info("MCP Tool Called: get_tool_guide")
    try:
        # Resolve the root directory (where claude_prompt.txt is located)
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        prompt_path = os.path.join(base_dir, "claude_prompt.txt")
        
        with open(prompt_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        return {"status": "success", "content": content}
    except Exception as e:
        logger.error("get_tool_guide error", error=str(e))
        return {"status": "error", "message": "Failed to read tool guide: " + str(e)}


if __name__ == "__main__":
    pass
