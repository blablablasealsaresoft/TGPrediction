# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an **AI-powered Solana trading bot** with Telegram interface. It's a production-ready, enterprise-grade platform featuring neural AI that learns from trades, active sentiment scanning, copy trading, auto-sniping, and advanced MEV protection.

**Core Value Proposition:**
- Unified Neural Intelligence that learns and adapts
- Active sentiment scanning (Twitter/Reddit) to find tokens before they pump
- Copy trading from 441+ elite wallets
- Auto-sniper with 6-layer protection system
- Flash loan arbitrage and prediction markets
- MEV protection via Jito bundles

## Repository Structure

```
TGbot/
├── src/
│   ├── bot/                    # Main bot implementation
│   │   ├── main.py            # RevolutionaryTradingBot class (core orchestrator)
│   │   └── basic_bot.py       # Legacy/simplified bot
│   ├── modules/               # Feature modules
│   │   ├── unified_neural_engine.py      # AI that learns from all signals
│   │   ├── active_sentiment_scanner.py   # Twitter/Reddit monitoring
│   │   ├── ai_strategy_engine.py         # ML predictions
│   │   ├── social_trading.py             # Copy trading marketplace
│   │   ├── sentiment_analysis.py         # Social media aggregation
│   │   ├── token_sniper.py               # Auto-sniper for new launches
│   │   ├── jupiter_client.py             # DEX aggregation via Jupiter
│   │   ├── trade_execution.py            # Trade execution layer
│   │   ├── wallet_manager.py             # Per-user wallet management
│   │   ├── database.py                   # SQLAlchemy async ORM
│   │   ├── elite_protection.py           # 6-layer honeypot detection
│   │   ├── automated_trading.py          # Auto-trading engine
│   │   ├── flash_loan_engine.py          # Flash loan arbitrage
│   │   ├── bundle_launch_predictor.py    # Pre-launch detection
│   │   ├── prediction_markets.py         # Polymarket-style staking
│   │   └── ui_formatter.py               # Enterprise UI formatting
│   ├── ops/                   # Operational utilities
│   │   ├── health.py          # Health check system
│   │   ├── probes.py          # HTTP probe server
│   │   └── broadcast.py       # Production safety guards
│   └── config.py              # Environment validation & config
├── scripts/
│   ├── run_bot.py             # Main entry point (production)
│   ├── seed_tracked_wallets.py # Load elite wallets for copy trading
│   ├── train_ai_model.py      # Train ML models
│   └── verify_all_features.py # Feature verification
├── tests/
│   ├── unit/                  # Unit tests
│   ├── conftest.py            # Pytest fixtures
│   └── test_*.py              # Integration tests
├── requirements/
│   └── dev.lock               # Locked dependencies
├── deploy/                    # Deployment configs
└── docs/                      # Documentation
```

## Development Commands

### Running the Bot

```bash
# Activate virtual environment
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

# Load environment variables
set -a; source .env; set +a  # Linux/Mac
# (Windows: set variables manually or use .env file)

# Run bot on mainnet (production mode)
python scripts/run_bot.py --network mainnet

# Run bot on devnet (testing)
python scripts/run_bot.py --network devnet

# Run in read-only mode (no trade execution)
python scripts/run_bot.py --network mainnet --read-only

# Disable auto-trading features
python scripts/run_bot.py --network mainnet --no-auto-trade
```

### Testing

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/unit/test_config.py

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=src --cov-report=html

# Run integration tests (requires API keys)
pytest tests/test_copy_trading.py
```

### Database Operations

```bash
# The bot automatically initializes the database on first run
# Database file: trading_bot.db (SQLite)

# Backup database
cp trading_bot.db "trading_bot.db.backup.$(date +%Y%m%d_%H%M%S)"

# Migrate database (when schema changes)
python scripts/migrate_database.py
```

### Seeding Data

```bash
# Load 441 elite wallets for copy trading
python scripts/seed_tracked_wallets.py \
    --file importantdocs/unique_wallets_list.txt \
    --min-score 70 \
    --copy-enabled true

# Train AI models on historical data
python scripts/train_ai_model.py
```

### Monitoring & Health Checks

```bash
# View live logs
tail -f logs/trading_bot.jsonl

# Check bot health (HTTP endpoint)
curl http://localhost:8080/health

