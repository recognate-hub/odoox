import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from config.settings import get_settings
from routers.health import router as health_router
from routers.admin import router as admin_router
from routers.oauth import router as oauth_router
from core.logger import get_logger
from mcp_app.server import mcp
from mcp.server.sse import SseServerTransport
from fastapi import Request, Depends
from core.auth import get_tenant_context

logger = get_logger(__name__)

sse = SseServerTransport("/messages")

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up FastAPI server...")
    yield

def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="Odoo-Claude CRM Middleware",
        description="FastAPI application serving MCP tools and Admin Dashboard",
        version="1.0.0",
        lifespan=lifespan
    )
    
    # Add CORS middleware for the MCP Inspector
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Mount Static Files
    app.mount("/static", StaticFiles(directory="static"), name="static")
    
    # Include standard REST routers
    app.include_router(health_router, tags=["Health"])
    app.include_router(admin_router, tags=["Admin"])
    app.include_router(oauth_router, prefix="/oauth", tags=["OAuth"])
    
    # Expose MCP Server over SSE (Multi-Tenant Secure)
    @app.get("/sse", dependencies=[Depends(get_tenant_context)])
    async def handle_sse(request: Request):
        async with sse.connect_sse(
            request.scope, request.receive, request._send
        ) as streams:
            await mcp._mcp_server.run(
                streams[0], streams[1], mcp._mcp_server.create_initialization_options()
            )
        return NoOpResponse()

    from starlette.responses import Response

    class NoOpResponse(Response):
        async def __call__(self, scope, receive, send):
            pass

    @app.post("/messages")
    async def handle_messages(request: Request):
        await sse.handle_post_message(
            request.scope, request.receive, request._send
        )
        return NoOpResponse()

    return app

app = create_app()

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
