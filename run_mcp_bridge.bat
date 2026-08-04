@echo off
cd /d "D:\Work Space\Project\Odoo"
poetry run python odoo_claude_mcp\scripts\mcp_sse_bridge.py %*
