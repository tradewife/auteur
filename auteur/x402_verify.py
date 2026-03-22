"""x402 payment verification — validates EIP-712 / personal_sign payment proofs.

The x402 protocol requires clients to include a signed payment proof in the
X-Payment header.  This module verifies that proof end-to-end:

  1. Decode base64 header → JSON payload
  2. Check amount, asset, chain, recipient, expiry
  3. Replay protection (in-memory nonce set)
  4. Recover signer from ECDSA signature over typed EIP-712 hash
  5. Return structured PaymentProof on success

No stubs.  Every check is real.
"""

from __future__ import annotations

import base64
import json
import time
from dataclasses import dataclass, field

from eth_account import Account
from eth_account.messages import encode_defunct, encode_typed_data
from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# EIP-712 type definition for AUTEUR payments
AUTEUR_PAYMENT_TYPES = {
    "EIP712Domain": [
        {"name": "name", "type": "string"},
        {"name": "version", "type": "string"},
        {"name": "chainId", "type": "uint256"},
        {"name": "verifyingContract", "type": "address"},
    ],
    "Payment": [
        {"name": "amount", "type": "uint256"},
        {"name": "asset", "type": "string"},
        {"name": "recipient", "type": "address"},
        {"name": "nonce", "type": "uint256"},
        {"name": "expiry", "type": "uint256"},
    ],
}

AUTEUR_DOMAIN = {
    "name": "AUTEUR Payment",
    "version": "1",
    # chainId is injected dynamically from settings
    "chainId": 84532,  # Base Sepolia
}

# ---------------------------------------------------------------------------
# In-memory replay protection
# ---------------------------------------------------------------------------

_used_nonces: set[int] = set()
_MAX_NONCE_CACHE = 10_000


