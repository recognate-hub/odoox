import asyncio
import contextvars
import threading

import uvicorn
from mcp.server.fastmcp import FastMCP
from mcp.server.sse import SseServerTransport
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import Route

cv = contextvars.ContextVar("cv", default=None)
mcp = FastMCP("test")

@mcp.tool()
def test_tool() -> str:
    val = cv.get()
    return f"ContextVar is: {val}"

sse = SseServerTransport("/messages")

class NoOpResponse(Response):
    async def __call__(self, scope, receive, send):
        pass

async def get_sse(request: Request):
    cv.set("HELLO_WORLD")
    async with sse.connect_sse(request.scope, request.receive, request._send) as streams:
        await mcp._mcp_server.run(streams[0], streams[1], mcp._mcp_server.create_initialization_options())
    return NoOpResponse()

async def post_messages(request: Request):
    await sse.handle_post_message(request.scope, request.receive, request._send)
    return NoOpResponse()

app = Starlette(routes=[
    Route("/sse", endpoint=get_sse, methods=["GET"]),
    Route("/messages", endpoint=post_messages, methods=["POST"]),
])

def run_server():
    uvicorn.run(app, host="127.0.0.1", port=9999, log_level="error")

async def run_client():
    from mcp.client.session import ClientSession
    from mcp.client.sse import sse_client
    async with sse_client("http://127.0.0.1:9999/sse") as streams:
        async with ClientSession(streams[0], streams[1]) as session:
            await session.initialize()
            result = await session.call_tool("test_tool", arguments={})
            print(f"Tool Result 1: {result.content}")
            result2 = await session.call_tool("test_tool", arguments={})
            print(f"Tool Result 2: {result2.content}")

if __name__ == "__main__":
    t = threading.Thread(target=run_server, daemon=True)
    t.start()
    import time
    time.sleep(1)
    asyncio.run(run_client())
