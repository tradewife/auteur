"""x402 settlement — calls spend() on the auteur.sol contract after generation.

After a brief is successfully processed and a video is generated, this module
finalizes the onchain payment by calling the spend() function on the deployed
auteur.sol contract (Base Sepolia).

The spend() function:
  spend(address agentId, string taskId, uint256 amount, string cid)

This emits a SpendReceipt event that serves as the onchain proof of delivery.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass

import httpx
from eth_account import Account
from eth_account.messages import encode_defunct
from eth_abi import encode


# Base Sepolia chain ID
BASE_SEPOLIA_CHAIN_ID = 84532


@dataclass
class SettleResult:
    """Result of onchain spend() call."""

    success: bool
    tx_hash: str | None = None
    block_number: int | None = None
    error: str | None = None


def _build_spend_calldata(
    agent_id: str,
    task_id: str,
    amount: int,
    cid: str,
) -> bytes:
    """ABI-encode the spend() function call.

    Function signature: spend(address, string, uint256, string)
    Selector: 0x0eff02ca (keccak256("spend(address,string,uint256,string)")[:4])
    """
    # Function selector
    selector = bytes.fromhex("0eff02ca")

    # ABI encode arguments
    agent_id_bytes = bytes.fromhex(agent_id.replace("0x", "").zfill(64))
    amount_bytes = amount.to_bytes(32, byteorder="big")

    # String encoding: offset(32) + length(32) + padded data
    task_id_encoded = _encode_string(task_id)
    cid_encoded = _encode_string(cid)

    return selector + agent_id_bytes + task_id_encoded + amount_bytes + cid_encoded


def _encode_string(s: str) -> bytes:
    """ABI-encode a single string (dynamic type)."""
    encoded = s.encode("utf-8")
    # Offset to data (32 bytes for offset + 32 bytes for length = 64)
    offset = 64
    padded = encoded.ljust((len(encoded) + 31) // 32 * 32, b"\x00")
    return offset.to_bytes(32, byteorder="big") + len(encoded).to_bytes(32, byteorder="big") + padded


def _get_base_sepolia_params(rpc_url: str, from_address: str) -> dict:
    """Fetch current gas price, nonce, and chain ID from the RPC."""
    with httpx.Client(timeout=15) as client:
        # Get nonce
        resp = client.post(
            rpc_url,
            json={
                "jsonrpc": "2.0",
                "method": "eth_getTransactionCount",
                "params": [from_address, "pending"],
                "id": 1,
            },
        )
        nonce = int(resp.json()["result"], 16)

        # Get gas price
        resp = client.post(
            rpc_url,
            json={
                "jsonrpc": "2.0",
                "method": "eth_gasPrice",
                "params": [],
                "id": 2,
            },
        )
        gas_price = int(resp.json()["result"], 16)

        # Get chain ID
        resp = client.post(
            rpc_url,
            json={
                "jsonrpc": "2.0",
                "method": "eth_chainId",
                "params": [],
                "id": 3,
            },
        )
        chain_id = int(resp.json()["result"], 16)

        # Get latest block (for gas limit estimation)
        resp = client.post(
            rpc_url,
            json={
                "jsonrpc": "2.0",
                "method": "eth_blockNumber",
                "params": [],
                "id": 4,
            },
        )
        block_number = int(resp.json()["result"], 16)

    return {
        "nonce": nonce,
        "gas_price": gas_price,
        "chain_id": chain_id,
        "block_number": block_number,
    }


def settle_spend(
    *,
    rpc_url: str,
    private_key: str,
    contract_address: str,
    agent_id: str,
    task_id: str,
    amount: int,
    cid: str,
) -> SettleResult:
    """Call spend() on the auteur.sol contract.

    Builds, signs, and broadcasts the transaction. Returns the tx hash
    on success or an error on failure.
    """
    try:
        account = Account.from_key(private_key)
        from_address = account.address

        # Fetch chain params
        params = _get_base_sepolia_params(rpc_url, from_address)

        # Build calldata
        calldata = _build_spend_calldata(agent_id, task_id, amount, cid)

        # Build transaction
        tx = {
            "chainId": params["chain_id"],
            "nonce": params["nonce"],
            "to": contract_address,
            "value": 0,
            "gas": 300_000,  # Conservative gas limit for spend()
            "maxFeePerGas": params["gas_price"] * 2,
            "maxPriorityFeePerGas": params["gas_price"],
            "data": calldata,
        }

        # Sign
        signed = account.sign_transaction(tx)
        raw_tx = signed.rawTransaction.hex()

        # Broadcast
        with httpx.Client(timeout=30) as client:
            resp = client.post(
                rpc_url,
                json={
                    "jsonrpc": "2.0",
                    "method": "eth_sendRawTransaction",
                    "params": [f"0x{raw_tx}"],
                    "id": 5,
                },
            )

        result = resp.json()
        if "error" in result:
            return SettleResult(
                success=False,
                error=f"RPC error: {json.dumps(result['error'])}",
            )

        tx_hash = result.get("result", "")
        if not tx_hash or not tx_hash.startswith("0x"):
            return SettleResult(success=False, error=f"Unexpected RPC response: {result}")

        # Wait for receipt
        receipt = _wait_for_receipt(rpc_url, tx_hash, timeout=60)

        return SettleResult(
            success=True,
            tx_hash=tx_hash,
            block_number=receipt.get("blockNumber"),
        )

    except Exception as exc:
        return SettleResult(success=False, error=str(exc))


def _wait_for_receipt(
    rpc_url: str, tx_hash: str, timeout: int = 60, poll_interval: float = 2.0
) -> dict:
    """Poll for transaction receipt until confirmed or timeout."""
    start = time.time()
    with httpx.Client(timeout=15) as client:
        while time.time() - start < timeout:
            resp = client.post(
                rpc_url,
                json={
                    "jsonrpc": "2.0",
                    "method": "eth_getTransactionReceipt",
                    "params": [tx_hash],
                    "id": 1,
                },
            )
            result = resp.json().get("result")
            if result is not None:
                return result
            time.sleep(poll_interval)

    return {"blockNumber": None, "status": None}
