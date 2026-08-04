#!/usr/bin/env python3
import sys
import anyio
import argparse
from mcp.client.sse import sse_client
from mcp.client.session import ClientSession
from mcp.server.stdio import stdio_server

async def _pump(read_stream, write_stream):
    """Pipe messages between the client session and the stdio proxy streams."""
    try:
        async for message in read_stream:
            await write_stream.send(message)
    except Exception:
        pass

async def main(url: str):
    async with sse_client(url) as (sse_read, sse_write):
        async with stdio_server() as (stdio_read, stdio_write):
            # Run two concurrent tasks to pipe messages in both directions
            async with anyio.create_task_group() as tg:
                tg.start_soon(_pump, stdio_read, sse_write)
                tg.start_soon(_pump, sse_read, stdio_write)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="MCP SSE to Stdio Bridge")
    parser.add_argument("url", help="The SSE endpoint URL to connect to")
    args = parser.parse_args()
    
    anyio.run(main, args.url)
