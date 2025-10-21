# 🚀 Solana Trading Bot - Advanced Telegram Bot for Solana Trading

A sophisticated Telegram bot for automated Solana trading with wallet tracking, token analysis, and anti-scam protection.

## ⚠️ CRITICAL WARNINGS

**READ THIS BEFORE PROCEEDING:**

1. **YOU CAN LOSE ALL YOUR MONEY** - Automated trading is extremely risky
2. **START WITH SMALL AMOUNTS** - Test with $10-50 maximum initially
3. **TEST ON DEVNET FIRST** - Always test new features on Solana devnet
4. **NO GUARANTEES** - This bot does not guarantee profits
5. **SECURITY IS YOUR RESPONSIBILITY** - Protect your private keys
6. **NOT FINANCIAL ADVICE** - Use at your own risk
7. **REGULATORY COMPLIANCE** - Check your local laws regarding automated trading

### This Bot is NOT Production-Ready

This is an educational framework. Before using real funds:
- Conduct extensive testing
- Perform security audits
- Add proper error handling
- Implement comprehensive logging
- Set up monitoring and alerts
- Review and understand all code

## ✨ Features

### Core Trading
- **Buy/Sell Execution** - Trade tokens via Jupiter aggregator (best prices)
- **Auto Trading** - Optional automated trading mode
- **Slippage Protection** - Configurable slippage tolerance
- **Position Tracking** - Monitor open positions and PnL

### Advanced Features
- **Token Sniping** - Snipe tokens at launch (buy when liquidity added)
- **Anti-MEV Protection** - Use Jito bundles to prevent frontrunning
- **Wallet Tracking** - Track and rank profitable wallets
- **Token Analysis** - Comprehensive safety checks for tokens
- **Honeypot Detection** - Detect and avoid honeypot scams
- **Liquidity Checks** - Verify sufficient liquidity before trading

### Safety Features
- **Trade Size Limits** - Maximum per-trade limits
- **Daily Loss Limits** - Stop trading after losses exceed threshold
- **Confirmation Required** - Optional confirmation for all trades
- **Safety Scoring** - Token safety score (0-100)
- **Scam Detection** - Check mint/freeze authority, liquidity, patterns

### Analytics
- **Trade History** - Complete trading history with PnL
- **Performance Stats** - Win rate, total PnL, trade count
- **Wallet Leaderboard** - Top performing tracked wallets
- **Real-time Monitoring** - Live trade execution updates

## 📋 Prerequisites

- Python 3.10 or higher
- Solana wallet with SOL for trading
- Telegram account
- Premium Solana RPC (Helius, QuickNode, or Alchemy recommended)

## 🛠️ Installation

### 1. Clone or Download the Repository

```bash
# If you have git
git clone <repository-url>
cd solana-trading-bot

# Or download and extract the files
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up Telegram Bot

1. Message @BotFather on Telegram
2. Send `/newbot`
3. Follow instructions to create your bot
4. Copy the bot token (looks like: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

### 5. Set Up Solana Wallet

**⚠️ IMPORTANT: Create a NEW wallet specifically for this bot!**

```python
# Generate new wallet (run this in Python):
from solders.keypair import Keypair
import base58

# Generate new keypair
keypair = Keypair()
private_key = base58.b58encode(bytes(keypair)).decode('utf-8')
public_key = str(keypair.pubkey())

print(f"Public Key: {public_key}")
print(f"Private Key: {private_key}")  # KEEP THIS SECRET!
```

**Security Best Practices:**
- Never use your main wallet
- Only fund with amounts you can afford to lose
- Start with 0.1-0.5 SOL for testing
- Store private key securely (consider hardware wallet)

### 6. Get Premium RPC (Highly Recommended)

Free RPCs are rate-limited and slow. Get a premium RPC:

**Helius (Recommended):**
1. Go to https://helius.dev
2. Sign up for free tier
3. Create API key
4. Use: `https://rpc.helius.xyz/?api-key=YOUR_KEY`

**QuickNode:**
1. Go to https://quicknode.com
2. Create Solana endpoint
3. Copy your RPC URL

**Alchemy:**
1. Go to https://alchemy.com
2. Create Solana app
3. Copy your RPC URL

### 7. Configure Environment

```bash
# Copy template
cp .env.template .env

# Edit .env file with your values
nano .env  # or use your preferred editor
```

Fill in:
- `TELEGRAM_BOT_TOKEN` - From @BotFather
- `SOLANA_RPC_URL` - Your premium RPC URL
- `WALLET_PRIVATE_KEY` - Your bot wallet private key (Base58)

