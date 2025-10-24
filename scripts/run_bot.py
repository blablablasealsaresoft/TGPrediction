#!/usr/bin/env python3
"""
Main entry point for running the trading bot
Handles initialization, error handling, and graceful shutdown
"""

import asyncio
import logging
import signal
import sys
from pathlib import Path
from typing import Optional

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.config import get_config
from src.modules.database import DatabaseManager
from src.bot.main import RevolutionaryTradingBot
from solana.rpc.async_api import AsyncClient

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('logs/trading_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class BotRunner:
    """Manages bot lifecycle"""
    
    def __init__(self):
        self.bot = None
        self.config = None
        self.db_manager: Optional[DatabaseManager] = None
        self.solana_client: Optional[AsyncClient] = None
        self.shutdown_event = asyncio.Event()
    
    async def start(self):
        """Start the bot"""
        try:
            logger.info("Loading configuration...")
            self.config = get_config()

            logger.info("Initializing database...")
            self.db_manager = DatabaseManager(self.config.database_url)
            await self.db_manager.init_db()

            logger.info("Preparing Solana client...")
            self.solana_client = AsyncClient(self.config.solana_rpc_url)

            logger.info("Starting Revolutionary Trading Bot...")
            self.bot = RevolutionaryTradingBot(
                self.config,
                self.db_manager,
                solana_client=self.solana_client,
            )

            await self.bot.start(self.shutdown_event)

        except KeyboardInterrupt:
            logger.info("Keyboard interrupt received")
        except Exception as e:
            logger.error(f"Fatal error: {e}", exc_info=True)
            raise
        finally:
            await self.cleanup()
    
    async def cleanup(self):
        """Cleanup resources"""
        logger.info("Shutting down...")
        if self.bot:
            try:
                await self.bot.stop()
            except Exception as e:
                logger.error(f"Error during shutdown: {e}")

        if self.solana_client:
            try:
                await self.solana_client.close()
            except Exception as e:
                logger.error(f"Error closing Solana client: {e}")
            finally:
                self.solana_client = None

        if self.db_manager:
            try:
                await self.db_manager.dispose()
            except Exception as e:
                logger.error(f"Error disposing database manager: {e}")
            finally:
                self.db_manager = None

        self.bot = None
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}")
        self.shutdown_event.set()


async def main():
    """Main entry point"""
    # Create logs directory
    Path("logs").mkdir(exist_ok=True)
    
    runner = BotRunner()
    
    # Setup signal handlers
    signal.signal(signal.SIGINT, runner.signal_handler)
    signal.signal(signal.SIGTERM, runner.signal_handler)
    
    try:
        await runner.start()
    except Exception as e:
        logger.error(f"Bot crashed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("SOLANA REVOLUTIONARY TRADING BOT")
    logger.info("=" * 60)
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)

