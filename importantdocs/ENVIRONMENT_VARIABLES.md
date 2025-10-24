# Environment Variables Reference

## Standardized Variable Names (Preferred)

Use these variable names in production deployments:

### Critical Security
```bash
# REQUIRED: Wallet encryption key
# Generate with: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
WALLET_ENCRYPTION_KEY=<your-fernet-key>
```

### Telegram
```bash
TELEGRAM_BOT_TOKEN=<your-bot-token>
ADMIN_CHAT_ID=<your-telegram-user-id>
```

### Solana
```bash
SOLANA_RPC_URL=https://mainnet.helius-rpc.com/?api-key=<your-key>
WALLET_PRIVATE_KEY=<base58-private-key>
SOLANA_NETWORK=mainnet-beta
```

### Trading Parameters (Standardized Names)
```bash
# Position sizing
MAX_POSITION_SIZE_SOL=1.0           # ← Use this (not MAX_TRADE_SIZE_SOL)
DEFAULT_BUY_AMOUNT_SOL=0.1

# Risk management
MAX_DAILY_LOSS_SOL=5.0              # ← Use this (not DAILY_LOSS_LIMIT_SOL)
STOP_LOSS_PERCENTAGE=10.0
TAKE_PROFIT_PERCENTAGE=20.0
TRAILING_STOP_PERCENTAGE=0.0

# Execution
MAX_SLIPPAGE=5.0
REQUIRE_CONFIRMATION=true
```

### Protection
```bash
MIN_LIQUIDITY_USD=10000
CHECK_MINT_AUTHORITY=true
CHECK_FREEZE_AUTHORITY=true
HONEYPOT_CHECK_ENABLED=true
```

### Database
```bash
# Development (SQLite)
DATABASE_URL=sqlite+aiosqlite:///trading_bot.db

# Production (PostgreSQL recommended)
DATABASE_URL=postgresql://user:password@host:5432/trading_bot
```

### Social Media (Optional)
```bash
# Twitter
TWITTER_API_KEY=
TWITTER_API_SECRET=
TWITTER_BEARER_TOKEN=
TWITTER_CLIENT_ID=
TWITTER_CLIENT_SECRET=

# Reddit
REDDIT_CLIENT_ID=
REDDIT_CLIENT_SECRET=
REDDIT_USER_AGENT=TradingBot/1.0

# Discord
DISCORD_TOKEN=
```

### Enhanced RPC (Optional)
```bash
# Helius for faster transaction parsing
HELIUS_API_KEY=<your-helius-key>
```

### Monitoring (Optional)
```bash
ENABLE_HEALTH_CHECK_SERVER=true
HEALTH_CHECK_PORT=8080
```

### Logging
```bash
LOG_LEVEL=INFO
LOG_FILE=logs/trading_bot.log
```

---

## Legacy Variable Names (Backward Compatible)

These old names still work but are deprecated:

```bash
MAX_TRADE_SIZE_SOL=1.0          # ← Deprecated: Use MAX_POSITION_SIZE_SOL
DAILY_LOSS_LIMIT_SOL=5.0        # ← Deprecated: Use MAX_DAILY_LOSS_SOL
```

**Migration:** Update your `.env` file to use the new standardized names. Old names will continue to work as fallbacks to ensure backward compatibility.

---

## Production Best Practices

### 1. Secure Storage
```bash
# DO NOT commit .env to git
# Use secure storage instead:

# AWS Systems Manager
aws ssm put-parameter --name /trading-bot/wallet-key --value "<key>" --type SecureString

# Kubernetes Secrets
kubectl create secret generic trading-bot-secrets \
  --from-literal=WALLET_ENCRYPTION_KEY=<key>

# HashiCorp Vault
vault kv put secret/trading-bot WALLET_ENCRYPTION_KEY=<key>
```

### 2. RPC Configuration
```bash
# Free tier (rate limited)
SOLANA_RPC_URL=https://api.mainnet-beta.solana.com

# Production (recommended)
SOLANA_RPC_URL=https://mainnet.helius-rpc.com/?api-key=<key>
# or
SOLANA_RPC_URL=https://rpc.helius.xyz/?api-key=<key>
# or
SOLANA_RPC_URL=https://<your-triton-node>.rpcpool.com/<key>
```