### 8. Initialize Database

```bash
python3 -c "import asyncio; from database import DatabaseManager; asyncio.run(DatabaseManager().init_db())"
```

## 🚀 Running the Bot

### Test on Devnet First (HIGHLY RECOMMENDED)

```bash
# In .env, set:
USE_DEVNET=true
DEVNET_RPC_URL=https://api.devnet.solana.com

# Get devnet SOL (free):
# solana airdrop 1 YOUR_WALLET_ADDRESS --url devnet

# Run bot
python3 solana_trading_bot.py
```

### Run on Mainnet

```bash
# Make sure USE_DEVNET=false in .env
python3 solana_trading_bot.py
```

### Run in Background (Production)

```bash
# Using nohup
nohup python3 solana_trading_bot.py > bot.log 2>&1 &

# Or using screen
screen -S trading-bot
python3 solana_trading_bot.py
# Press Ctrl+A, then D to detach
# Reconnect with: screen -r trading-bot

# Or using systemd (create service file)
```

## 📱 Using the Bot

### Basic Commands

```
/start - Initialize bot
/balance - Check wallet balance
/buy <token> <amount> - Buy tokens
/sell <token> <amount> - Sell tokens
/analyze <token> - Analyze token safety
/settings - Configure bot settings
/help - Show all commands
```

### Advanced Commands

```
/snipe <token> <amount> - Snipe token launch
/track <wallet> [label] - Track wallet performance
/leaderboard - Show top wallets
/positions - View open positions
/stats - View trading statistics
/stop - Emergency stop all trading
```

### Example Usage

```
# Check balance
/balance

# Analyze a token first
/analyze So11111111111111111111111111111111111111112

# Buy 0.1 SOL worth of token
/buy TokenMintAddress 0.1

# Track a successful wallet
/track WalletAddress "Smart Trader"

# View top wallets
/leaderboard

# Enable auto-trading (⚠️ RISKY!)
/settings -> Auto Trading -> Enable
```

## ⚙️ Configuration

### Safety Limits

Edit in `.env`:

```bash
MAX_TRADE_SIZE_SOL=1.0          # Max per trade
DAILY_LOSS_LIMIT_SOL=5.0        # Stop trading if losses exceed
REQUIRE_CONFIRMATION=true        # Ask before each trade
```

### Trading Parameters

```bash
MAX_SLIPPAGE=0.05               # 5% slippage tolerance
DEFAULT_BUY_AMOUNT_SOL=0.1      # Default buy amount
MIN_PROFIT_PERCENTAGE=2.0        # Min profit for auto-sell
```

### Anti-Scam Settings

```bash
CHECK_HONEYPOTS=true            # Detect honeypots
MIN_LIQUIDITY_USD=10000         # Min liquidity required
CHECK_MINT_AUTHORITY=true       # Check mint authority
CHECK_FREEZE_AUTHORITY=true     # Check freeze authority
```

## 🔒 Security Best Practices

### Do:
✅ Use a dedicated wallet for the bot
✅ Start with small amounts (0.1-0.5 SOL)
✅ Test thoroughly on devnet first
✅ Keep private keys secure
✅ Use premium RPC for reliability
✅ Set conservative safety limits
✅ Monitor bot activity regularly
✅ Keep software updated
✅ Review transactions before confirming

### Don't:
❌ Use your main wallet
❌ Share private keys or .env file
❌ Commit .env to version control
❌ Enable auto-trading without testing
❌ Trade with more than you can lose
❌ Ignore warning messages
❌ Skip token safety checks
❌ Run on untrusted servers

## 🐛 Troubleshooting

### Bot Won't Start

```bash
# Check Python version
python3 --version  # Should be 3.10+

# Reinstall dependencies
pip install --upgrade -r requirements.txt

# Check .env file
cat .env  # Verify all values are set
```

### RPC Errors

```bash
# Test RPC connection
curl -X POST -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"getHealth"}' \
  YOUR_RPC_URL

# If using free RPC, you're likely rate-limited
# Solution: Get premium RPC
```

### Transaction Failures

Common causes:
- Insufficient SOL for gas fees
- Token has trading restrictions (honeypot)
- Slippage too low for volatile tokens
- RPC latency issues

Solutions:
- Ensure wallet has SOL for fees (0.01+ SOL)
- Run `/analyze <token>` before buying
- Increase slippage for volatile tokens
- Use premium RPC with low latency

