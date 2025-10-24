# Production-Grade Trading Bot - Implementation Guide

## Overview

This guide documents the implementation of all production-grade recommendations for the Solana trading bot ecosystem. The platform now features:

- ✅ Full database persistence for social trading and sniper state
- ✅ Manual `/buy` and `/sell` commands with risk controls
- ✅ Graceful shutdown handling
- ✅ Hardened wallet encryption key management
- ✅ Resumable, multi-tenant sniper system
- ✅ Unified trade execution service
- ✅ RPC call batching and rate limiting
- ✅ Comprehensive risk control enforcement
- ✅ Sentiment and community data integration into AI

---

## Quick Start

### 1. Environment Setup

```bash
# Required: Wallet encryption key
export WALLET_ENCRYPTION_KEY="your-fernet-key-here"

# Generate a new key if needed:
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# Telegram
export TELEGRAM_BOT_TOKEN="your-bot-token"
export ADMIN_CHAT_ID="your-telegram-id"

# Solana
export SOLANA_RPC_URL="https://api.mainnet-beta.solana.com"
export WALLET_PRIVATE_KEY="your-base58-private-key"

# Optional: Social sentiment
export TWITTER_API_KEY="..."
export TWITTER_BEARER_TOKEN="..."
export REDDIT_CLIENT_ID="..."
export DISCORD_TOKEN="..."

# Optional: Enhanced RPC
export HELIUS_API_KEY="..."  # Faster transaction parsing
```

### 2. Database Initialization

```bash
# The database is automatically initialized on first run
python scripts/run_bot.py
```

Tables created:
- `trades` - All trade history
- `positions` - Open positions with stop-loss/take-profit
- `user_wallets` - Encrypted per-user wallets
- `tracked_wallets` - Wallet intelligence, trader profiles, copy relationships
- `user_settings` - Risk controls and sniper configuration
- `snipe_runs` - AI decision snapshots

### 3. Running the Bot

```bash
# Standard run
python scripts/run_bot.py

# With logging
python scripts/run_bot.py 2>&1 | tee logs/bot_$(date +%Y%m%d).log

# Background with systemd (production)
sudo systemctl start trading-bot
```

---

## Core Features

### User Wallets

Each user gets a unique Solana wallet:

```python
# Automatic on /start
/start  # Creates encrypted wallet, registers trader, awards points

# Check wallet
/wallet       # Shows address, balance, trading stats
/deposit      # Deposit instructions
/balance      # Quick balance check
/export_keys  # Export private key for Phantom/Solflare
```

**Security:**
- Private keys encrypted with Fernet (AES-128)
- Master key required from `WALLET_ENCRYPTION_KEY`
- Keys never logged or exposed
- Per-user isolation

### Manual Trading

```bash
# Buy tokens
/buy <token_mint> <amount_sol> [symbol]
# Example: /buy EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v 0.5 USDC

# Sell tokens
/sell <token_mint> [amount_tokens|all]
# Example: /sell EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v all
```

**Risk Controls Applied:**
- Max trade size (`max_trade_size_sol` from user settings)
- Daily loss limit (`daily_loss_limit_sol`)
- Balance verification
- Honeypot detection (if enabled)
- Minimum liquidity check

### AI-Powered Analysis

```bash
/ai <token_mint>        # Full AI analysis
/analyze <token_mint>   # Alias

# Returns:
# - ML prediction (probability of success)
# - Pattern recognition (stealth launch, whale accumulation, etc.)
# - Market regime (bull/bear/volatile)
# - Sentiment analysis (Twitter, Reddit, Discord)
# - Community ratings
# - Position sizing recommendation
```

**AI Components:**
- `MLPredictionEngine` - RandomForest classifier trained on historical trades
- `PatternRecognitionEngine` - Identifies profitable patterns
- `AdaptiveStrategyOptimizer` - Adjusts strategy weights based on performance
- `SmartPositionSizer` - Kelly Criterion-based sizing

### Auto-Sniper

```bash
# Enable auto-sniper
/snipe_enable

# Configure
# - Max buy amount (default: 0.1 SOL)
# - Min liquidity (default: 10,000 USD)
# - Min AI confidence (default: 65%)
# - Max daily snipes (default: 10)

# Check status
/snipe

# Disable
/snipe_disable
```

**How It Works:**
1. `PumpFunMonitor` detects new token launches (Birdeye, DexScreener, Pump.fun)
2. AI analyzes token (liquidity, sentiment, pattern)
3. If confidence > threshold, executes Jito-protected buy
4. Position managed by automated trader (stop-loss, take-profit)
5. All decisions logged to `snipe_runs` table

**Persistence:**
- Settings saved to `user_settings` table
- Restarts resume enabled snipers
- Daily limits persist across restarts

### Copy Trading

