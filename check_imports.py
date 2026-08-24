import os
import ast

tools_dir = "d:/Work Space/Project/Odoo/mcp_app/tools"

for filename in os.listdir(tools_dir):
    if filename.endswith(".py") and not filename.startswith("__"):
        filepath = os.path.join(tools_dir, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        
        has_span_usage = "_span" in content
        has_span_import = "_span" in content and ("import _span" in content or "import mcp, _span" in content or "_span, mcp" in content or "_span" in [node.name for node in ast.walk(ast.parse(content)) if isinstance(node, ast.alias)])
        
        tree = ast.parse(content)
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
        
        has_span_import_ast = "_span" in imports
        
        if has_span_usage and not has_span_import_ast:
            print(f"File {filename} uses _span but does NOT import it!")
