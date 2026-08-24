import asyncio
import sys
import os

sys.path.append(os.path.abspath("."))
from mcp_app.server import mcp
from core.context import current_token

async def main():
    current_token.set("mock_token")
    try:
        result = await mcp.call_tool("get_installed_apps", arguments={})
        for app in result:
            print(f"- {app.get('name', 'Unknown')}: {app.get('desc', '')} (Category: {app.get('category', 'Unknown')})")
    except Exception as e:
        print("Error:", e)
        
if __name__ == "__main__":
    asyncio.run(main())