# Monitor bot status
python scripts/bot_status.py

# View performance metrics
python scripts/monitor_performance.py
```

## Architecture Overview

### 1. Bot Entry Point Flow

`scripts/run_bot.py` → `BotRunner` → `RevolutionaryTradingBot` → Telegram handlers

- **run_bot.py**: Handles CLI args, logging setup, environment validation, graceful shutdown
- **BotRunner**: Manages lifecycle (database init, Solana client, health probes)
- **RevolutionaryTradingBot**: Main bot class that orchestrates all modules

### 2. Configuration Management

**Environment Variables** (see `ENV_ULTIMATE_FINAL.txt` for complete reference):
- Validated by `src/config.py` on startup
- Production mode (`ENV=prod`) enforces strict validation
- Mandatory keys: `TELEGRAM_BOT_TOKEN`, `ADMIN_CHAT_ID`, `WALLET_PRIVATE_KEY`, `WALLET_ENCRYPTION_KEY`

**Production Safety Guards**:
- `ALLOW_BROADCAST=false` by default (prevents actual transactions)
- `CONFIRM_TOKEN` required for trades when broadcast is enabled
- `READ_ONLY_MODE` disables all execution paths
- `ALLOW_AUTOTRADE` gates auto-trading and sniper features

### 3. Core Intelligence Systems

#### Unified Neural Engine (`unified_neural_engine.py`)
- **Purpose**: Combines AI, sentiment, wallet intelligence, community ratings into ONE learned score
- **Key Feature**: Weights auto-adjust based on which signals actually work
- **Learning**: After 100+ trades, system knows which patterns succeed
- **Cross-correlation**: Detects when multiple signals align (3+ strong = 15% boost)

#### Active Sentiment Scanner (`active_sentiment_scanner.py`)
- **Purpose**: Actively scans Twitter/Reddit every 5 minutes for trending Solana tokens
- **Output**: Viral tokens ranked by mentions, sentiment, source diversity
- **Integration**: Feeds into unified neural engine
- **Key Methods**: `scan_twitter()`, `scan_reddit()`, `get_trending_tokens()`

#### AI Strategy Engine (`ai_strategy_engine.py`)
- **ML Models**: RandomForest, GradientBoosting for price prediction
- **Features**: liquidity, volume, sentiment, holder distribution, wallet signals
- **Training**: `train_ai_model.py` script trains on historical data
- **Prediction**: Returns probability, confidence, recommendation (buy/sell/hold)

#### Social Trading (`social_trading.py`)
- **Marketplace**: Users can copy elite traders
- **Leaderboard**: Rankings by win rate, total profit, reputation
- **Copy Mechanics**: Automatic execution when tracked wallet trades
- **Database**: `TrackedWallet` table with copy relationships

### 4. Trading Execution Flow

```
User Command → RevolutionaryTradingBot handler
  ↓
  AI Analysis (unified neural + sentiment + protection)
  ↓
  Trade Execution Service
  ↓
  Jupiter Client (DEX aggregation)
  ↓
  Jito Bundle (MEV protection)
  ↓
  Solana Transaction
  ↓
  Database Recording (Trade, Position, UserSettings)
```

**Key Classes**:
- `TradeExecutionService`: Coordinates trade execution
- `JupiterClient`: Fetches best swap routes from Jupiter aggregator
- `AntiMEVProtection`: Submits transactions via Jito bundles

### 5. Wallet Architecture

**Per-User Wallets** (`wallet_manager.py`):
- Each Telegram user gets their own Solana wallet
- Private keys encrypted with `WALLET_ENCRYPTION_KEY`
- Stored in `UserWallet` table
- Automatic wallet creation on `/start`

**Platform Wallet**:
- Defined by `WALLET_PRIVATE_KEY` in environment
- Used for platform operations, fee collection

### 6. Database Schema

**Key Tables** (defined in `src/modules/database.py`):
- `trades`: All trade records (buy/sell, PnL tracking)
- `positions`: Open positions with entry/exit data
- `user_wallets`: Per-user wallet credentials (encrypted)
- `tracked_wallets`: Wallets being monitored for copy trading
- `user_settings`: Per-user configuration (risk limits, auto-trading)
- `snipe_runs`: Auto-sniper execution history

**Database Manager** (`DatabaseManager` class):
- Async SQLAlchemy with `AsyncSession`
- SQLite by default (`sqlite+aiosqlite:///trading_bot.db`)
- Can use PostgreSQL in production

