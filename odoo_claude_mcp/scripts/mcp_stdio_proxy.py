#!/usr/bin/env python3
"""
MCP Stdio Proxy for Odoo

Claude Desktop runs this script locally. This script uses the official
`mcp` python SDK to expose tools over stdio to Claude Desktop.
When Claude calls a tool, this script forwards the call to the Odoo JSON-RPC endpoints.
"""

import sys
import os
import httpx
import anyio
from mcp.server import Server
from mcp.types import Tool, TextContent
from mcp.server.stdio import stdio_server

# Configuration via environment variables in claude_desktop_config.json
ODOO_URL = os.getenv("ODOO_URL", "http://localhost:8069")
ODOO_DB = os.getenv("ODOO_DB", "odoo")
ODOO_USER = os.getenv("ODOO_USER", "admin")
ODOO_PASS = os.getenv("ODOO_PASS", "admin")

app = Server("odoo-mcp-proxy")

def _jsonrpc_call(endpoint: str, params: dict):
    url = f"{ODOO_URL.rstrip('/')}{endpoint}"
    payload = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": params,
        "id": 1
    }
    
    # We must authenticate and pass a session cookie to the controller.
    # For simplicity in this proxy, we use basic XML-RPC to get a session ID,
    # or just use Odoo's /web/session/authenticate
    auth_payload = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "db": ODOO_DB,
            "login": ODOO_USER,
            "password": ODOO_PASS
        },
        "id": 1
    }
    
    with httpx.Client() as client:
        # 1. Authenticate
        auth_resp = client.post(f"{ODOO_URL.rstrip('/')}/web/session/authenticate", json=auth_payload)
        auth_resp.raise_for_status()
        
        # 2. Call endpoint
        resp = client.post(url, json=payload)
        resp.raise_for_status()
        return resp.json()

@app.list_tools()
async def list_tools() -> list[Tool]:
    """Fetch available tools from Odoo and register them with MCP."""
    resp = _jsonrpc_call("/mcp/tools", {})
    if "result" in resp and "tools" in resp["result"]:
        odoo_tools = resp["result"]["tools"]
        mcp_tools = []
        for t in odoo_tools:
            mcp_tools.append(Tool(
                name=t["name"],
                description=t["description"],
                inputSchema=t["inputSchema"]
            ))
        return mcp_tools
    return []

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Execute a tool by forwarding the request to Odoo."""
    resp = _jsonrpc_call("/mcp/call_tool", {"name": name, "arguments": arguments})
    
    if "result" in resp:
        res = resp["result"]
        if res.get("status") == "success":
            return [TextContent(type="text", text=str(res.get("result")))]
        else:
            return [TextContent(type="text", text=f"Error: {res.get('message')}")]
    
    if "error" in resp:
        return [TextContent(type="text", text=f"Odoo Error: {resp['error']}")]
        
    return [TextContent(type="text", text="Unknown error occurred.")]

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )

if __name__ == "__main__":
    anyio.run(main)
