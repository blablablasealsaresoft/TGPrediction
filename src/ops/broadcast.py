"""Centralized Solana broadcast guardrails."""

import logging
import os
from typing import Any, Dict, Optional

from solana.rpc.async_api import AsyncClient

from src.config import IS_PROD

logger = logging.getLogger(__name__)


async def send(
    rpc_client: AsyncClient,
    tx_bytes: bytes,
    *,
    context: Optional[Dict[str, Any]] = None,
    confirm_token: Optional[str] = None,
) -> str:
    """Broadcast a transaction with production guardrails."""
    context = context or {}
    allow_broadcast = os.getenv("ALLOW_BROADCAST", "false").strip().lower() in {"1", "true", "yes", "on"}
    expected_token = os.getenv("CONFIRM_TOKEN")

    if IS_PROD:
        if not allow_broadcast:
            raise RuntimeError("Broadcast denied: ALLOW_BROADCAST is not enabled in production.")
        if not (confirm_token and expected_token and confirm_token == expected_token):
            raise RuntimeError("Broadcast denied: missing or invalid confirm_token.")

    logger.info(
        "Submitting transaction",
        extra={
            "details": {
                "context": context,
                "tx_size": len(tx_bytes),
            }
        },
    )
    result = await rpc_client.send_raw_transaction(
        tx_bytes,
        opts={"skip_preflight": False, "preflight_commitment": "confirmed"},
    )
    signature = str(result.value)
    logger.info(
        "Transaction broadcast complete",
        extra={"details": {"signature": signature, "context": context}},
    )
    return signature
