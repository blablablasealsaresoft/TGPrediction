# ⚡ QUICK START GUIDE

Too excited to read the full README? Here's the fastest path to get trading (but please be careful!):

## ⚠️ CRITICAL 3-SECOND WARNING
**YOU CAN LOSE ALL YOUR MONEY. START WITH $10 MAXIMUM. TEST ON DEVNET FIRST.**

## 🚀 5-Minute Setup

### 1. Install (2 minutes)
```bash
# Make setup script executable and run it
chmod +x setup.sh
./setup.sh
```

### 2. Configure (2 minutes)

Edit `.env` file:
```bash
nano .env
```

You need 3 things:

1. **Telegram Bot Token**
   - Message @BotFather on Telegram
   - Send `/newbot`
   - Copy the token

2. **Solana RPC**
   - Sign up at https://helius.dev (free tier)
   - Get your API key
   - Use: `https://rpc.helius.xyz/?api-key=YOUR_KEY`

3. **Wallet Private Key**
   ```python
   # Run this to create a new wallet:
   python3 -c "from solders.keypair import Keypair; import base58; k = Keypair(); print('Public:', k.pubkey()); print('Private:', base58.b58encode(bytes(k)).decode())"
   ```
   - Copy the private key to `.env`
   - Send 0.1 SOL to the public address

### 3. Run (1 minute)
```bash
source venv/bin/activate
python3 solana_trading_bot.py
```

## 📱 First Trade

1. Open Telegram, find your bot
2. Send `/start`
3. Send `/balance` - verify your SOL balance
4. Analyze a token:
   ```
   /analyze So11111111111111111111111111111111111111112
   ```
5. Buy small amount:
   ```
   /buy TokenAddress 0.01
   ```

## 🎯 Essential Commands

```
/balance     - Check balance
/analyze     - Check if token is safe
/buy         - Buy tokens (SMALL AMOUNTS!)
/sell        - Sell tokens
/positions   - View open positions
/stats       - See your performance
/settings    - Configure safety limits
```

## 🛡️ Safety Settings

Before trading seriously, configure:

```
/settings
```

Set:
- Max trade size: 0.1 SOL
- Daily loss limit: 0.5 SOL
- Require confirmation: ON
- Check honeypots: ON

## 🎓 Pro Tips

1. **Always analyze first**
   ```
   /analyze <token>
   ```
   Only buy if score > 70

2. **Start TINY**
   - First 10 trades: 0.01 SOL max
   - Test everything before going bigger

3. **Track good wallets**
   ```
   /track <wallet_address> "Label"
   ```
   Learn from successful traders

4. **Use stop losses**
   - In `/settings`, enable default stop losses
   - Set to 10% initially

5. **Take profits**
   - Don't get greedy
   - Sell 50% when you're up 20%

## 🚨 Common Mistakes

❌ Buying without analyzing (`/analyze` first!)
❌ Trading with too much (start with 0.01 SOL)
❌ Ignoring safety warnings
❌ Not setting stop losses
❌ Chasing pumps (FOMO kills profits)

## 🔥 Advanced Features (When Ready)

### Wallet Tracking
```
/track WalletAddress "Smart Trader"
/leaderboard
```

### Token Sniping (RISKY!)
```
/snipe TokenAddress 0.05
```

### Auto Trading (VERY RISKY!)
```
/settings -> Enable Auto Trading
```

## 📊 Reading Signals

Token Safety Score:
- 90-100: Very safe ✅
- 70-89: Generally safe ✅
- 50-69: Risky ⚠️
- 0-49: Very risky ❌

## 🆘 Help!

### Bot won't start?
```bash
# Check Python version
python3 --version  # Need 3.10+

# Reinstall
pip install -r requirements.txt
```

### Can't connect to Solana?
- Get better RPC: https://helius.dev
- Check wallet has SOL

### Transactions failing?
- Ensure 0.01+ SOL for gas
- Run `/analyze` on token first
- Increase slippage if very volatile

## 📈 Profit Strategy

1. **Day 1-7**: Learn
   - Trade 0.01 SOL per trade
   - Track 10 wallets
   - Analyze everything

2. **Day 8-30**: Build
   - Increase to 0.05 SOL per trade
   - Find patterns
   - Refine strategy

3. **Month 2+**: Scale
   - Only if profitable in month 1
   - Gradually increase position sizes
   - Stay disciplined

## ⚖️ Reality Check

Most traders lose money. To win:
- Be patient
- Stay disciplined
- Take profits
- Use stop losses
- Never risk more than 1-2% per trade
- Learn from losses

## 🔗 Resources

- Full README: `README.md`
- Telegram Support: @YourSupportChannel
- Solana Docs: https://docs.solana.com
- Jupiter (DEX): https://jup.ag

## 💬 Final Words

"The market is a device for transferring money from the impatient to the patient." - Warren Buffett

Start small. Learn fast. Scale slowly.

Good luck! 🚀

---

**Still reading?** Good. You might actually make money. Most people skip straight to trading and lose everything. Read the full README.md for complete instructions.