```bash
# View leaderboard
/leaderboard

# Copy a trader
/copy_trader <trader_id> <amount_per_trade> [copy_percentage]
# Example: /copy_trader 123456789 0.1 100

# Stop copying
/stop_copy <trader_id>

# View your copies
/my_stats
```

**Features:**
- Automatic trade mirroring (buys and sells)
- Configurable copy percentage (scale positions)
- Max amount per trade
- Max daily trades
- Real-time follower count updates
- Profit sharing tracking

**Trader Tiers:**
- Bronze: 0-40 reputation
- Silver: 40-60
- Gold: 60-75
- Platinum: 75-90
- Diamond: 90+

### Wallet Intelligence

```bash
# Track a smart wallet
/track <wallet_address> [label]

# View rankings
/rankings

# Start automated trading
/autostart

# Check status
/autostatus

# Stop automated trading
/autostop
```

**Automated Trading:**
1. Scans tracked wallets every 30 seconds
2. Detects token buys (batched RPC calls)
3. Calculates confidence based on:
   - Number of wallets buying
   - Wallet quality scores
   - Recency of buys
4. Executes trades above confidence threshold
5. Manages positions with stop-loss/take-profit

### Community Intelligence

```bash
# View community ratings
/community <token_mint>

# Rate a token
/rate_token <token_mint> <rating_1_to_10> [comment]
```

**Crowdsourced Data:**
- Token ratings (0-10)
- Risk flags
- Community sentiment
- Scam detection

---

## Architecture

### Trade Execution Flow

```
User Input / Trigger
    ↓
TradeExecutionService.execute_buy/sell()
    ├→ Load user settings from database
    ├→ Validate risk limits (max size, daily loss)
    ├→ Check balance
    ├→ Run protection checks (honeypot, liquidity)
    ├→ Get quote from Jupiter
    ├→ Execute swap (standard or Jito bundle)
    ├→ Record trade to database
    ├→ Open/close position
    ├→ Award reward points
    └→ Propagate to copy traders (if trader)
```

### State Persistence

**On Startup:**
```python
# 1. Database initialized
await db_manager.init_db()

# 2. Social trading state loaded
await social_marketplace.initialize()
# Loads: trader profiles, copy relationships, leaderboard

# 3. Sniper state loaded
await sniper.load_persistent_settings()
# Loads: enabled users, settings, active snipes

# 4. Bot starts
await bot.start(shutdown_event)
```

**During Operation:**
- All trades → `trades` table
- Positions → `positions` table (updated on partial/full exit)
- Sniper decisions → `snipe_runs` table
- Copy relationships → `tracked_wallets` (copy_trader_id, copy_enabled)
- User settings → `user_settings` (trade limits, sniper config)

### RPC Optimization

**Batching Strategy:**
```python
# Automated trader processes 20 wallets at a time
batch_size = 20
for batch in range(0, wallet_count, batch_size):
    tasks = [fetch_signatures(addr) for addr in batch]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    await asyncio.sleep(0.05)  # Rate limit pause
```

**Transaction Caching:**
```python
# Cache parsed transactions for 10 minutes
self._transaction_cache[signature] = {
    'timestamp': datetime.now(),
    'mint': token_mint
}
```

**Helius Enhancement:**
- If `HELIUS_API_KEY` set, uses enhanced transaction endpoint
- Faster parsing, pre-analyzed swap data
- Falls back to standard RPC if unavailable

---

## Configuration

### User Settings (per user, stored in database)

```python
# Trading
max_trade_size_sol = 1.0
daily_loss_limit_sol = 5.0
slippage_percentage = 5.0
require_confirmation = True

# Risk management
use_stop_loss = True
default_stop_loss_percentage = 10.0
use_take_profit = True
default_take_profit_percentage = 20.0

# Protection
check_honeypots = True
min_liquidity_usd = 10000.0

# Sniper
snipe_enabled = False
snipe_max_amount = 0.1
snipe_min_liquidity = 10000.0
snipe_min_confidence = 0.65
snipe_max_daily = 10
snipe_only_strong_buy = True
```

**Modify via:**
- Database direct edit (for admin)
- Bot commands (future: `/settings`)
- Web dashboard (future enhancement)

### Global Config (config.py)

```python
# Trading
max_trade_size_sol = 1.0
max_slippage = 5.0
stop_loss_percentage = 10.0
take_profit_percentage = 20.0

# Protection
honeypot_check_enabled = True
min_liquidity_usd = 10000.0

# Jito
jito_enabled = True
jito_tip_lamports = 100000
```

---

## Monitoring

### Metrics Tracked