### 7. Protection Systems

**6-Layer Elite Protection** (`elite_protection.py`):
1. Honeypot detection (6 different methods)
2. Mint authority checks (prevents infinite minting)
3. Freeze authority checks (prevents wallet freezing)
4. Holder distribution analysis (detects concentrated ownership)
5. Twitter handle reuse detection (catches serial scammers)
6. Contract deep analysis (high-level security scanning)

**Auto-Sniper Safety** (`token_sniper.py`):
- Min liquidity: $2,000+
- AI confidence threshold: 65%+
- Daily limits: 5 snipes max, 0.2 SOL max per snipe
- All 6 protection layers applied before execution

### 8. Advanced Features

**Flash Loan Arbitrage** (`flash_loan_engine.py`):
- Detects price discrepancies across DEXs
- Executes atomic arbitrage via Marginfi/Solend
- Risk-free profit opportunities

**Bundle Launch Predictor** (`bundle_launch_predictor.py`):
- Pre-launch monitoring (2-6 hours early)
- Whale tracking and team verification
- Ultra-confidence predictions (80-85% accuracy)

**Prediction Markets** (`prediction_markets.py`):
- Polymarket-style staking on token predictions
- Network effects engine for viral growth
- Community-driven intelligence

## Common Development Tasks

### Adding a New Telegram Command

1. Add handler in `src/bot/main.py`:
```python
async def my_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    # Your logic here
    await update.message.reply_text("Response")

# Register in setup_handlers()
self.application.add_handler(CommandHandler("mycommand", self.my_command))
```

2. Update help text in the `/help` command handler

### Adding a New Module

1. Create file in `src/modules/my_module.py`
2. Import in `src/bot/main.py`
3. Initialize in `RevolutionaryTradingBot.__init__()`
4. Add corresponding database tables in `src/modules/database.py` if needed

### Modifying Environment Variables

1. Update `src/config.py` with new variable definitions:
   - Add to `MANDATORY_VARS`, `NUMERIC_FLOAT_VARS`, `BOOL_VARS`, or `STRING_VARS`
   - Add validation logic in `validate_env()`
2. Update `ENV_ULTIMATE_FINAL.txt` template
3. Add to `Config` dataclass and `from_env()` method

### Running Tests After Changes

```bash
# Always run tests before committing
pytest

# Run specific test for modified module
pytest tests/unit/test_database.py -v

# Check code formatting
black src/ tests/
flake8 src/ tests/
```

## Deployment

### Production Deployment (Ubuntu/Linux)

See `UBUNTU_DEPLOYMENT.md` for complete guide. Quick steps:

```bash
# 1. Clone repo
git clone <repo-url> TGbot && cd TGbot

# 2. Setup environment
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 3. Configure .env
cp ENV_ULTIMATE_FINAL.txt .env
nano .env  # Fill in secrets

# 4. Setup systemd service
sudo cp deploy/systemd/trading-bot.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable trading-bot
sudo systemctl start trading-bot

# 5. Monitor
sudo journalctl -u trading-bot -f
```

### Docker Deployment

```bash
docker-compose up -d
```

## Important Design Patterns

### 1. Async/Await Throughout
- All I/O operations are async (database, RPC calls, HTTP requests)
- Use `async with` for session management
- Database uses `AsyncSession` from SQLAlchemy

### 2. Production Safety Guards
- Never execute trades without explicit confirmation in production
- `ALLOW_BROADCAST=false` by default
- `CONFIRM_TOKEN` required for actual trades
- Read-only mode available for testing

### 3. Graceful Error Handling
- Try/except blocks around all external API calls
- Fallback RPC URLs if primary fails
- Detailed error logging with context
- User-friendly error messages via Telegram

### 4. Modular Architecture
- Each feature is a separate module in `src/modules/`
- Main bot class orchestrates modules
- Database manager provides unified data access
- Configuration centralized in `src/config.py`

### 5. Learning Systems
- Unified neural engine learns from trade outcomes
- Weight adjustment based on signal accuracy
- Cross-signal correlation detection
- Time-based pattern recognition

