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

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.config import get_config
from src.modules.database import DatabaseManager
from src.bot.main import RevolutionaryTradingBot

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
        self.shutdown_event = asyncio.Event()
    
    async def start(self):
        """Start the bot"""
        try:
            # Load config
            logger.info("Loading configuration...")
            config = get_config()
            
            # Initialize database
            logger.info("Initializing database...")
            db_manager = DatabaseManager(config.database_url)
            await db_manager.init_db()
            
            # Create and start bot
            logger.info("Starting Revolutionary Trading Bot...")
            self.bot = RevolutionaryTradingBot()
            
            # Start bot (this should be implemented in main.py)
            await self.bot.start()
            
            # Wait for shutdown signal
            await self.shutdown_event.wait()
            
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

