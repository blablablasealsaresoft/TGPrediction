#!/usr/bin/env python3
"""
Health Check Script for Trading Bot
Verifies all components are properly configured and operational
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import asyncio
import logging
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


class HealthChecker:
    """Comprehensive health check for trading bot"""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.passed = []
    
    def check(self, name, condition, error_msg=None, warning=False):
        """Record check result"""
        if condition:
            self.passed.append(name)
            logger.info(f"✅ {name}")
            return True
        else:
            msg = error_msg or f"{name} failed"
            if warning:
                self.warnings.append(msg)
                logger.warning(f"⚠️  {msg}")
            else:
                self.errors.append(msg)
                logger.error(f"❌ {msg}")
            return False
    
    async def run_all_checks(self):
        """Run all health checks"""
        logger.info("=" * 60)
        logger.info("TRADING BOT HEALTH CHECK")
        logger.info("=" * 60)
        
        # Configuration checks
        logger.info("\n📋 Configuration Checks:")
        self.check_configuration()
        
        # Database checks
        logger.info("\n🗄️  Database Checks:")
        await self.check_database()
        
        # Network checks
        logger.info("\n🌐 Network Checks:")
        await self.check_network()
        
        # Module checks
        logger.info("\n📦 Module Checks:")
        self.check_modules()
        
        # Summary
        self.print_summary()
    
    def check_configuration(self):
        """Check environment configuration"""
        # Critical
        self.check(
            "WALLET_ENCRYPTION_KEY",
            os.getenv('WALLET_ENCRYPTION_KEY'),
            "WALLET_ENCRYPTION_KEY not set. Generate with: python -c \"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\""
        )
        
        self.check(
            "TELEGRAM_BOT_TOKEN",
            os.getenv('TELEGRAM_BOT_TOKEN'),
            "TELEGRAM_BOT_TOKEN not set"
        )
        
        self.check(
            "SOLANA_RPC_URL",
            os.getenv('SOLANA_RPC_URL'),
            "SOLANA_RPC_URL not set (default will be used)"
        )
        
        # Optional but recommended
        self.check(
            "ADMIN_CHAT_ID",
            os.getenv('ADMIN_CHAT_ID'),
            "ADMIN_CHAT_ID not set (admin commands disabled)",
            warning=True
        )
        
        self.check(
            "HELIUS_API_KEY",
            os.getenv('HELIUS_API_KEY'),
            "HELIUS_API_KEY not set (using standard RPC, may be slower)",
            warning=True
        )
        
        # Sentiment (optional)
        sentiment_configured = any([
            os.getenv('TWITTER_API_KEY'),
            os.getenv('REDDIT_CLIENT_ID'),
            os.getenv('DISCORD_TOKEN')
        ])
        self.check(
            "Sentiment APIs",
            sentiment_configured,
            "No sentiment APIs configured (sentiment features limited)",
            warning=True
        )
    
    async def check_database(self):
        """Check database health"""
        try:
            from src.modules.database import DatabaseManager
            
            db = DatabaseManager()
            await db.init_db()
            
            self.check("Database initialization", True)
            
            # Check tables exist
            async with db.async_session() as session:
                from sqlalchemy import text
                result = await session.execute(
                    text("SELECT name FROM sqlite_master WHERE type='table'")
                )
                tables = [row[0] for row in result.fetchall()]
                
                required_tables = [
                    'trades', 'positions', 'user_wallets',
                    'tracked_wallets', 'user_settings', 'snipe_runs'
                ]
                
                for table in required_tables:
                    self.check(
                        f"Table: {table}",
                        table in tables,
                        f"Required table '{table}' missing"
                    )
                
                # Check for data
                result = await session.execute(text("SELECT COUNT(*) FROM user_wallets"))
                user_count = result.scalar()
                self.check(
                    f"Users in database ({user_count})",
                    True,
                    warning=user_count == 0
                )
            
            await db.dispose()
            
        except Exception as e:
            self.check("Database connection", False, f"Database error: {e}")
    
    async def check_network(self):
        """Check network connectivity"""
        try:
            from solana.rpc.async_api import AsyncClient
            
            rpc_url = os.getenv('SOLANA_RPC_URL', 'https://api.mainnet-beta.solana.com')
            client = AsyncClient(rpc_url)
            
            # Test RPC connection
            try:
                version = await client.get_version()
                self.check(
                    f"Solana RPC ({rpc_url})",
                    version.value is not None,
                    f"RPC connection failed: {rpc_url}"
                )
            except Exception as e:
                self.check(
                    "Solana RPC",
                    False,
                    f"RPC error: {e}"
                )
            
            # Test health
            try:
                health = await client.get_health()
                self.check(
                    "RPC node health",
                    health.value == "ok",
                    "RPC node unhealthy"
                )
            except Exception as e:
                self.check(
                    "RPC node health",
                    False,
                    f"Health check failed: {e}"
                )
            
            await client.close()
            
        except Exception as e:
            self.check("Network checks", False, f"Network error: {e}")
    
    def check_modules(self):
        """Check module imports"""
        modules = [
            ('src.config', 'Configuration'),
            ('src.modules.database', 'Database'),
            ('src.modules.wallet_manager', 'Wallet Manager'),
            ('src.modules.jupiter_client', 'Jupiter DEX'),
            ('src.modules.ai_strategy_engine', 'AI Strategy'),
            ('src.modules.social_trading', 'Social Trading'),
            ('src.modules.token_sniper', 'Token Sniper'),
            ('src.modules.automated_trading', 'Automated Trading'),
            ('src.modules.trade_execution', 'Trade Execution'),
            ('src.modules.elite_protection', 'Elite Protection'),
            ('src.modules.wallet_intelligence', 'Wallet Intelligence'),
            ('src.modules.sentiment_analysis', 'Sentiment Analysis'),
            ('src.bot.main', 'Bot Main'),
        ]
        
        for module_name, display_name in modules:
            try:
                __import__(module_name)
                self.check(f"Module: {display_name}", True)
            except Exception as e:
                self.check(f"Module: {display_name}", False, f"Import error: {e}")
    
    def print_summary(self):
        """Print health check summary"""
        logger.info("\n" + "=" * 60)
        logger.info("HEALTH CHECK SUMMARY")
        logger.info("=" * 60)
        
        logger.info(f"✅ Passed: {len(self.passed)}")
        logger.info(f"⚠️  Warnings: {len(self.warnings)}")
        logger.info(f"❌ Errors: {len(self.errors)}")
        
        if self.warnings:
            logger.info("\n⚠️  Warnings:")
            for warning in self.warnings:
                logger.info(f"  - {warning}")
        
        if self.errors:
            logger.info("\n❌ Errors:")
            for error in self.errors:
                logger.info(f"  - {error}")
            logger.info("\n❌ Health check FAILED. Fix errors before running bot.")
            return False
        else:
            logger.info("\n✅ Health check PASSED. Bot is ready to run.")
            return True


async def main():
    """Main health check entry point"""
    checker = HealthChecker()
    success = await checker.run_all_checks()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())