```python
# BotMonitor
monitor.record_trade_success()
monitor.record_trade_failure()
monitor.record_request()  # RPC calls
monitor.record_metric(name, value, tags)

# Automated Trader
- scan_duration_seconds
- rpc_requests (per scan)
- opportunities_found
- wallets_with_activity

# Trade Executor
- trades_executed
- trade_failures
- positions_opened
- positions_closed
```

### Logs

```bash
# Bot logs
tail -f logs/trading_bot.log

# Key log patterns
grep "🎯 NEW TOKEN" logs/trading_bot.log        # Sniper detections
grep "BUY executed" logs/trading_bot.log        # Successful buys
grep "SELL executed" logs/trading_bot.log       # Successful sells
grep "✨ OPPORTUNITY" logs/trading_bot.log      # Automated trader signals
grep "🎯 SNIPE EXECUTED" logs/trading_bot.log   # Sniper executions
```

---

## Database Schema Reference

### trades
- `user_id`, `signature`, `trade_type` (buy/sell)
- `token_mint`, `amount_sol`, `amount_tokens`, `price`
- `success`, `pnl_sol`, `pnl_percentage`
- `context` (manual, ai_signal, sniper, copy_trade, automated)

### positions
- `user_id`, `position_id`, `token_mint`
- `entry_price`, `entry_amount_sol`, `entry_amount_tokens`
- `exit_price`, `exit_amount_sol` (if closed)
- `is_open`, `pnl_sol`, `pnl_percentage`
- `stop_loss_percentage`, `take_profit_percentage`
- `source` (context of entry)

### user_wallets
- `user_id`, `public_key`, `encrypted_private_key`
- `sol_balance`, `last_balance_update`

### tracked_wallets
- `user_id`, `wallet_address`, `label`
- `total_trades`, `profitable_trades`, `win_rate`, `total_pnl`, `score`
- **Trader fields:** `is_trader`, `trader_tier`, `followers`, `reputation_score`
- **Copy fields:** `copy_trader_id`, `copy_enabled`, `copy_amount_sol`, `copy_percentage`

### user_settings
- `user_id`
- **Trade limits:** `max_trade_size_sol`, `daily_loss_limit_sol`, `slippage_percentage`
- **Risk:** `use_stop_loss`, `default_stop_loss_percentage`, `use_take_profit`, `default_take_profit_percentage`
- **Protection:** `check_honeypots`, `min_liquidity_usd`
- **Sniper:** `snipe_enabled`, `snipe_max_amount`, `snipe_min_liquidity`, `snipe_min_confidence`, `snipe_max_daily`, `snipe_daily_used`, `snipe_last_reset`

### snipe_runs
- `snipe_id`, `user_id`, `token_mint`, `amount_sol`
- `status` (ANALYZED, MONITORING, EXECUTING, COMPLETED, FAILED)
- `ai_confidence`, `ai_recommendation`, `ai_snapshot`
- `decision_timestamp`, `triggered_at`, `completed_at`

---

## Operational Procedures

### Graceful Shutdown

```bash
# Send SIGTERM
kill -TERM <pid>

# Or Ctrl+C
# Triggers:
# 1. shutdown_event.set()
# 2. Bot waits for current operations
# 3. Sniper stops
# 4. Telegram updater stops
# 5. Database connections close
# 6. Solana client closes
```

### Backup Database

```bash
# Stop bot
sudo systemctl stop trading-bot

# Backup
cp trading_bot.db trading_bot.db.backup_$(date +%Y%m%d_%H%M%S)

# Or use SQLite backup
sqlite3 trading_bot.db ".backup trading_bot.db.backup"

# Start bot
sudo systemctl start trading-bot
```

### Rotate Encryption Key

```bash
# Generate new key
python scripts/rotate_wallet_key.py

# Follows prompts to:
# 1. Generate new Fernet key
# 2. Re-encrypt all user wallets
# 3. Update database
# 4. Update environment variable
```

### Migrate to PostgreSQL (Production)

```bash
# 1. Export SQLite data
python scripts/export_to_postgres.py

# 2. Update config
export DATABASE_URL="postgresql://user:pass@host:5432/trading_bot"

# 3. Restart bot
```

---

## Troubleshooting

### "WALLET_ENCRYPTION_KEY environment variable is required"

**Cause:** Missing encryption key

**Fix:**
```bash
export WALLET_ENCRYPTION_KEY=$(python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
```

**Important:** Save this key securely! Without it, user wallets are unrecoverable.

### RPC Rate Limiting

**Symptoms:**
- "429 Too Many Requests" errors
- Slow wallet scans

**Fix:**
1. Use Helius or Triton RPC (higher limits)
2. Reduce `batch_size` in automated_trading.py
3. Increase `await asyncio.sleep(0.05)` between batches

### Sniper Not Triggering

