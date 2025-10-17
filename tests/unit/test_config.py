"""
Tests for configuration module
"""

import pytest
import os
from src.config import Config, TradingConfig


def test_trading_config_creation():
    """Test TradingConfig creation"""
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
    
    assert trading.max_slippage == 5.0
    assert trading.default_buy_amount_sol == 0.1
    assert trading.require_confirmation is True


def test_config_validation(mock_config):
    """Test configuration validation"""
    # Valid config should not raise
    mock_config.validate()
    
    # Invalid slippage
    mock_config.trading.max_slippage = 100
    with pytest.raises(ValueError, match="MAX_SLIPPAGE"):
        mock_config.validate()
    
    # Invalid network
    mock_config.trading.max_slippage = 5.0  # Reset
    mock_config.solana_network = "invalid"
    with pytest.raises(ValueError, match="SOLANA_NETWORK"):
        mock_config.validate()


def test_config_from_env(monkeypatch):
    """Test loading config from environment variables"""
    # Set environment variables
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test_token")
    monkeypatch.setenv("ADMIN_CHAT_ID", "123456")
    monkeypatch.setenv("MAX_SLIPPAGE", "3.5")
    
    config = Config.from_env()
    
    assert config.telegram_bot_token == "test_token"
    assert config.admin_chat_id == 123456
    assert config.trading.max_slippage == 3.5

