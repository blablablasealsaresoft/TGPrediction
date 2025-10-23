# 📊 BOT MONITORING & LOGS GUIDE

## 🎯 Quick Start - Check Everything

```bash
# Quick status check
python scripts/bot_status.py

# Live performance monitor (updates every 10 seconds)
python scripts/monitor_performance.py

# View recent logs (last 50 lines)
python scripts/view_logs.py
```

---

## 📜 LOG VIEWING COMMANDS

### Basic Log Viewing:

```bash
# Last 50 lines (default)
python scripts/view_logs.py

# Last 100 lines
python scripts/view_logs.py -n 100

# Follow logs in real-time (like tail -f)
python scripts/view_logs.py -f

# Filter for specific text
python scripts/view_logs.py --filter "sniper"
python scripts/view_logs.py --filter "trade"
python scripts/view_logs.py --filter "wallet"
```

### Preset Filters:

```bash
# Show only sniper activity
python scripts/view_logs.py --sniper

# Show only trade activity
python scripts/view_logs.py --trades

# Show only errors
python scripts/view_logs.py --errors

# Follow sniper activity in real-time
python scripts/view_logs.py --sniper -f
```

### Advanced:

```bash
# Last 200 lines, filter for "NEW TOKEN"
python scripts/view_logs.py -n 200 --filter "NEW TOKEN"

# Follow logs and show only wallet scans
python scripts/view_logs.py -f --filter "Scanned"

# Show errors from last 500 lines
python scripts/view_logs.py -n 500 --errors
```

---

## 🎯 MONITORING DASHBOARD

### Live Performance Monitor:

```bash
# Start live dashboard (updates every 10 seconds)
python scripts/monitor_performance.py
```

**Shows:**
- Wallet balance (real-time)
- Tracked wallets count
- Bot process status
- Recent activity
- Current settings
- Updates every 10 seconds

**Stop with:** Ctrl+C

---

## 📊 KEY THINGS TO MONITOR

### 1. **Sniper Activity**

Look for these log messages:
```
🚀 Checking Birdeye for new tokens...
📊 Found X tokens from Birdeye
🎯 NEW TOKEN DETECTED: SYMBOL - Liquidity: $X
🛡️ Running elite protection checks...
🎯 AI says: strong_buy with X% confidence
✅ ELITE SNIPE EXECUTED!
📊 Position registered for auto-management
```

### 2. **Copy Trading Activity**

Look for:
```
📊 Loading 17 tracked wallets from database...
🔍 Scanned 17 top wallets for opportunities
🎯 Executing automated trade: buy X SOL
✅ Position opened
```

### 3. **Auto-Sell Triggers**

Look for:
```
🛑 Stop loss triggered at -15%
💰 Take profit triggered at +50%
📉 Trailing stop triggered
✅ Position closed successfully
   PnL: +X SOL
```

### 4. **Errors to Watch**

```bash
# Check for errors
python scripts/view_logs.py --errors

# Common issues:
- "Rate limit" - Helius should prevent this
- "Insufficient balance" - Need more SOL
- "401 Unauthorized" - Twitter API (not critical)
```

---

## 📈 PERFORMANCE METRICS

### Check Trading Stats:

**In Telegram:**
```
/stats        - Your trading performance
/positions    - Open positions
/autostatus   - Automated trading status
/wallet       - Wallet balance & history
```

### Check Database:

```bash
# View all tracked wallets
python -c "import asyncio; from src.modules.database import DatabaseManager; async def show(): db = DatabaseManager('sqlite+aiosqlite:///trading_bot.db'); wallets = await db.get_tracked_wallets(8059844643); print(f'Tracked: {len(wallets)}'); [print(f'{w.wallet_address[:8]}... - {w.label}') for w in wallets]; asyncio.run(show())"
```

---

## 🔍 WHAT TO LOOK FOR

### **Successful Snipe:**
```
2025-10-22 12:34:56 - 🎯 NEW TOKEN DETECTED: PEPE2 (AbCd123...) - Liquidity: $3,500
2025-10-22 12:34:57 - 🛡️ Running elite protection checks for PEPE2...
2025-10-22 12:34:58 - 🎯 AI says: strong_buy with 78% confidence
2025-10-22 12:34:59 - 🎯 EXECUTING ELITE SNIPE: PEPE2
2025-10-22 12:35:01 - ✅ ELITE SNIPE EXECUTED!
2025-10-22 12:35:01 -    Amount: 0.05 SOL
2025-10-22 12:35:01 - 📊 Position registered for auto-management
```

### **Successful Copy Trade:**
```
2025-10-22 13:15:20 - 📊 Loading 17 tracked wallets...
2025-10-22 13:15:30 - 🔍 Scanned 17 top wallets for opportunities
2025-10-22 13:15:31 - 🎯 Wallet 3S8TjEDc... bought token XYZ
2025-10-22 13:15:32 - 🤖 AI confidence: 82% - Executing copy trade
2025-10-22 13:15:34 - ✅ Copied trade: 0.05 SOL
```