**Check:**
```python
# 1. Sniper enabled?
SELECT user_id, snipe_enabled FROM user_settings WHERE snipe_enabled = 1;

# 2. Daily limit reached?
SELECT user_id, snipe_daily_used, snipe_max_daily FROM user_settings;

# 3. Check snipe runs
SELECT * FROM snipe_runs ORDER BY decision_timestamp DESC LIMIT 10;

# 4. Check logs
grep "NEW TOKEN" logs/trading_bot.log | tail -20
```

### Copy Trading Not Working

**Check:**
```python
# 1. Copy relationship exists?
SELECT * FROM tracked_wallets WHERE copy_trader_id IS NOT NULL AND copy_enabled = 1;

# 2. Trader profile exists?
SELECT * FROM tracked_wallets WHERE is_trader = 1;

# 3. Check social marketplace initialization
# Look for: "Loaded X trader profiles" in logs
```

---

## Performance Tuning

### RPC Latency

```python
# Use dedicated node
export SOLANA_RPC_URL="https://your-dedicated-node.com"

# Or Helius with higher tier
export HELIUS_API_KEY="your-premium-key"
export SOLANA_RPC_URL="https://mainnet.helius-rpc.com/?api-key=your-key"
```

### Database Performance

```bash
# Analyze query performance
sqlite3 trading_bot.db

# Add indexes (if not exists)
CREATE INDEX IF NOT EXISTS idx_trades_user_timestamp ON trades(user_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_positions_user_open ON positions(user_id, is_open);
CREATE INDEX IF NOT EXISTS idx_tracked_wallets_score ON tracked_wallets(score DESC);
```

### Memory Usage

```python
# Limit transaction cache size
self._transaction_cache_max = 1000  # In automated_trading.py

# Clear old entries periodically
if len(self._transaction_cache) > self._transaction_cache_max:
    oldest = sorted(self._transaction_cache.items(), key=lambda x: x[1]['timestamp'])[:100]
    for sig, _ in oldest:
        del self._transaction_cache[sig]
```

---

## API Reference

### TradeExecutionService

```python
# Buy
await trade_executor.execute_buy(
    user_id=123,
    token_mint="...",
    amount_sol=0.5,
    token_symbol="TOKEN",
    reason="manual",
    context="manual_command",
    execution_mode="standard",  # or "jito"
    metadata={"custom": "data"}
)

# Sell
await trade_executor.execute_sell(
    user_id=123,
    token_mint="...",
    amount_tokens=None,  # None = sell all
    reason="stop_loss",
    context="risk_management",
    metadata={"trigger": "stop_loss_10%"}
)
```

### AIStrategyManager

```python
analysis = await ai_manager.analyze_opportunity(
    token_data={
        'liquidity_usd': 50000,
        'volume_24h': 100000,
        'holder_count': 1000,
        # ... more fields
    },
    portfolio_value=10.0,
    sentiment_snapshot=await sentiment_aggregator.get_token_sentiment(token_mint),
    community_signal=await community_intel.get_community_signal(token_mint)
)

# Returns:
# {
#     'action': 'buy' | 'sell' | 'neutral',
#     'confidence': 0.0-1.0,
#     'position_size': <SOL amount>,
#     'reasoning': "...",
#     'ml_prediction': {...},
#     'pattern': 'stealth_launch' | ...
# }
```

### WalletIntelligenceEngine

```python
# Track wallet
await wallet_intelligence.track_wallet(
    wallet_address="...",
    label="Smart Money #1"
)

# Get rankings
rankings = await wallet_intelligence.get_ranked_wallets(limit=10)

# Analyze performance
metrics = await wallet_intelligence.analyze_wallet_performance(wallet_address)
```

---

## Production Deployment Checklist

- [ ] Set `WALLET_ENCRYPTION_KEY` in secure environment (KMS, Vault)
- [ ] Configure monitoring (Grafana, Datadog)
- [ ] Set up database backups (daily, off-site)
- [ ] Use dedicated Solana RPC node (Helius, Triton)
- [ ] Configure alerting (Telegram, PagerDuty)
- [ ] Set up log rotation (`logrotate`)
- [ ] Test graceful shutdown (`SIGTERM` handling)
- [ ] Document key rotation procedure
- [ ] Set up health checks (Kubernetes liveness/readiness)
- [ ] Configure rate limits and circuit breakers

---

## Support

**Documentation:**
- See `PRODUCTION_READINESS_REPORT.md` for detailed assessment
- See `README.md` for feature overview

**Issues:**
- Check logs: `logs/trading_bot.log`
- Check database: `sqlite3 trading_bot.db`
- Review user settings: `SELECT * FROM user_settings WHERE user_id = X;`

**Community:**
- Telegram group: [link]
- GitHub issues: [link]

---

**Last Updated:** 2025-10-24  
**Version:** 1.0.0  
**Status:** Production Ready

