"""x402 ASGI middleware — payment gate for the AUTEUR MCP server.

Intercepts HTTP POST requests to the MCP endpoint.  If no valid X-Payment
header is present, returns HTTP 402 with payment requirements.  Otherwise
verifies the proof and passes the request through.

When X402_ENABLED is false or AUTEUR_WALLET is not set, the middleware
passes all requests through (development mode).
"""

from __future__ import annotations

import json
import logging

from auteur.config import get_settings
from auteur.x402_verify import PaymentError, verify_x402_payment

logger = logging.getLogger("auteur.x402")


class X402Middleware:
    """Raw ASGI middleware that enforces x402 payment on MCP requests."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        # Only intercept HTTP POST requests (MCP JSON-RPC calls)
        if scope["type"] != "http" or scope["method"] != "POST":
            await self.app(scope, receive, send)
            return

        settings = get_settings()

        # Development bypass: skip payment gate if not configured
        if not settings.x402_enabled:
            await self.app(scope, receive, send)
            return

        # Extract X-Payment header from ASGI scope
        headers = {}
        for key, value in scope.get("headers", []):
            headers[key.decode("utf-8", errors="replace").lower()] = value.decode("utf-8", errors="replace")

        payment_header = headers.get("x-payment", "")

        if not payment_header:
            await self._send_402(send, {
                "error": "Payment required",
                "code": "PAYMENT_REQUIRED",
                "amount": settings.shot_price_usdc,
                "asset": "ETH",
                "chain": "base-sepolia",
                "address": settings.auteur_wallet,
                "instructions": (
                    "Sign an AUTEUR payment with your wallet and include "
                    "the proof in the X-Payment header (base64-encoded JSON). "
                    "See AUTEUR docs for the EIP-712 Payment schema."
                ),
            })
            return

        # Verify payment proof
        try:
            proof = verify_x402_payment(
                payment_header,
                expected_recipient=settings.auteur_wallet,
                min_amount=settings.shot_price_usdc,
            )
            logger.info(
                "x402 payment verified: signer=%s amount=%s nonce=%d",
                proof.signer, proof.amount, proof.nonce,
            )
            # Store proof in ASGI scope for downstream use
            scope["x402_proof"] = proof
        except PaymentError as exc:
            logger.warning("x402 verification failed: %s — %s", exc.code, exc.message)
            await self._send_402(send, {
                "error": f"Payment verification failed: {exc.message}",
                "code": exc.code,
                "amount": settings.shot_price_usdc,
                "asset": "ETH",
                "chain": "base-sepolia",
                "address": settings.auteur_wallet,
            })
            return

        # Payment verified — pass through to FastMCP
        await self.app(scope, receive, send)

    @staticmethod
    async def _send_402(send, body: dict):
        """Send HTTP 402 Payment Required response."""
        body_bytes = json.dumps(body).encode("utf-8")
        await send({
            "type": "http.response.start",
            "status": 402,
            "headers": [
                [b"content-type", b"application/json"],
                [b"x-payment-required", b"true"],
            ],
        })
        await send({
            "type": "http.response.body",
            "body": body_bytes,
        })
