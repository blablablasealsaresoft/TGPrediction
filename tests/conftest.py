"""
Pytest configuration and fixtures
"""

import os

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock


os.environ.setdefault("WALLET_ENCRYPTION_KEY", "dLchbDvo1g_JUTokdPNfKM2-tP32T7kL6YwEH54oFsY=")


@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for the test session"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_config():
    """Mock configuration"""
    from src.config import Config, TradingConfig
    
    trading = TradingConfig(
        max_slippage=5.0,
        default_buy_amount_sol=0.1,
        min_profit_percentage=2.0,
        max_trade_size_sol=1.0,
        daily_loss_limit_sol=5.0,
        require_confirmation=True,
        min_liquidity_usd=10000.0,
        check_mint_authority=True,
        check_freeze_authority=True,
    )
    
    return Config(
        telegram_bot_token="test_token",
        admin_chat_id=123456,
        solana_rpc_url="https://api.devnet.solana.com",
        wallet_private_key="test_key",
        solana_network="devnet",
        trading=trading,
        twitter_api_key=None,
        twitter_api_secret=None,
        reddit_client_id=None,
        reddit_client_secret=None,
        discord_token=None,
        database_url="sqlite+aiosqlite:///:memory:",
        enable_health_check_server=False,
        health_check_port=8080,
        log_level="DEBUG",
        log_file="test.log"
    )


@pytest.fixture
async def mock_database():
    """Mock database manager"""
    from src.modules.database import DatabaseManager
    
    db = DatabaseManager("sqlite+aiosqlite:///:memory:")
    await db.init_db()
    yield db


@pytest.fixture
def mock_jupiter_client():
    """Mock Jupiter client"""
    return AsyncMock()


@pytest.fixture
def mock_telegram_update():
    """Mock Telegram update"""
    update = Mock()
    update.effective_user.id = 123456
    update.effective_user.username = "testuser"
    update.message.reply_text = AsyncMock()
    return update

