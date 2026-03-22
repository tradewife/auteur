"""AUTEUR MCP server entry point with x402 payment middleware.

Usage (Railway):
    python -m auteur.start

Usage (local):
    python -m auteur.start

This replaces `fastmcp run auteur/server.py:mcp` to enable the x402
payment gate middleware in front of the MCP server.
"""

from __future__ import annotations

import os

import uvicorn

from auteur.server import mcp
from auteur.x402_middleware import X402Middleware


def create_app():
    """Create the ASGI app with x402 middleware wrapped around FastMCP."""
    inner = mcp.http_app()
    return X402Middleware(inner)


app = create_app()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)
