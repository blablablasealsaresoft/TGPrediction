# ⚡ Quick Start Guide

## Get Your Trading Bot Running in 5 Minutes

### Step 1: Install Python
Download Python 3.9+ from [python.org](https://python.org) or use your package manager.

```bash
# Verify Python version
python --version  # Should be 3.9 or higher
```

### Step 2: Setup Project

```bash
# Run the setup script
python scripts/setup_project.py
```

This will:
- Create necessary directories
- Copy `.env.example` to `.env`
- Install dependencies (if you choose yes)

### Step 3: Configure Bot

Edit `.env` file with your credentials:

```env
# Get from @BotFather on Telegram
TELEGRAM_BOT_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11

# Your Solana wallet private key (Base58 encoded)
# Get from: solana-keygen new
WALLET_PRIVATE_KEY=your_private_key_here

# Optional: Your Telegram user ID (get from @userinfobot)
ADMIN_CHAT_ID=123456789
```

**⚠️ IMPORTANT:**
- Never share your private key
- Start with a NEW wallet with small amounts
- Test on devnet first if unsure

### Step 4: Run the Bot

```bash
python scripts/run_bot.py
```

You should see:
```
============================================================
SOLANA REVOLUTIONARY TRADING BOT
============================================================
Loading configuration...
Initializing database...
Starting Revolutionary Trading Bot...
Bot is running! Press Ctrl+C to stop.
```

### Step 5: Test in Telegram

1. Open Telegram and find your bot
2. Send `/start` to begin
3. Try `/help` to see all commands
4. Use `/settings` to configure safety limits

---

## First Trade (Recommended Approach)

### Start Safe:

1. **Enable confirmations** (default):
   ```
   /settings
   → Require Confirmation: ON
   ```

2. **Set safety limits**:
   ```
   → Max Trade Size: 0.1 SOL
   → Daily Loss Limit: 1.0 SOL
   ```

3. **Analyze a token first**:
   ```
   /ai_analyze <token_address>
   ```

4. **Make small test buy**:
   ```
   /buy <token_address> 0.05
   ```

5. **Check your position**:
   ```
   /positions
   ```

6. **Sell when ready**:
   ```
   /sell <token_address> all
   ```

---

## Common Issues & Solutions

### "TELEGRAM_BOT_TOKEN is required"
**Solution:** Edit `.env` and add your bot token from @BotFather

### "Module not found"
**Solution:** Install dependencies:
```bash
pip install -r requirements.txt
```

### "Database error"
**Solution:** Initialize database:
```bash
python -c "import asyncio; from src.modules.database import DatabaseManager; asyncio.run(DatabaseManager().init_db())"
```

### Bot not responding
**Solution:** Check logs in `logs/trading_bot.log`

---

## Next Steps

### Learn the Features
1. Read the [README.md](README.md) for all features
2. Check [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) for production setup
3. Explore AI features: `/ai_analyze`, `/trending`
4. Try social trading: `/leaderboard`, `/copy_trader`

### Safety Tips
- ✅ Start with <$50
- ✅ Test on devnet first
- ✅ Enable all safety checks
- ✅ Monitor daily P&L
- ✅ Never share private keys
- ✅ Use stop losses

### Advanced Features
- **AI Analysis:** `/ai_analyze <token>` - ML-powered predictions
- **Copy Trading:** `/leaderboard` → `/copy_trader <id>`
- **Sentiment:** `/trending` - Viral tokens right now
- **Community:** `/community <token>` - Crowdsourced intel

---

## Docker Quick Start (Alternative)

If you prefer Docker:

```bash
# 1. Copy config
cp config/.env.example .env

# 2. Edit .env with your credentials
nano .env

# 3. Start with Docker
docker-compose up -d

# 4. Check logs
docker-compose logs -f trading-bot
```

---

## Getting Help

1. **Documentation:** Read [README.md](README.md) and [docs/](docs/)
2. **Logs:** Check `logs/trading_bot.log`
3. **Issues:** Open GitHub issue with error details
4. **Community:** Join discussions on GitHub

---

## Success Checklist

Before trading real money:

- [ ] Bot starts without errors
- [ ] Tested `/start` command works
- [ ] Configured safety limits
- [ ] Tried test commands (`/help`, `/settings`)
- [ ] Understand all risks
- [ ] Read README.md completely
- [ ] Set up monitoring/alerts
- [ ] Have backup plan

---

**You're Ready!** 🚀

Remember:
- Start small
- Test thoroughly
- Never risk more than you can afford to lose
- This is NOT financial advice

Happy trading! 💎