def _check_nonce(nonce: int) -> None:
    """Reject duplicate nonces.  Evicts oldest entries when cache is full."""
    if nonce in _used_nonces:
        raise PaymentError("nonce_already_used", f"Nonce {nonce} was already used")
    if len(_used_nonces) >= _MAX_NONCE_CACHE:
        # Evict the oldest ~half to avoid unbounded growth
        to_remove = list(_used_nonces)[: _MAX_NONCE_CACHE // 2]
        for n in to_remove:
            _used_nonces.discard(n)
    _used_nonces.add(nonce)


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------


class PaymentError(Exception):
    """Raised when payment verification fails."""

    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message
        super().__init__(message)


class PaymentPayload(BaseModel):
    """The decoded payment proof payload from the X-Payment header."""

    signature: str = Field(description="0x-prefixed ECDSA signature (65 bytes)")
    signer: str = Field(description="0x-prefixed signer address (recovered)")
    amount: str = Field(description="Payment amount as string integer (wei)")
    asset: str = Field(default="ETH", description="Asset ticker: ETH or USDC")
    chain: str = Field(default="base-sepolia", description="Chain identifier")
    recipient: str = Field(description="0x-prefixed recipient address")
    nonce: int = Field(description="Unique nonce to prevent replay")
    expiry: int = Field(description="Unix timestamp after which proof expires")
    tx_hash: str | None = Field(
        default=None,
        description="Optional onchain payment tx hash for additional verification",
    )


@dataclass
class PaymentProof:
    """Verified payment proof — returned on successful verification."""

    signer: str
    amount: str
    asset: str
    chain: str
    recipient: str
    nonce: int
    expiry: int
    tx_hash: str | None = None


# ---------------------------------------------------------------------------
# Verification
# ---------------------------------------------------------------------------


def decode_header(raw_header: str) -> PaymentPayload:
    """Decode the X-Payment header value (base64 JSON) into a PaymentPayload."""
    if not raw_header:
        raise PaymentError("missing_header", "X-Payment header is empty")

    try:
        decoded = base64.b64decode(raw_header.strip(), validate=True)
        data = json.loads(decoded)
    except (ValueError, json.JSONDecodeError) as exc:
        raise PaymentError("invalid_encoding", f"Cannot decode X-Payment header: {exc}")

    try:
        return PaymentPayload.model_validate(data)
    except Exception as exc:
        raise PaymentError("invalid_payload", f"Invalid payment payload: {exc}")


def verify_payload(
    payload: PaymentPayload,
    *,
    expected_recipient: str,
    min_amount: str,
    accepted_chain: str = "base-sepolia",
    accepted_assets: tuple[str, ...] = ("ETH", "USDC"),
    now: int | None = None,
) -> None:
    """Check amount, asset, chain, recipient, expiry, nonce.

    Raises PaymentError on any failure.  Returns None on success.
    """
    ts = now or int(time.time())

    # Chain check
    if payload.chain != accepted_chain:
        raise PaymentError(
            "wrong_chain",
            f"Expected chain '{accepted_chain}', got '{payload.chain}'",
        )

    # Asset check
    if payload.asset.upper() not in (a.upper() for a in accepted_assets):
        raise PaymentError(
            "unsupported_asset",
            f"Accepted assets: {accepted_assets}, got '{payload.asset}'",
        )

    # Recipient check (case-insensitive address comparison)
    if payload.recipient.lower() != expected_recipient.lower():
        raise PaymentError(
            "wrong_recipient",
            f"Payment must be sent to {expected_recipient}, got {payload.recipient}",
        )

    # Amount check (integer string comparison)
    try:
        if int(payload.amount) < int(min_amount):
            raise PaymentError(
                "insufficient_amount",
                f"Minimum payment is {min_amount} wei, got {payload.amount}",
            )
    except ValueError:
        raise PaymentError("invalid_amount", f"Amount must be an integer string, got '{payload.amount}'")

    # Expiry check
    if payload.expiry < ts:
        raise PaymentError(
            "payment_expired",
            f"Payment expired at {payload.expiry}, current time is {ts}",
        )

    # Nonce replay check
    _check_nonce(payload.nonce)


def verify_signature(payload: PaymentPayload) -> str:
    """Verify the ECDSA signature and recover the signer address.

    Uses EIP-712 typed data signing.  Falls back to personal_sign if the
    EIP-712 verification fails (backward compatibility).

    Returns the recovered signer address (0x-prefixed, checksummed).

    Raises PaymentError if signature is invalid or does not match claimed signer.
    """
    domain = {**AUTEUR_DOMAIN, "verifyingContract": payload.recipient}

    typed_data = {
        "types": AUTEUR_PAYMENT_TYPES,
        "domain": domain,
        "primaryType": "Payment",
        "message": {
            "amount": int(payload.amount),
            "asset": payload.asset,
            "recipient": payload.recipient,
            "nonce": payload.nonce,
            "expiry": payload.expiry,
        },
    }

    # Attempt EIP-712 typed data verification
    try:
        encode_typed_data(full_message=typed_data)
        recovered = Account.recover_message(encode_typed_data(full_message=typed_data), signature=payload.signature)
        return recovered
    except Exception:
        pass  # Fall through to personal_sign

    # Fallback: personal_sign verification
    # The message that was signed:
    sign_message = (
        f"AUTEUR Payment\n"
        f"Amount: {payload.amount}\n"
        f"Asset: {payload.asset}\n"
        f"Recipient: {payload.recipient}\n"
        f"Nonce: {payload.nonce}\n"
        f"Expiry: {payload.expiry}"
    )

    try:
        msg_hash = encode_defunct(text=sign_message)
        recovered = Account.recover_message(msg_hash, signature=payload.signature)
        return recovered
    except Exception as exc:
        raise PaymentError(
            "invalid_signature",
            f"Signature verification failed: {exc}",
        )


def verify_x402_payment(
    raw_header: str,
    *,
    expected_recipient: str,
    min_amount: str,
) -> PaymentProof:
    """Full x402 payment verification pipeline.

    1. Decode base64 header
    2. Validate payload fields (amount, chain, recipient, expiry, nonce)
    3. Verify ECDSA signature (EIP-712 or personal_sign fallback)
    4. Cross-check recovered signer matches claimed signer
    5. Return PaymentProof

    Raises PaymentError on any failure.
    """
    payload = decode_header(raw_header)

    verify_payload(
        payload,
        expected_recipient=expected_recipient,
        min_amount=min_amount,
    )

    recovered_signer = verify_signature(payload)

    # Cross-check: recovered signer must match claimed signer
    if payload.signer and payload.signer.lower() != recovered_signer.lower():
        raise PaymentError(
            "signer_mismatch",
            f"Claimed signer {payload.signer} does not match recovered {recovered_signer}",
        )

    return PaymentProof(
        signer=recovered_signer,
        amount=payload.amount,
        asset=payload.asset,
        chain=payload.chain,
        recipient=payload.recipient,
        nonce=payload.nonce,
        expiry=payload.expiry,
        tx_hash=payload.tx_hash,
    )
