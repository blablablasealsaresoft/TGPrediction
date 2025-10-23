#!/usr/bin/env python3

"""Rotate the WALLET_ENCRYPTION_KEY used to protect user wallets.

This utility re-encrypts every stored wallet with a new Fernet key. It can
also generate a fresh key when one is not provided. Always run a database
backup before rotating keys in production.
"""

from __future__ import annotations

import argparse
import asyncio
import logging
import os
import sys
from typing import Optional

from dotenv import load_dotenv
from cryptography.fernet import Fernet, InvalidToken
from sqlalchemy import select

load_dotenv()

# Ensure project modules are importable when executed directly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.modules.database import DatabaseManager, UserWallet  # noqa: E402
from src.modules.wallet_manager import WalletEncryption  # noqa: E402

logger = logging.getLogger("wallet_key_rotation")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Rotate the WALLET_ENCRYPTION_KEY protecting stored wallets."
    )
    parser.add_argument(
        "--database-url",
        default=os.getenv("DATABASE_URL", "sqlite+aiosqlite:///trading_bot.db"),
        help="Database connection string (defaults to DATABASE_URL env or local SQLite).",
    )
    parser.add_argument(
        "--current-key",
        help=(
            "Existing WALLET_ENCRYPTION_KEY. Defaults to the environment value if set."
        ),
    )
    parser.add_argument(
        "--new-key",
        help="New WALLET_ENCRYPTION_KEY to apply. Must be a urlsafe base64-encoded 32-byte key.",
    )
    parser.add_argument(
        "--generate-new-key",
        action="store_true",
        help="Generate a compliant key automatically. The value will be printed to stdout.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate keys and decrypt all wallets without writing changes.",
    )
    return parser


async def _rotate_keys(
    *,
    database_url: str,
    current_key: str,
    new_key: str,
    dry_run: bool,
) -> None:
    current_bytes = WalletEncryption.validate_key(current_key)
    new_bytes = WalletEncryption.validate_key(new_key)

    current_cipher = Fernet(current_bytes)
    new_cipher = Fernet(new_bytes)

    db = DatabaseManager(database_url)

    async with db.async_session() as session:
        result = await session.execute(select(UserWallet))
        wallets = result.scalars().all()

        if not wallets:
            logger.info("No wallets found in the database. Nothing to rotate.")
            return

        logger.info("Rotating encryption for %s wallet(s)", len(wallets))

        validated = 0
        updated = 0
        for wallet in wallets:
            try:
                decrypted = current_cipher.decrypt(wallet.encrypted_private_key.encode())
            except InvalidToken as exc:
                raise RuntimeError(
                    "Failed to decrypt wallet %s with the current key. Aborting rotation."
                    % wallet.public_key
                ) from exc

            validated += 1

            if dry_run:
                continue

            wallet.encrypted_private_key = new_cipher.encrypt(decrypted).decode()
            updated += 1

        if dry_run:
            logger.info(
                "Dry run completed successfully for %s wallet(s). All entries are decryptable with the current key.",
                validated,
            )
            return

        await session.commit()
        logger.info("Successfully rotated %s wallet(s).", updated)


async def _main_async(args: argparse.Namespace) -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    current_key = args.current_key or os.getenv("WALLET_ENCRYPTION_KEY")
    if not current_key:
        raise RuntimeError(
            "Current WALLET_ENCRYPTION_KEY must be supplied via --current-key or the environment."
        )

    if args.generate_new_key and args.new_key:
        raise ValueError("Provide either --new-key or --generate-new-key, not both.")

    if args.generate_new_key:
        new_key = WalletEncryption.generate_key()
        print("Generated new wallet encryption key:\nWALLET_ENCRYPTION_KEY=%s" % new_key)
    elif args.new_key:
        new_key = args.new_key
    else:
        raise RuntimeError("A new key is required. Use --new-key or --generate-new-key.")

    await _rotate_keys(
        database_url=args.database_url,
        current_key=current_key,
        new_key=new_key,
        dry_run=args.dry_run,
    )

    if args.dry_run:
        logger.info("Dry run only. Database was not modified.")
    else:
        logger.info(
            "Rotation complete. Update WALLET_ENCRYPTION_KEY in your secret manager before restarting services."
        )


def main(argv: Optional[list[str]] = None) -> None:
    parser = _build_parser()
    args = parser.parse_args(argv)
    asyncio.run(_main_async(args))


if __name__ == "__main__":  # pragma: no cover - manual script entrypoint
    main()

