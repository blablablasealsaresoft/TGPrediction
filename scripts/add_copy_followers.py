#!/usr/bin/env python3
"""Create copy-trading relationships for a follower across many leader wallets."""

import argparse
import asyncio
import os
import sys
from pathlib import Path
from typing import Dict, List, Tuple

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.modules.database import DatabaseManager, TrackedWallet  # noqa: E402


def load_wallets(path: Path) -> List[str]:
    wallets: List[str] = []
    with path.open("r", encoding="utf-8", errors="ignore") as handle:
        for line in handle:
            raw = line.strip()
            if not raw:
                continue
            wallets.append(raw.split()[-1])
    # Deduplicate preserving order
    seen = set()
    uniq = []
    for wallet in wallets:
        if wallet not in seen:
            uniq.append(wallet)
            seen.add(wallet)
    return uniq


async def map_wallets_to_trader_ids(
    db: DatabaseManager, wallets: List[str]
) -> Dict[str, int]:
    """Return wallet -> trader user_id for existing leader profiles."""
    async with db.async_session() as session:
        stmt = select(TrackedWallet.wallet_address, TrackedWallet.user_id).where(
            TrackedWallet.wallet_address.in_(wallets),
            TrackedWallet.is_trader.is_(True),
            TrackedWallet.copy_trader_id.is_(None),
        )
        rows = await session.execute(stmt)
        mapping = {}
        for row in rows:
            wallet_address, user_id = row
            if user_id is not None:
                mapping[wallet_address] = user_id
        return mapping


async def amain() -> None:
    parser = argparse.ArgumentParser(
        description="Enable copy trading for a follower across many leaders."
    )
    parser.add_argument("--follower-id", type=int, required=True, help="User ID that will follow the leaders")
    parser.add_argument("--file", required=True, help="Path to wallet list (leaders)")
    parser.add_argument("--amount-sol", type=float, default=0.05, help="Max SOL per copied trade")
    parser.add_argument("--max-daily-trades", type=int, default=10, help="Follower cap per leader per day")
    parser.add_argument(
        "--enable",
        type=str,
        default="true",
        help="Enable the copy relationship immediately (true/false)",
    )
    args = parser.parse_args()

    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        print("DATABASE_URL is required.", file=sys.stderr)
        sys.exit(2)

    wallet_path = Path(args.file).expanduser()
    if not wallet_path.exists():
        print(f"Wallet list not found: {wallet_path}", file=sys.stderr)
        sys.exit(2)

    wallets = load_wallets(wallet_path)
    if not wallets:
        print("Wallet list is empty.", file=sys.stderr)
        sys.exit(1)

    enable = args.enable.strip().lower() in {"1", "true", "yes", "y"}
    db = DatabaseManager(db_url)
    try:
        await db.init_db()
    except SQLAlchemyError as exc:  # pragma: no cover - defensive
        print(f"Failed to initialize database: {exc}", file=sys.stderr)
        sys.exit(2)

    mapping = await map_wallets_to_trader_ids(db, wallets)

    linked = 0
    missing = 0

    settings_template = {
        "copy_percentage": 100.0,
        "max_copy_amount": float(args.amount_sol),
        "max_daily_trades": int(args.max_daily_trades),
    }

    for wallet in wallets:
        trader_id = mapping.get(wallet)
        if not trader_id:
            missing += 1
            continue

        settings = dict(settings_template)
        settings["wallet_address"] = wallet
        settings["label"] = f"Copy {wallet[:6]}"

        relationship, _ = await db.set_copy_relationship(
            follower_id=args.follower_id,
            trader_id=trader_id,
            settings=settings,
        )

        if not enable and relationship.copy_enabled:
            await db.disable_copy_relationship(args.follower_id, trader_id)
        elif enable and not relationship.copy_enabled:
            await db.set_copy_relationship(args.follower_id, trader_id, settings)

        linked += 1

    print(
        f"[add_copy_followers] follower={args.follower_id} linked={linked} "
        f"missing_leaders={missing} amount_sol={args.amount_sol} enabled={enable}"
    )


if __name__ == "__main__":
    asyncio.run(amain())
