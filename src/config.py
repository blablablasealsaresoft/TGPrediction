
"""Configuration management for trading bot.

Enforces a strict environment contract derived from importantdocs/ENVIRONMENT_VARIABLES.md
and exposes helpers for the rest of the application."""

import base64
import os
from typing import Dict, Optional, Set
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

BOOL_TRUE = {"1", "true", "yes", "on"}

# Required environment variables and their types
NUMERIC_FLOAT_VARS = {
    "MAX_POSITION_SIZE_SOL",
    "DEFAULT_BUY_AMOUNT_SOL",
    "MAX_DAILY_LOSS_SOL",
    "STOP_LOSS_PERCENTAGE",
    "TAKE_PROFIT_PERCENTAGE",
    "TRAILING_STOP_PERCENTAGE",
    "MAX_SLIPPAGE",
    "MIN_LIQUIDITY_USD",
}

NUMERIC_INT_VARS = {
    "ADMIN_CHAT_ID",
    "HEALTH_CHECK_PORT",
}

BOOL_VARS = {
    "REQUIRE_CONFIRMATION",
    "CHECK_MINT_AUTHORITY",
    "CHECK_FREEZE_AUTHORITY",
    "HONEYPOT_CHECK_ENABLED",
    "ENABLE_HEALTH_CHECK_SERVER",
}

STRING_VARS = {
    "WALLET_ENCRYPTION_KEY",
    "TELEGRAM_BOT_TOKEN",
    "SOLANA_RPC_URL",
    "WALLET_PRIVATE_KEY",
    "SOLANA_NETWORK",
    "DATABASE_URL",
    "LOG_LEVEL",
    "LOG_FILE",
}

MANDATORY_VARS: Set[str] = (
    NUMERIC_FLOAT_VARS
    | NUMERIC_INT_VARS
    | BOOL_VARS
    | STRING_VARS
)

ALIAS_MAP = {
    "DEFAULT_BUY_AMOUNT_SOL": ["DEFAULT_BUY_AMOUNT"],
    "MAX_POSITION_SIZE_SOL": ["MAX_TRADE_SIZE_SOL"],
    "MAX_DAILY_LOSS_SOL": ["DAILY_LOSS_LIMIT_SOL"],
}

IS_PROD = os.getenv("ENV", "dev").strip().lower() == "prod"


def _normalize_percentage(value: float) -> float:
    """Convert fractional percentages (0-1) to 0-100 scale."""
    if value <= 1:
        return value * 100
    return value


def _get_float(name: str, default: str) -> float:
    """Safely parse a float environment variable."""
    raw = os.getenv(name, default)
    try:
        return float(raw)
    except (TypeError, ValueError) as exc:  # pragma: no cover - defensive guard
        raise ValueError(f"Invalid numeric value for {name}: {raw}") from exc


def _get_bool(name: str, default: str = 'false') -> bool:
    """Parse a boolean flag from environment variables."""
    value = os.getenv(name, default)
    if value is None:
        return False
    return value.strip().lower() in BOOL_TRUE


def _require_bool(value: str, key: str, errors: Dict[str, str]):
    if value.strip().lower() not in BOOL_TRUE and value.strip().lower() not in {"0", "false", "no", "off"}:
        errors[key] = "must be boolean (true/false)"


def _require_float(value: str, key: str, errors: Dict[str, str]):
    try:
        float(value)
    except (TypeError, ValueError):
        errors[key] = "must be numeric"


def _require_int(value: str, key: str, errors: Dict[str, str]):
    try:
        int(value)
    except (TypeError, ValueError):
        errors[key] = "must be an integer"


def validate_env() -> None:
    """Fail fast if required environment variables are missing or invalid."""
    missing = []
    invalid: Dict[str, str] = {}

    for key in sorted(MANDATORY_VARS):
        value = os.getenv(key)
        if (value is None or value.strip() == "") and key in ALIAS_MAP:
            for alias in ALIAS_MAP[key]:
                alias_val = os.getenv(alias)
                if alias_val and alias_val.strip():
                    os.environ.setdefault(key, alias_val)
                    value = alias_val
                    break
        if value is None or value.strip() == "":
            missing.append(key)
            continue
        if key in NUMERIC_FLOAT_VARS:
            _require_float(value, key, invalid)
        elif key in NUMERIC_INT_VARS:
            _require_int(value, key, invalid)
        elif key in BOOL_VARS:
            _require_bool(value, key, invalid)

    if IS_PROD:
        _validate_prod_constraints(missing, invalid)

    if missing or invalid:
        lines = []
        if missing:
            lines.append("Missing: " + ", ".join(sorted(missing)))
        if invalid:
            issues = ", ".join(f"{k} ({msg})" for k, msg in sorted(invalid.items()))
            lines.append("Invalid: " + issues)
        raise RuntimeError("Environment validation failed:\n" + "\n".join(lines))


