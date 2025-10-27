#!/usr/bin/env python3
"""Comprehensive health-check CLI for the trading bot."""

import argparse
import asyncio
import json
import sys
from pathlib import Path

# Ensure project root on sys.path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.config import get_config, validate_env  # noqa: E402
from src.ops.health import perform_health_checks  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Trading bot health check")
    parser.add_argument(
        "--network",
        choices=["devnet", "testnet", "mainnet", "mainnet-beta"],
        help="Expected Solana network (defaults to configured SOLANA_NETWORK)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print machine-readable JSON output",
    )
    return parser.parse_args()


async def main() -> int:
    args = parse_args()
    validate_env()
    config = get_config()

    expected_network = args.network or config.solana_network
    ok, results = await perform_health_checks(expected_network)

    if args.json:
        payload = {
            "status": "pass" if ok else "fail",
            "checks": {name: {"ok": status, "detail": detail} for name, (status, detail) in results.items()},
        }
        print(json.dumps(payload, indent=2))
    else:
        print("=" * 60)
        print("TRADING BOT HEALTH CHECK")
        print("=" * 60)
        for name, (status, detail) in results.items():
            icon = "✅" if status else "❌"
            print(f"{icon} {name}: {detail}")
        print("=" * 60)
        print("Overall:", "PASS" if ok else "FAIL")

    return 0 if ok else 2


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
    except KeyboardInterrupt:
        exit_code = 1
    sys.exit(exit_code)