### 3. Database Configuration
```bash
# Development
DATABASE_URL=sqlite+aiosqlite:///trading_bot.db

# Production (High Availability)
DATABASE_URL=postgresql://user:password@host:5432/trading_bot?sslmode=require

# Production (AWS RDS)
DATABASE_URL=postgresql://admin:pass@your-rds.amazonaws.com:5432/trading_bot

# Production (Google Cloud SQL)
DATABASE_URL=postgresql://user:pass@/trading_bot?host=/cloudsql/project:region:instance
```

---

## Configuration Validation

Run health check to verify configuration:

```bash
python scripts/health_check.py
```

Expected output:
```
✅ WALLET_ENCRYPTION_KEY
✅ TELEGRAM_BOT_TOKEN
✅ SOLANA_RPC_URL
✅ Database initialization
✅ All modules
✅ Health check PASSED
```

---

## Environment-Specific Configs

### Development
```bash
# .env.development
SOLANA_NETWORK=devnet
SOLANA_RPC_URL=https://api.devnet.solana.com
DATABASE_URL=sqlite+aiosqlite:///trading_bot_dev.db
LOG_LEVEL=DEBUG
```

### Staging
```bash
# .env.staging
SOLANA_NETWORK=mainnet-beta
SOLANA_RPC_URL=https://mainnet.helius-rpc.com/?api-key=<key>
DATABASE_URL=postgresql://user:pass@staging-db:5432/trading_bot
LOG_LEVEL=INFO
```

### Production
```bash
# .env.production (or from secrets manager)
SOLANA_NETWORK=mainnet-beta
SOLANA_RPC_URL=https://mainnet.helius-rpc.com/?api-key=<premium-key>
DATABASE_URL=postgresql://user:pass@prod-db:5432/trading_bot?sslmode=require
LOG_LEVEL=INFO
ENABLE_HEALTH_CHECK_SERVER=true
```

---

## Verification Commands

### Check Current Config
```bash
python -c "
from src.config import get_config
config = get_config()
print('Database:', config.database_url)
print('RPC:', config.solana_rpc_url)
print('Network:', config.solana_network)
print('Max Position:', config.trading.max_trade_size_sol, 'SOL')
print('Daily Loss Limit:', config.trading.daily_loss_limit_sol, 'SOL')
"
```

### Test Configuration
```bash
# Run full health check
python scripts/health_check.py

# Test RPC connection
python -c "
import asyncio
from solana.rpc.async_api import AsyncClient
from src.config import get_config

async def test():
    config = get_config()
    client = AsyncClient(config.solana_rpc_url)
    version = await client.get_version()
    print('RPC Version:', version.value)
    await client.close()

asyncio.run(test())
"
```

---

## Quick Reference

| Variable | Old Name (Deprecated) | Purpose |
|----------|----------------------|---------|
| `MAX_POSITION_SIZE_SOL` | `MAX_TRADE_SIZE_SOL` | Maximum trade size |
| `MAX_DAILY_LOSS_SOL` | `DAILY_LOSS_LIMIT_SOL` | Daily loss limit |
| `DEFAULT_BUY_AMOUNT_SOL` | `DEFAULT_BUY_AMOUNT` | Default buy amount |
| `HONEYPOT_CHECK_ENABLED` | `HONEYPOT_DETECTION_ENABLED` | Enable honeypot checks |

**Migration Guide:** Replace old names with new names in your `.env` file. Both will work during transition period.

---

## Security Checklist

- [ ] `WALLET_ENCRYPTION_KEY` stored securely (not in git)
- [ ] `.env` file in `.gitignore`
- [ ] Production uses PostgreSQL (not SQLite)
- [ ] RPC URL uses dedicated endpoint (not free tier)
- [ ] `ADMIN_CHAT_ID` set to your Telegram ID
- [ ] Database connection uses SSL (`?sslmode=require`)
- [ ] Secrets rotated quarterly

---

**Last Updated:** October 24, 2025  
**Version:** 1.0.0

