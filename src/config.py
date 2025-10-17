"""
Configuration management for trading bot
Loads settings from environment variables with validation
"""

import os
from typing import Optional
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


@dataclass
class TradingConfig:
    """Trading parameters"""
    max_slippage: float
    default_buy_amount_sol: float
    min_profit_percentage: float
    max_trade_size_sol: float
    daily_loss_limit_sol: float
    require_confirmation: bool
    min_liquidity_usd: float
    check_mint_authority: bool
    check_freeze_authority: bool


@dataclass
class Config:
    """Main configuration class"""
    
    # Telegram
    telegram_bot_token: str
    admin_chat_id: Optional[int]
    
    # Solana
    solana_rpc_url: str
    wallet_private_key: str
    solana_network: str
    
    # Trading
    trading: TradingConfig
    
    # Social Media APIs
    twitter_api_key: Optional[str]
    twitter_api_secret: Optional[str]
    reddit_client_id: Optional[str]
    reddit_client_secret: Optional[str]
    discord_token: Optional[str]
    
    # Database
    database_url: str
    
    # Monitoring
    enable_health_check_server: bool
    health_check_port: int
    
    # Logging
    log_level: str
    log_file: str
    
    @classmethod
    def from_env(cls) -> 'Config':
        """Load configuration from environment variables"""
        
        # Telegram
        telegram_bot_token = os.getenv('TELEGRAM_BOT_TOKEN', '')
        if not telegram_bot_token:
            raise ValueError("TELEGRAM_BOT_TOKEN is required")
        
        admin_chat_id_str = os.getenv('ADMIN_CHAT_ID')
        admin_chat_id = int(admin_chat_id_str) if admin_chat_id_str else None
        
        # Solana
        solana_rpc_url = os.getenv('SOLANA_RPC_URL', 'https://api.mainnet-beta.solana.com')
        wallet_private_key = os.getenv('WALLET_PRIVATE_KEY', '')
        solana_network = os.getenv('SOLANA_NETWORK', 'mainnet-beta')
        
        # Trading
        trading = TradingConfig(
            max_slippage=float(os.getenv('MAX_SLIPPAGE', '5.0')),
            default_buy_amount_sol=float(os.getenv('DEFAULT_BUY_AMOUNT_SOL', '0.1')),
            min_profit_percentage=float(os.getenv('MIN_PROFIT_PERCENTAGE', '2.0')),
            max_trade_size_sol=float(os.getenv('MAX_TRADE_SIZE_SOL', '1.0')),
            daily_loss_limit_sol=float(os.getenv('DAILY_LOSS_LIMIT_SOL', '5.0')),
            require_confirmation=os.getenv('REQUIRE_CONFIRMATION', 'true').lower() == 'true',
            min_liquidity_usd=float(os.getenv('MIN_LIQUIDITY_USD', '10000')),
            check_mint_authority=os.getenv('CHECK_MINT_AUTHORITY', 'true').lower() == 'true',
            check_freeze_authority=os.getenv('CHECK_FREEZE_AUTHORITY', 'true').lower() == 'true',
        )
        
        # Social Media (optional)
        twitter_api_key = os.getenv('TWITTER_API_KEY')
        twitter_api_secret = os.getenv('TWITTER_API_SECRET')
        reddit_client_id = os.getenv('REDDIT_CLIENT_ID')
        reddit_client_secret = os.getenv('REDDIT_CLIENT_SECRET')
        discord_token = os.getenv('DISCORD_TOKEN')
        
        # Database
        database_url = os.getenv('DATABASE_URL', 'sqlite+aiosqlite:///trading_bot.db')
        
        # Monitoring
        enable_health_check_server = os.getenv('ENABLE_HEALTH_CHECK_SERVER', 'true').lower() == 'true'
        health_check_port = int(os.getenv('HEALTH_CHECK_PORT', '8080'))
        
        # Logging
        log_level = os.getenv('LOG_LEVEL', 'INFO')
        log_file = os.getenv('LOG_FILE', 'logs/trading_bot.log')
        
        return cls(
            telegram_bot_token=telegram_bot_token,
            admin_chat_id=admin_chat_id,
            solana_rpc_url=solana_rpc_url,
            wallet_private_key=wallet_private_key,
            solana_network=solana_network,
            trading=trading,
            twitter_api_key=twitter_api_key,
            twitter_api_secret=twitter_api_secret,
            reddit_client_id=reddit_client_id,
            reddit_client_secret=reddit_client_secret,
            discord_token=discord_token,
            database_url=database_url,
            enable_health_check_server=enable_health_check_server,
            health_check_port=health_check_port,
            log_level=log_level,
            log_file=log_file
        )
    
    def validate(self):
        """Validate configuration"""
        errors = []
        
        if not self.telegram_bot_token:
            errors.append("TELEGRAM_BOT_TOKEN is required")
        
        if self.solana_network not in ['devnet', 'testnet', 'mainnet-beta']:
            errors.append(f"Invalid SOLANA_NETWORK: {self.solana_network}")
        
        if self.trading.max_slippage < 0 or self.trading.max_slippage > 50:
            errors.append("MAX_SLIPPAGE must be between 0 and 50")
        
        if self.trading.max_trade_size_sol <= 0:
            errors.append("MAX_TRADE_SIZE_SOL must be positive")
        
        if errors:
            raise ValueError(f"Configuration errors:\n" + "\n".join(f"- {e}" for e in errors))


# Global config instance
_config: Optional[Config] = None


def get_config() -> Config:
    """Get global configuration instance"""
    global _config
    if _config is None:
        _config = Config.from_env()
        _config.validate()
    return _config


def reload_config():
    """Reload configuration from environment"""
    global _config
    _config = None
    return get_config()

