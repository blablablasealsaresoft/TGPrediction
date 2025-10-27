#!/usr/bin/env python3
"""
Seed elite leader wallets into tracked_wallets so copy-trading can follow them.

Usage:
    python scripts/seed_tracked_wallets.py \
        --file importantdocs/unique_wallets_list.txt \
        --min-score 70 \
        --copy-enabled true
"""

import argparse
import asyncio
import hashlib
import os
import sys
from pathlib import Path
from typing import List, Tuple

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

import base58

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.modules.database import DatabaseManager, TrackedWallet  # noqa: E402

B58_CHARS = set("123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz")


def load_wallets(path: Path) -> List[str]:
    """Read wallets from file; tolerate numbering like `1. wallet`."""
    wallets: List[str] = []
    with path.open("r", encoding="utf-8", errors="ignore") as handle:
        for line in handle:
            raw = line.strip()
            if not raw:
                continue
            token = raw.split()[-1]
            wallets.append(token)
    # Deduplicate while preserving order
    seen = set()
    uniq = []
    for value in wallets:
        if value not in seen:
            uniq.append(value)
            seen.add(value)
    return uniq


def is_base58_wallet(value: str) -> bool:
    """Light validation for Solana-style base58 pubkeys."""
    if not (32 <= len(value) <= 64):
        return False
    if not all(char in B58_CHARS for char in value):
        return False
    try:
        decoded = base58.b58decode(value)
    except ValueError:
        return False
    return len(decoded) in (32, 64)


def derive_trader_user_id(wallet_address: str) -> int:
    """Deterministically derive a synthetic user_id for leader wallets."""
    digest = hashlib.sha256(wallet_address.encode("utf-8")).digest()
    candidate = 900_000_000 + int.from_bytes(digest[:4], "big")
    return candidate


async def ensure_unique_user_id(session, desired: int) -> int:
    """Bump the synthetic user_id until it is unused."""
    current = desired
    while True:
        stmt = select(TrackedWallet).where(
            TrackedWallet.user_id == current,
            TrackedWallet.copy_trader_id.is_(None),
        )
        result = await session.execute(stmt)
        record = result.scalar_one_or_none()
        if record is None:
            return current
        current += 1


async def upsert_wallets(
    db: DatabaseManager,
    wallets: List[str],
    min_score: float,
    copy_enabled: bool,
    dry_run: bool,
) -> Tuple[int, int, int]:
    """Insert/update wallets; return (inserted, updated, invalid)."""
    inserted = 0
    updated = 0
    invalid = 0

    async with db.async_session() as session:
        for wallet in wallets:
            if not is_base58_wallet(wallet):
                invalid += 1
                continue

            stmt = (
                select(TrackedWallet)
                .where(
                    TrackedWallet.wallet_address == wallet,
                    TrackedWallet.copy_trader_id.is_(None),
                )
                .limit(1)
            )
            result = await session.execute(stmt)
            record = result.scalars().first()

            if dry_run:
                if record:
                    updated += 1
                else:
                    inserted += 1
                continue

            if record:
                record.is_trader = True
                record.copy_enabled = copy_enabled
                record.score = max(record.score or 0.0, float(min_score))
                record.label = record.label or f"Leader {wallet[:6]}"
                updated += 1
            else:
                user_id = await ensure_unique_user_id(
                    session,
                    derive_trader_user_id(wallet),
                )
                new_wallet = TrackedWallet(
                    user_id=user_id,
                    wallet_address=wallet,
                    label=f"Leader {wallet[:6]}",
                    is_trader=True,
                    is_verified=True,
                    copy_enabled=copy_enabled,
                    score=float(min_score),
                )
                session.add(new_wallet)
                inserted += 1

        if not dry_run:
            await session.commit()

    return inserted, updated, invalid


async def amain() -> None:
    parser = argparse.ArgumentParser(description="Seed leader wallets into tracked_wallets")
    parser.add_argument("--file", required=True, help="Path to wallet list (one per line)")
    parser.add_argument("--min-score", type=float, default=70.0, help="Initial intelligence score (0-100)")
    parser.add_argument(
        "--copy-enabled",
        type=str,
        default="true",
        help="Mark copy_enabled for all leaders (true/false)",
    )
    parser.add_argument(
        "--dry-run",
        type=str,
        default="false",
        help="Preview inserts/updates without writing (true/false)",
    )
    args = parser.parse_args()

    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        print("DATABASE_URL is required.", file=sys.stderr)
        sys.exit(2)

    copy_enabled = args.copy_enabled.strip().lower() in {"1", "true", "yes", "y"}
    dry_run = args.dry_run.strip().lower() in {"1", "true", "yes", "y"}

    wallet_path = Path(args.file).expanduser()
    if not wallet_path.exists():
        print(f"Wallet list not found: {wallet_path}", file=sys.stderr)
        sys.exit(2)

    wallets = load_wallets(wallet_path)
    if not wallets:
        print("No wallets found in the provided file.", file=sys.stderr)
        sys.exit(1)

    db = DatabaseManager(db_url)
    try:
        await db.init_db()
    except SQLAlchemyError as exc:  # pragma: no cover - defensive
        print(f"Failed to initialize database: {exc}", file=sys.stderr)
        sys.exit(2)

    inserted, updated, invalid = await upsert_wallets(
        db=db,
        wallets=wallets,
        min_score=args.min_score,
        copy_enabled=copy_enabled,
        dry_run=dry_run,
    )

    mode = "DRY-RUN" if dry_run else "APPLIED"
    print(
        f"[seed_tracked_wallets] {mode}: "
        f"total={len(wallets)} inserted={inserted} updated={updated} invalid={invalid}"
    )


if __name__ == "__main__":
    asyncio.run(amain())
