
#!/usr/bin/env python3
"""Main entry point for running the trading bot with production guardrails."""

import argparse
import asyncio
import json
import logging
import os
import signal
import sys
from datetime import datetime, timezone, UTC
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
from typing import Optional

# Fix Windows console encoding for emojis
if sys.platform == "win32":
    import codecs
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.bot.main import RevolutionaryTradingBot
from src.config import IS_PROD, get_config, validate_env
from src.modules.database import DatabaseManager
from src.ops.health import perform_health_checks
from src.ops.probes import start_probe_server
from solana.rpc.async_api import AsyncClient

LOG_FILE = Path("logs/trading_bot.jsonl")
logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Revolutionary Solana Trading Bot")
    parser.add_argument(
        "--network",
        choices=["devnet", "mainnet"],
        default=os.getenv("SOLANA_NETWORK", "devnet").replace("mainnet-beta", "mainnet"),
        help="Target Solana cluster",
    )
    parser.add_argument(
        "--no-auto-trade",
        action="store_true",
        help="Force auto-trade and sniper toggles off",
    )
    parser.add_argument(
        "--read-only",
        action="store_true",
        help="Disable trade execution paths (recommended for audits)",
    )
    return parser.parse_args()


def configure_logging():
    LOG_FILE.parent.mkdir(exist_ok=True)
    formatter = JsonLogFormatter()

    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(formatter)

    rotating_handler = TimedRotatingFileHandler(
        LOG_FILE,
        when="midnight",
        backupCount=7,
        encoding="utf-8",
    )
    rotating_handler.setFormatter(formatter)

    logging.basicConfig(
        level=logging.INFO,
        handlers=[stdout_handler, rotating_handler],
        force=True,
    )


class JsonLogFormatter(logging.Formatter):
    """Serialize log records to JSON for downstream ingestion."""

    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "ts": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "component": record.name,
            "event": record.getMessage(),
        }
        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)
        if hasattr(record, "details"):
            payload["details"] = record.details
        return json.dumps(payload, ensure_ascii=False)


def apply_overrides(args: argparse.Namespace):
    network = args.network
    if network == "mainnet":
        os.environ["SOLANA_NETWORK"] = "mainnet-beta"
    else:
        os.environ["SOLANA_NETWORK"] = "devnet"

    if args.no_auto_trade:
        os.environ["AUTO_TRADE_ENABLED"] = "false"
        os.environ["SNIPE_ENABLED"] = "false"

    if IS_PROD and args.read_only:
        os.environ["READ_ONLY_MODE"] = "true"
    elif args.read_only:
        os.environ.setdefault("READ_ONLY_MODE", "true")


class BotRunner:
    """Manages bot lifecycle and readiness probes."""

    def __init__(self, read_only: bool):
        self.bot = None
        self.config = None
        self.db_manager: Optional[DatabaseManager] = None
        self.solana_client: Optional[AsyncClient] = None
        self.shutdown_event = asyncio.Event()
        self.probe_server = None
        self.read_only = read_only and IS_PROD

    async def start(self):
        try:
            logger.info("Loading configuration")
            self.config = get_config()

            self._log_safety_banner()

            logger.info("Initializing database")
            self.db_manager = DatabaseManager(self.config.database_url)
            await self.db_manager.init_db()

            logger.info("Preparing Solana client")
            self.solana_client = AsyncClient(self.config.solana_rpc_url)

            prometheus_enabled = os.getenv("PROMETHEUS_ENABLED", "false").lower() in {"1", "true", "yes", "on"}
            self.probe_server = await start_probe_server(
                lambda: perform_health_checks(self.config.solana_network),
                prometheus_enabled=prometheus_enabled,
            )

            logger.info("Starting Revolutionary Trading Bot")
            self.bot = RevolutionaryTradingBot(
                self.config,
                self.db_manager,
                solana_client=self.solana_client,
            )

            await self.bot.start(self.shutdown_event)
        except KeyboardInterrupt:
            logger.info("Keyboard interrupt received")
        except Exception:
            logger.exception("Fatal error while running bot")
            raise
        finally:
            await self.cleanup()

    def _log_safety_banner(self):
        auto_trade = os.getenv("AUTO_TRADE_ENABLED", "true").lower()
        snipe = os.getenv("SNIPE_ENABLED", "true").lower()
        broadcast = os.getenv("ALLOW_BROADCAST", "false").lower()
        banner = [
            "▓" * 60,
            "RED SAFETY BANNER",
            f"Network: {self.config.solana_network}",
            f"Auto-trade enabled: {auto_trade}",
            f"Snipe enabled: {snipe}",
            f"Broadcast allowed: {broadcast}",
            f"Read-only mode: {os.getenv('READ_ONLY_MODE', 'false')}",
            "▓" * 60,
        ]
        logger.warning("\n".join(banner))

    async def cleanup(self):
        logger.info("Shutting down")
        if self.bot:
            try:
                await self.bot.stop()
            except Exception:
                logger.exception("Error during bot shutdown")
        if self.solana_client:
            try:
                await self.solana_client.close()
            except Exception:
                logger.exception("Error closing Solana client")
            finally:
                self.solana_client = None
        if self.db_manager:
            try:
                await self.db_manager.dispose()
            except Exception:
                logger.exception("Error disposing database manager")
            finally:
                self.db_manager = None
        if self.probe_server:
            await self.probe_server.stop()
            self.probe_server = None
        self.bot = None

    def signal_handler(self, signum, _frame):
        logger.info("Received signal %s; initiating shutdown", signum)
        self.shutdown_event.set()


async def main_async(args: argparse.Namespace):
    apply_overrides(args)
    validate_env()

    runner = BotRunner(read_only=args.read_only)

    signal.signal(signal.SIGINT, runner.signal_handler)
    signal.signal(signal.SIGTERM, runner.signal_handler)

    await runner.start()


def main():
    configure_logging()
    args = parse_args()
    logger.info("=" * 60)
    logger.info("SOLANA REVOLUTIONARY TRADING BOT")
    logger.info("=" * 60)
    asyncio.run(main_async(args))


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception:
        logger.exception("Fatal error encountered")
        sys.exit(1)