### Database Errors

```bash
# Reset database
rm trading_bot.db
python3 -c "import asyncio; from database import DatabaseManager; asyncio.run(DatabaseManager().init_db())"
```

## 📊 Understanding Token Analysis

The bot scores tokens 0-100 based on:

- **90-100**: Very safe (likely established token)
- **70-89**: Generally safe (standard checks passed)
- **50-69**: Moderate risk (some warnings)
- **0-49**: High risk (multiple red flags)

Warning flags:
- Low liquidity
- Mint authority not revoked
- Freeze authority not revoked
- Suspicious trading patterns
- Known honeypot

## 🎯 Advanced Features

### Wallet Tracking

Track profitable wallets and learn from their strategies:

```
/track WalletAddress "Label"
```

The bot will:
- Analyze their trading history
- Calculate win rate and PnL
- Give them a score (0-100)
- Monitor their future trades (optional)

### Token Sniping

Buy tokens immediately when liquidity is added:

```
/snipe TokenMintAddress 0.1
```

**Note**: Sniping is competitive and risky!

### Anti-MEV Protection

The bot uses Jito bundles to prevent:
- Frontrunning
- Sandwich attacks
- MEV extraction

This is automatic for all trades.

## 📈 Maximizing Profitability

### Strategies

1. **Follow the Smart Money**
   - Track top wallets
   - Analyze their patterns
   - Copy successful strategies

2. **Early Entry**
   - Use sniping for new launches
   - Set alerts for new pools
   - Be quick but cautious

3. **Risk Management**
   - Never risk more than 1-2% per trade
   - Set stop losses
   - Take profits regularly
   - Use position sizing

4. **Token Research**
   - Always run `/analyze` first
   - Check token socials
   - Verify team and project
   - Look for red flags

### Common Mistakes to Avoid

❌ FOMO (Fear of missing out)
❌ Ignoring safety checks
❌ Over-trading
❌ Not taking profits
❌ Revenge trading after losses
❌ Trading without stop losses

## 🔧 Customization

### Adding New Features

The bot is modular. Key files:

- `solana_trading_bot.py` - Main bot logic
- `jupiter_client.py` - DEX integration
- `database.py` - Data persistence
- `trading_engine.py` - Trade execution (in main file)

### Creating Custom Strategies

Example: Add a momentum trading strategy

```python
# Add to solana_trading_bot.py

async def momentum_strategy(self, token_mint: str):
    """Buy tokens showing strong momentum"""
    # Get price history
    prices = await self.get_token_price_history(token_mint)
    
    # Calculate momentum
    if self.is_strong_momentum(prices):
        # Execute buy
        await self.trading_engine.execute_buy(token_mint, 0.1)
```

## 📝 Maintenance

### Regular Tasks

Daily:
- Check bot status
- Review trade performance
- Monitor for errors

Weekly:
- Update tracked wallets
- Adjust safety limits
- Review profitable strategies

Monthly:
- Update dependencies
- Clean old database records
- Review and optimize strategies

### Updating the Bot

```bash
# Pull latest changes
git pull

# Update dependencies
pip install --upgrade -r requirements.txt

# Restart bot
# ... (stop current process)
python3 solana_trading_bot.py
```

## 🤝 Contributing

This is an educational framework. Improvements welcome!

Areas needing work:
- Enhanced token analysis
- More DEX integrations
- Better MEV protection
- Machine learning for predictions
- Multi-wallet support
- Advanced risk management

## ⚖️ Legal Disclaimer

This software is provided "as is" without warranty of any kind. The developers are not responsible for:
- Financial losses
- Bugs or errors
- Security vulnerabilities
- Regulatory compliance

**By using this bot, you acknowledge:**
- You understand the risks
- You are using it at your own risk
- You are responsible for compliance with laws
- No guarantees of profit are made

Cryptocurrency trading carries significant risk. Only trade with money you can afford to lose.

## 📞 Support

For issues or questions:
1. Check this README
2. Review error logs
3. Search existing issues
4. Test on devnet first

**Remember**: Test with small amounts, never share private keys, and always do your own research!

## 🙏 Acknowledgments

Built with:
- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)
- [Solana Python SDK](https://github.com/michaelhly/solana-py)
- [Jupiter Aggregator](https://jup.ag/)
- [Jito Labs](https://www.jito.wtf/)

---

**Final Warning**: This bot can lose money. Start small, test thoroughly, and never risk more than you can afford to lose. Good luck! 🚀
