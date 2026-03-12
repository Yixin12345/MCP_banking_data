"""ASGI entrypoint for deploying FastAPI + MCP streamable HTTP on Render."""

from contextlib import asynccontextmanager
import os

from starlette.applications import Starlette
from starlette.responses import RedirectResponse
from starlette.routing import Route
from starlette.routing import Mount

from fastapi_app.app import app as fastapi_app
from main import mcp

# Mounted at /mcp, so MCP endpoint should be the mount root.
mcp.settings.streamable_http_path = "/"
if os.getenv("MCP_DISABLE_DNS_REBINDING_PROTECTION", "true").lower() in {"1", "true", "yes"}:
    mcp.settings.transport_security.enable_dns_rebinding_protection = False


@asynccontextmanager
async def lifespan(_: Starlette):
    async with mcp.session_manager.run():
        yield


async def redirect_mcp(_):
    return RedirectResponse(url="/mcp/", status_code=307)


app = Starlette(
    routes=[
        Route("/mcp", endpoint=redirect_mcp, methods=["GET", "POST", "OPTIONS"]),
        Mount("/mcp", app=mcp.streamable_http_app()),
        Mount("/", app=fastapi_app),
    ],
    lifespan=lifespan,
)