## Key Integration Points

### Solana Blockchain
- **Library**: `solana-py` with `solders` for types
- **RPC**: Helius (premium), with 3 fallback RPCs
- **Transactions**: Versioned transactions for efficiency
- **MEV Protection**: Jito bundles with priority fees

### Jupiter Aggregator
- **API**: `https://quote-api.jup.ag/v6`
- **Purpose**: Best swap routes across all Solana DEXs
- **Integration**: `JupiterClient` class in `jupiter_client.py`

### Jito MEV Protection
- **Block Engine**: `https://mainnet.block-engine.jito.wtf/api/v1`
- **Tip Account**: Configured in environment
- **Bundle Execution**: Atomic transaction bundles

### Social Media APIs
- **Twitter**: OAuth 2.0 with bearer token
- **Reddit**: OAuth2 with client credentials
- **Discord**: Bot token authentication

### External Data Sources
- **Helius**: Token metadata, holder distribution
- **Birdeye**: Token analytics, new launches
- **DexScreener**: Pair monitoring, price data

## Testing Strategy

### Unit Tests (`tests/unit/`)
- Test individual functions/classes in isolation
- Mock external dependencies (RPC, APIs, database)
- Fast execution, no network calls

### Integration Tests (`tests/`)
- Test complete workflows (copy trading, auto-sniper)
- Use real database (in-memory SQLite)
- Mock only external APIs (Twitter, Solana RPC)

### E2E Tests
- `test_sniper_e2e.py`: Full auto-sniper workflow
- Requires API keys in environment
- Tests real integrations

### Running Tests
```bash
# Fast: Unit tests only
pytest tests/unit/ -v

# Full: All tests including integration
pytest -v

# Specific feature
pytest tests/test_copy_trading.py -k "test_leaderboard"
```

## Security Considerations

1. **Private Key Encryption**: User wallet private keys are encrypted with `WALLET_ENCRYPTION_KEY`
2. **Environment Secrets**: Never commit `.env` file (in `.gitignore`)
3. **Production Guards**: Multiple safety mechanisms prevent accidental mainnet trades
4. **SQL Injection**: Parameterized queries via SQLAlchemy ORM
5. **Rate Limiting**: 60 requests/minute per user, 20 trades/hour
6. **Input Validation**: All user inputs validated before processing

## Performance Optimization

- **Parallel RPC Submission**: Submit to 3 RPCs simultaneously
- **Priority Fees**: 2M microlamports for fast inclusion
- **WebSocket Monitoring**: Real-time updates for wallet tracking
- **Database Indexing**: Indexes on frequently queried columns
- **Caching**: Token metadata cached for 5 minutes
- **Connection Pooling**: Reuse Solana RPC connections

## Troubleshooting

### Bot won't start
- Check `logs/trading_bot.jsonl` for errors
- Verify all required environment variables are set
- Ensure database is initialized: `python -c "from src.modules.database import DatabaseManager; import asyncio; asyncio.run(DatabaseManager().init_db())"`

### Telegram webhook conflicts
```bash
python scripts/fix_telegram_conflict.py
```

### Trades not executing
- Check `ALLOW_BROADCAST` is `true`
- Verify `CONFIRM_TOKEN` is set and correct
- Check wallet balance is sufficient
- Review logs for execution errors

### Database locked errors
- Stop bot: `pkill -f run_bot`
- Wait 5 seconds
- Restart bot

### API rate limits
- Twitter: 100 requests per 15 minutes
- Reddit: 60 requests per minute
- Helius: 100K requests per day (free tier)

## Git Workflow

```bash
# Before making changes
git pull

# After making changes
git add .
git commit -m "Descriptive message"
git push

# On server (Ubuntu)
cd ~/code/TGbot
git pull
sudo systemctl restart trading-bot
```

## Additional Resources

- **Full Command List**: See `TELEGRAM_COMMANDS.md`
- **Environment Variables**: See `ENV_ULTIMATE_FINAL.txt`
- **Deployment Guide**: See `UBUNTU_DEPLOYMENT.md`
- **Neural AI Guide**: See `DEPLOY_NEURAL_UI_UPGRADE.md`
- **API Integration**: See `docs/API_INTEGRATION_GUIDE.md`
