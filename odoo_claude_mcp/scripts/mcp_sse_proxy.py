#!/usr/bin/env python3
"""
MCP SSE Proxy for Odoo

This script runs a lightweight ASGI server using Starlette.
It exposes Server-Sent Events (SSE) endpoints that Claude Connectors can connect to.
When Claude calls a tool via SSE, this proxy forwards the request to the Odoo JSON-RPC endpoints.
"""

import os

import httpx
import uvicorn
from mcp.server import Server
from mcp.server.sse import SseServerTransport
from mcp.types import TextContent, Tool
from starlette.applications import Starlette
from starlette.routing import Route

# Configuration via environment variables
ODOO_URL = os.getenv("ODOO_URL", "http://localhost:8069")
ODOO_DB = os.getenv("ODOO_DB", "odoo")
ODOO_USER = os.getenv("ODOO_USER", "admin")
ODOO_PASS = os.getenv("ODOO_PASS", "admin")
PORT = int(os.getenv("PORT", 8080))
HOST = os.getenv("HOST", "0.0.0.0")

app = Server("odoo-mcp-sse-proxy")

def _jsonrpc_call(endpoint: str, params: dict):
    """Forward a call to Odoo via JSON-RPC."""
    url = f"{ODOO_URL.rstrip('/')}{endpoint}"
    payload = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": params,
        "id": 1
    }
    
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
        # Authenticate
        auth_resp = client.post(f"{ODOO_URL.rstrip('/')}/web/session/authenticate", json=auth_payload)
        auth_resp.raise_for_status()
        
        # Call the actual tool endpoint
        resp = client.post(url, json=payload)
        resp.raise_for_status()
        return resp.json()

@app.list_tools()
async def list_tools() -> list[Tool]:
    """Fetch available tools from Odoo and register them."""
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

# --- SSE Integration (Starlette) ---
sse = SseServerTransport("/messages")

async def handle_sse(request):
    """Handle initial SSE connection."""
    async with sse.connect_sse(
        request.scope, request.receive, request._send
    ) as streams:
        await app.run(
            streams[0], streams[1], app.create_initialization_options()
        )

async def handle_messages(request):
    """Handle incoming POST messages from Claude."""
    await sse.handle_post_message(
        request.scope, request.receive, request._send
    )

starlette_app = Starlette(
    debug=True,
    routes=[
        Route("/sse", endpoint=handle_sse),
        Route("/messages", endpoint=handle_messages, methods=["POST"]),
    ],
)

if __name__ == "__main__":
    print(f"Starting SSE Proxy at http://{HOST}:{PORT}/sse")
    uvicorn.run(starlette_app, host=HOST, port=PORT)
