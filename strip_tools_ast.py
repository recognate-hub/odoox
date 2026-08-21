import ast
import sys
import os

files_to_methods = {
    "sales.py": ["create_quote"],
    "quality.py": ["create_quality_alert", "update_quality_alert"],
    "purchase.py": ["create_purchase_order", "update_purchase_order", "confirm_purchase_order"],
    "production.py": ["create_manufacturing_order", "update_manufacturing_order", "confirm_manufacturing_order", "create_eco"],
    "maintenance.py": ["create_maintenance_request", "schedule_preventative_maintenance"],
    "invoicing.py": ["create_invoice", "post_invoice", "register_payment"],
    "inventory.py": ["create_product", "create_stock_move"],
    "generic.py": ["create_record", "update_record", "create_sales_invoice", "archive_record", "create_attachment"],
    "discuss.py": ["send_email", "post_message", "create_channel"],
    "crm.py": ["create_lead", "update_lead"],
    "contacts.py": ["create_contact"],
    "calendar.py": ["schedule_meeting", "update_meeting", "delete_meeting"]
}

for filename, methods in files_to_methods.items():
    filepath = os.path.join("mcp_app", "tools", filename)
    if not os.path.exists(filepath):
        continue
        
    with open(filepath, "r", encoding="utf-8") as f:
        source = f.read()
        
    try:
        tree = ast.parse(source)
    except SyntaxError:
        print(f"Syntax error in {filename}")
        continue
        
    class NodeRemover(ast.NodeTransformer):
        def visit_FunctionDef(self, node):
            if node.name in methods:
                return None # Remove it
            return node
            
    transformer = NodeRemover()
    new_tree = transformer.visit(tree)
    ast.fix_missing_locations(new_tree)
    
    # ast.unparse requires python 3.9+
    new_source = ast.unparse(new_tree)
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(new_source)
        
print("Done stripping using AST.")
