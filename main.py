import uvicorn
from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from mcp.server.sse import SseServerTransport

from config.settings import get_settings
from core.auth import get_tenant_context
from core.logger import get_logger
from mcp_app.server import mcp
from routers.admin import router as admin_router
from routers.health import router as health_router
from routers.oauth import router as oauth_router
from routers.oauth_metadata import router as oauth_metadata_router

logger = get_logger(__name__)

sse = SseServerTransport("/messages")

from contextlib import asynccontextmanager

try:
    from opentelemetry import trace
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor

    # Initialize OpenTelemetry Tracer
    resource = Resource.create({"service.name": "odoox-gateway"})
    provider = TracerProvider(resource=resource)

    # Only add OTLP exporter if endpoint is configured
    import os
    if os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT"):
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import (
            OTLPSpanExporter,
        )
        otlp_exporter = OTLPSpanExporter()
        provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
        logger.info("OTLP exporter configured.")

    trace.set_tracer_provider(provider)
    tracer = trace.get_tracer(__name__)
    _otel_available = True
    logger.info("OpenTelemetry initialized successfully.")
except Exception as e:
    logger.exception(f"OpenTelemetry initialization failed: {e}. Tracing disabled.")
    _otel_available = False
    tracer = None

from core.rate_limit import get_rate_limiter, init_rate_limiter


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up FastAPI server...")
    await init_rate_limiter()
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
    app.include_router(oauth_metadata_router, tags=["OAuth Metadata"])
    
    @app.get("/", tags=["Root"])
    async def get_root():
        return {
            "service": "OdooX API Gateway",
            "status": "online",
            "version": "1.0.0",
            "message": "This is the headless API for OdooX. The frontend must be hosted separately via the Next.js application."
        }
    
    # Expose MCP Server over SSE (Multi-Tenant Secure)
    @app.get("/sse", dependencies=[Depends(get_tenant_context), get_rate_limiter(times=50, seconds=60)])
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

    @app.post("/messages", dependencies=[get_rate_limiter(times=50, seconds=60)])
    async def handle_messages_post(request: Request):
        # We DO NOT call get_tenant_context here because the MCP client (Claude) 
        # POSTs to this endpoint with only a sessionId, not the token. 
        # Security is maintained because the sessionId is a secure UUID, and the 
        # actual tool execution runs in the context of the GET /sse request which IS authenticated.
        class ASGIProxyResponse(Response):
            async def __call__(self, scope, receive, send):
                await sse.handle_post_message(scope, receive, send)
        return ASGIProxyResponse()

    @app.post("/sse", dependencies=[get_rate_limiter(times=50, seconds=60)])
    async def handle_sse_post(request: Request):
        body = await request.body()
        logger.info(f"POST /sse body: {body}")
        
        await get_tenant_context(request)
        class ASGIProxyResponse(Response):
            async def __call__(self, scope, receive, send):
                # We consumed the body, so we need to inject it back for sse.handle_post_message
                # But actually, sse.handle_post_message expects to read from receive.
                # Let's just pass it, but since body is consumed, receive will yield nothing.
                # To avoid breaking it, let's just use a custom receive.
                async def custom_receive():
                    return {"type": "http.request", "body": body, "more_body": False}
                await sse.handle_post_message(scope, custom_receive, send)
        return ASGIProxyResponse()

    # Instrument FastAPI with OpenTelemetry (if available)
    if _otel_available:
        FastAPIInstrumentor.instrument_app(app)

    return app

app = create_app()

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