### **Auto-Sell Success:**
```
2025-10-22 14:20:10 - 🔄 Monitoring position: PEPE2
2025-10-22 14:20:11 - 💰 Take profit triggered at +52%
2025-10-22 14:20:12 - 💰 Selling tokens...
2025-10-22 14:20:14 - ✅ Position closed successfully!
2025-10-22 14:20:14 -    PnL: +0.026 SOL (+52%)
```

---

## 🚨 WARNING SIGNS

### **Check logs immediately if you see:**

1. **"Insufficient balance"** - Need to fund wallet
2. **"Daily limit reached"** - Max trades hit (safe feature)
3. **"Stop loss triggered"** multiple times - Market dumping
4. **"429 Too Many Requests"** - Should NOT happen with Helius
5. **"Failed to close position"** - Manual intervention needed

---

## 🛠️ TROUBLESHOOTING COMMANDS

### Bot Not Running:
```bash
# Check if running
tasklist /FI "IMAGENAME eq python.exe"

# Start bot
cd C:\Users\ckthe\sol
python scripts/run_bot.py
```

### Check Specific Activity:
```bash
# Sniper activity
python scripts/view_logs.py --sniper -n 100

# Trade executions
python scripts/view_logs.py --trades -n 100

# Wallet scanning
python scripts/view_logs.py --filter "Scanned" -n 50

# Token detections
python scripts/view_logs.py --filter "NEW TOKEN" -n 50

# Protection checks
python scripts/view_logs.py --filter "protection" -n 50
```

### Real-Time Monitoring:
```bash
# Follow all activity
python scripts/view_logs.py -f

# Follow only sniper
python scripts/view_logs.py --sniper -f

# Follow only trades
python scripts/view_logs.py --trades -f

# Follow errors
python scripts/view_logs.py --errors -f
```

---

## 📊 MONITORING CHECKLIST

### **Every Hour:**
- [ ] Check wallet balance: `/wallet` in Telegram
- [ ] Check for new positions: `/positions`
- [ ] Verify bot is running: `python scripts/bot_status.py`

### **Every 4 Hours:**
- [ ] Review logs for errors: `python scripts/view_logs.py --errors`
- [ ] Check trading stats: `/stats` in Telegram
- [ ] Verify wallets being scanned: Check logs for "Scanned X wallets"

### **Daily:**
- [ ] Review all trades: `/stats`
- [ ] Check P&L: `/wallet`
- [ ] Review sniper activity: `python scripts/view_logs.py --sniper -n 200`
- [ ] Check auto-sell triggers: `python scripts/view_logs.py --filter "Position closed"`

---

## 📁 LOG FILES LOCATION

```
C:\Users\ckthe\sol\logs\trading_bot.log
```

**Viewing Options:**
1. **Script:** `python scripts/view_logs.py`
2. **Text Editor:** Open `logs/trading_bot.log`
3. **PowerShell:** `Get-Content logs/trading_bot.log -Tail 50`
4. **Real-time:** `python scripts/view_logs.py -f`

---

## 🎮 TELEGRAM MONITORING COMMANDS

### **Real-Time Status:**
```
/wallet       - Balance & stats
/positions    - Open positions
/autostatus   - Automated trading status
/stats        - Your performance
```

### **Activity Checks:**
```
/history      - Trade history
/rankings     - Wallet rankings
/trending     - Trending tokens
```

---

## 📈 WHAT GOOD PERFORMANCE LOOKS LIKE

### **Healthy Bot Logs:**
```
✅ Bot listening for commands
✅ Scanned 17 top wallets for opportunities
✅ Checking Birdeye for new tokens
✅ Checking DexScreener for new tokens
✅ No errors
```

### **Active Trading:**
```
✅ NEW TOKEN DETECTED (several per hour during active times)
✅ Elite snipe executed (occasionally)
✅ Copied trade (when wallets trade)
✅ Position closed with profit
```

### **Protection Working:**
```
⛔ Token failed elite safety checks
✓ Honeypot detected - avoided
✓ Low liquidity - skipped
✓ AI confidence too low - passed
```

---

## 🔔 ALERTS TO SET UP

### **When to Manually Check:**

1. **Balance drops below 0.1 SOL** - Fund wallet
2. **Multiple stop losses** - Market dumping, pause trading
3. **No activity for 24 hours** - Check bot status
4. **Error messages** - Review logs

---

## 💡 PRO TIPS

### **Best Times to Monitor:**
- **12 PM - 10 PM EST** (Most Solana activity)
- **After enabling `/autostart`** (First hour)
- **After new token launches** (Check if sniper caught it)

### **Performance Indicators:**
- **Scanned X wallets** - Should show 17
- **NEW TOKEN DETECTED** - Good, sniper working
- **Position opened** - Trading is active
- **Position closed** - Auto-sell working
- **PnL: +X SOL** - Making profit!

---

## 🚀 QUICK REFERENCE

```bash
# Status check
python scripts/bot_status.py

# Live monitor
python scripts/monitor_performance.py

# View logs
python scripts/view_logs.py

# Follow sniper
python scripts/view_logs.py --sniper -f

# Check errors
python scripts/view_logs.py --errors

# Telegram
/wallet
/positions
/stats
/autostatus
```

---

## ✅ YOUR BOT IS READY!

**All monitoring tools configured!**

Just run:
```
python scripts/monitor_performance.py
```

To see live updates every 10 seconds! 🎯