def _validate_prod_constraints(missing, invalid):
    """Extra validations enforced only when running in production."""
    allow_autotrade = os.getenv("ALLOW_AUTOTRADE", "false").strip().lower() in BOOL_TRUE
    if not allow_autotrade:
        os.environ["AUTO_TRADE_ENABLED"] = "false"
        os.environ["SNIPE_ENABLED"] = "false"

    wallet_key = os.getenv("WALLET_ENCRYPTION_KEY")
    if wallet_key:
        try:
            decoded = base64.urlsafe_b64decode(wallet_key + "==")
        except Exception:  # pragma: no cover - defensive path
            invalid["WALLET_ENCRYPTION_KEY"] = "must be valid urlsafe base64"
        else:
            if len(decoded) < 32:
                invalid["WALLET_ENCRYPTION_KEY"] = "must decode to at least 32 bytes"
    else:
        missing.append("WALLET_ENCRYPTION_KEY")

    allow_broadcast = os.getenv("ALLOW_BROADCAST", "false").strip().lower() in BOOL_TRUE
    confirm_token = os.getenv("CONFIRM_TOKEN")
    if allow_broadcast and not confirm_token:
        missing.append("CONFIRM_TOKEN")


@dataclass
class TradingConfig:
    """Trading parameters"""

    max_slippage: float
    default_buy_amount_sol: float
    max_trade_size_sol: float
    daily_loss_limit_sol: float
    require_confirmation: bool
    min_liquidity_usd: float
    check_mint_authority: bool
    check_freeze_authority: bool
    honeypot_check_enabled: bool
    stop_loss_percentage: float
    take_profit_percentage: float
    trailing_stop_percentage: float


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
    twitter_bearer_token: Optional[str]
    twitter_client_id: Optional[str]
    twitter_client_secret: Optional[str]
    reddit_client_id: Optional[str]
    reddit_client_secret: Optional[str]
    reddit_user_agent: Optional[str]
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
            max_slippage=_normalize_percentage(_get_float('MAX_SLIPPAGE', '5.0')),
            default_buy_amount_sol=_get_float('DEFAULT_BUY_AMOUNT', os.getenv('DEFAULT_BUY_AMOUNT_SOL', '0.1') or '0.1'),
            max_trade_size_sol=_get_float('MAX_POSITION_SIZE_SOL', os.getenv('MAX_TRADE_SIZE_SOL', '1.0') or '1.0'),
            daily_loss_limit_sol=_get_float('MAX_DAILY_LOSS_SOL', os.getenv('DAILY_LOSS_LIMIT_SOL', '5.0') or '5.0'),
            require_confirmation=_get_bool('REQUIRE_CONFIRMATION', 'true'),
            min_liquidity_usd=_get_float('MIN_LIQUIDITY_USD', '10000'),
            check_mint_authority=_get_bool('CHECK_MINT_AUTHORITY', 'true'),
            check_freeze_authority=_get_bool('CHECK_FREEZE_AUTHORITY', 'true'),
            honeypot_check_enabled=_get_bool(
                'HONEYPOT_CHECK_ENABLED',
                os.getenv('HONEYPOT_DETECTION_ENABLED', 'true') or 'true'
            ),
            stop_loss_percentage=_normalize_percentage(_get_float('STOP_LOSS_PERCENTAGE', '10.0')),
            take_profit_percentage=_normalize_percentage(_get_float('TAKE_PROFIT_PERCENTAGE', '20.0')),
            trailing_stop_percentage=_normalize_percentage(_get_float('TRAILING_STOP_PERCENTAGE', '0.0')),
        )

        # Social Media (optional)
        twitter_api_key = os.getenv('TWITTER_API_KEY')
        twitter_api_secret = os.getenv('TWITTER_API_SECRET')
        twitter_bearer_token = os.getenv('TWITTER_BEARER_TOKEN')
        twitter_client_id = os.getenv('TWITTER_CLIENT_ID')
        twitter_client_secret = os.getenv('TWITTER_CLIENT_SECRET')
        reddit_client_id = os.getenv('REDDIT_CLIENT_ID')
        reddit_client_secret = os.getenv('REDDIT_CLIENT_SECRET')
        reddit_user_agent = os.getenv('REDDIT_USER_AGENT')
        discord_token = os.getenv('DISCORD_TOKEN')

        # Database
        database_url = os.getenv('DATABASE_URL', 'sqlite+aiosqlite:///trading_bot.db')

        # Monitoring
        enable_health_check_server = _get_bool('ENABLE_HEALTH_CHECK_SERVER', 'true')
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
            twitter_bearer_token=twitter_bearer_token,
            twitter_client_id=twitter_client_id,
            twitter_client_secret=twitter_client_secret,
            reddit_client_id=reddit_client_id,
            reddit_client_secret=reddit_client_secret,
            reddit_user_agent=reddit_user_agent,
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
            errors.append("MAX_SLIPPAGE must be between 0 and 50 percent")

        if self.trading.max_trade_size_sol <= 0:
            errors.append("MAX_POSITION_SIZE_SOL must be positive")

        if self.trading.daily_loss_limit_sol <= 0:
            errors.append("MAX_DAILY_LOSS_SOL must be positive")

        if errors:
            raise ValueError(
                "Configuration errors:\n" + "\n".join(f"- {e}" for e in errors)
            )


# Global config instance
_config: Optional[Config] = None


def get_config() -> Config:
    """Get global configuration instance"""
    global _config
    if _config is None:
        validate_env()
        _config = Config.from_env()
        _config.validate()
    return _config


def reload_config():
    """Reload configuration from environment"""
    global _config
    _config = None
    return get_config()
