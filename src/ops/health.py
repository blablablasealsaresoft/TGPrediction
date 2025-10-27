"""Shared health-check routines used by the CLI and readiness probes."""

import asyncio
import shutil
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Optional, Tuple

import aiohttp
from solana.rpc.async_api import AsyncClient

from src.config import Config, get_config
from src.modules.database import DatabaseManager

HealthResult = Dict[str, Tuple[bool, str]]


async def perform_health_checks(expected_network: Optional[str] = None) -> Tuple[bool, HealthResult]:
    """Run all health checks and return (overall_ok, detailed_results)."""
    config = get_config()
    expected_network = expected_network or config.solana_network

    results: HealthResult = {}
    results["database"] = await _check_database(config)
    results["solana_rpc"] = await _check_solana_rpc(config, expected_network)
    results["telegram"] = await _check_telegram(config)
    results["disk_space"] = _check_disk_space()
    results["clock"] = _check_clock()

    overall = all(status for status, _ in results.values())
    return overall, results


async def _check_database(config: Config) -> Tuple[bool, str]:
    manager = DatabaseManager(config.database_url)
    try:
        await manager.init_db()
        return True, "database reachable"
    except Exception as exc:  # pragma: no cover - protective
        return False, f"db error: {exc.__class__.__name__}"
    finally:
        await manager.dispose()


async def _check_solana_rpc(config: Config, expected_network: str) -> Tuple[bool, str]:
    client = AsyncClient(config.solana_rpc_url)
    try:
        response = await client.get_version()
        cluster = response.get("result", {})
        network = config.solana_network
        if expected_network == "mainnet":
            expected_network = "mainnet-beta"
        if network != expected_network:
            return False, f"network mismatch (configured {network}, expected {expected_network})"
        if "solana-core" not in str(cluster):
            return False, "unexpected RPC response"
        return True, "rpc ok"
    except Exception as exc:  # pragma: no cover - protective
        return False, f"rpc error: {exc.__class__.__name__}"
    finally:
        await client.close()


async def _check_telegram(config: Config) -> Tuple[bool, str]:
    token = config.telegram_bot_token
    url = f"https://api.telegram.org/bot{token}/getMe"
    timeout = aiohttp.ClientTimeout(total=5)
    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url) as resp:
                data = await resp.json()
                if resp.status == 200 and data.get("ok"):
                    return True, "telegram ok"
                return False, "telegram rejected credentials"
    except Exception as exc:  # pragma: no cover - protective
        return False, f"telegram error: {exc.__class__.__name__}"


def _check_disk_space() -> Tuple[bool, str]:
    usage = shutil.disk_usage(Path(".").resolve())
    free_gb = usage.free / (1024 ** 3)
    if free_gb >= 1:
        return True, f"{free_gb:.2f}GB free"
    return False, f"low disk ({free_gb:.2f}GB free)"


def _check_clock() -> Tuple[bool, str]:
    unix_now = time.time()
    utc_now = datetime.now(timezone.utc).timestamp()
    drift = abs(unix_now - utc_now)
    if drift <= 2:
        return True, f"clock drift {drift:.3f}s"
    return False, f"clock drift {drift:.3f}s exceeds 2s"

