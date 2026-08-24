import asyncio
import sys
from mcp_app.server import mcp
from core.context import current_token

async def test():
    current_token.set("mock_token")
    print("Available tools:", [t.name for t in await mcp.list_tools()])
    # Try calling a generic tool
    try:
        result = await mcp.call_tool("get_installed_apps", arguments={})
        print("get_installed_apps result:", result)
    except Exception as e:
        print("Error calling get_installed_apps:", e)
        
if __name__ == "__main__":
    asyncio.run(test())
