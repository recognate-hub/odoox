#!/usr/bin/env python3
import argparse

import anyio
from mcp.client.sse import sse_client
from mcp.server.stdio import stdio_server


async def _pump(read_stream, write_stream):
    """Pipe messages between the client session and the stdio proxy streams."""
    try:
        async for message in read_stream:
            if isinstance(message, Exception):
                import sys

                print(f"[mcp_sse_bridge] Stream error: {message}", file=sys.stderr)
                break
            await write_stream.send(message)
    except Exception:
        pass


async def main(url: str):
    from urllib.parse import parse_qs, urlparse

    parsed = urlparse(url)
    qs = parse_qs(parsed.query)
    headers = {}
    if qs.get("token"):
        headers["Authorization"] = f"Bearer {qs['token'][0]}"

    async with sse_client(url, headers=headers) as (sse_read, sse_write):
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
