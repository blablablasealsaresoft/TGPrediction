# 🎯 QUICK MONITORING REFERENCE - Your Bot

## ✅ **CURRENT STATUS:**

**Bot:** Running (PID 15096)  
**Wallets Tracked:** 17 (3 traders + 14 affiliates)  
**Balance:** 0.2 SOL  
**Settings:** Optimized for testing  

---

## 📊 **3 WAYS TO MONITOR:**

### **1. TELEGRAM (EASIEST)**

Just use your bot in Telegram:

```
/wallet       ← Check balance & stats
/positions    ← See open trades  
/autostatus   ← Automated trading status
/stats        ← Your performance
```

**Best for:** Quick checks on phone

---

### **2. QUICK STATUS CHECK**

Run this command anytime:

```bash
python scripts/bot_status.py
```

**Shows:**
- ✅ API configurations
- ✅ Tracked wallets (all 17)
- ✅ Your balance
- ✅ Bot running status
- ✅ Current settings

**Best for:** Daily check-ins

---

### **3. LIVE MONITORING**

Real-time dashboard (updates every 10 seconds):

```bash
python scripts/monitor_performance.py
```

**Shows:**
- Wallet balance (live)
- Top 5 wallets by score
- Bot process status
- Recent log activity
- Current settings
- Auto-refreshes

**Stop with:** Ctrl+C

**Best for:** Watching bot in action

---

## 🔍 **VIEW LOGS:**

### **Basic Commands:**

```bash
# Last 50 lines
python scripts/view_logs.py

# Last 100 lines
python scripts/view_logs.py -n 100

# Follow in real-time
python scripts/view_logs.py -f
```

### **Filter Logs:**

```bash
# Sniper activity only
python scripts/view_logs.py --sniper

# Trades only
python scripts/view_logs.py --trades

# Errors only
python scripts/view_logs.py --errors

# Custom filter
python scripts/view_logs.py --filter "wallet"
```

---

## 🎯 **WHAT TO LOOK FOR:**

### **✅ Good Signs:**

```
✅ Bot is now listening for commands
✅ Checking Birdeye for new tokens
✅ Scanned 17 top wallets for opportunities
✅ Automated trading STARTED
✅ Position registered for auto-management
```

### **⚠️ Warning Signs:**

```
⚠️ Insufficient balance
⚠️ Daily limit reached
⚠️ Rate limit (shouldn't happen with Helius)
⚠️ Multiple stop losses (market dumping)
```

### **🎊 Trading Activity:**

```
🎯 NEW TOKEN DETECTED: SYMBOL
🛡️ Running elite protection checks
🎯 AI says: strong_buy
✅ ELITE SNIPE EXECUTED
💰 Take profit triggered
✅ Position closed - PnL: +X SOL
```

---

## 📱 **TELEGRAM COMMANDS (FULL LIST):**

### **Wallet & Balance:**
```
/wallet       - Balance & wallet info
/balance      - Quick balance check  
/deposit      - Deposit instructions
/export       - Export private key
```

### **Trading:**
```
/buy <token>  - Buy a token
/sell <token> - Sell a token
/positions    - Open positions
/history      - Trade history
```

### **Automation:**
```
/autostart    - Start copy trading (IMPORTANT!)
/autostop     - Stop automated trading
/autostatus   - Check automation status
/snipe        - Configure auto-sniper
```

### **Analysis:**
```
/ai <token>   - AI analysis
/trending     - Trending tokens
/stats        - Your performance
```

### **Wallet Tracking:**
```
/track <addr> - Track a wallet
/rankings     - Top performing wallets
```

---

## 🎮 **YOUR TESTING WORKFLOW:**

### **Start Trading (First Time):**

1. **Activate automated trading:**
   ```
   /autostart
   ```
   
2. **Enable sniper:**
   ```
   /snipe
   ```
   Click "Enable Auto-Snipe"
   
3. **Verify wallet:**
   ```
   /wallet
   ```

4. **Monitor in terminal:**
   ```bash
   python scripts/monitor_performance.py
   ```

### **Daily Routine:**

**Morning:**
```bash
# Check status
python scripts/bot_status.py

# Telegram
/stats
/positions
```

**During Day:**
```bash
# Watch live (when active)
python scripts/monitor_performance.py

# Or check Telegram
/wallet
/positions
```

**Evening:**
```bash
# Review day
/stats
/history

# Check logs
python scripts/view_logs.py --trades -n 100
```

---

## 📊 **YOUR OPTIMIZED SETTINGS:**

**Safe for 0.2 SOL:**
```
Buy Amount:        0.05 SOL  ← Can do 4 trades
Snipe Amount:      0.05 SOL
Daily Limit:       1.0 SOL
Max Daily Loss:    0.15 SOL  ← 75% protected
Max Trades/Day:    10
Max Snipes/Day:    3

Stop Loss:         -15%
Take Profit:       +50%
Trailing Stop:     10%

Min Liquidity:     $2,000
AI Confidence:     75%
```

---

## 🔔 **WHEN TO CHECK:**

### **Immediately:**
- After running `/autostart`
- After enabling sniper
- If you get a Telegram notification

### **Every Hour:**
- Quick Telegram check: `/wallet`
- Or: `python scripts/bot_status.py`

### **Daily:**
- Review stats: `/stats`
- Check logs: `python scripts/view_logs.py -n 100`

---

## 💡 **PRO TIPS:**

### **Monitoring Like a Pro:**

1. **Keep Telegram open** - Instant notifications
2. **Run live monitor in background:**
   ```bash
   python scripts/monitor_performance.py
   ```
3. **Check errors daily:**
   ```bash
   python scripts/view_logs.py --errors
   ```

### **Performance Tracking:**

- **First week:** Monitor closely, check every 2-4 hours
- **After week 1:** If all good, daily checks OK
- **Always:** Keep Telegram notifications on

---

## 🚀 **READY TO MONITOR!**

**Your monitoring tools:**
- ✅ Telegram commands (easiest)
- ✅ `bot_status.py` (quick check)
- ✅ `monitor_performance.py` (live dashboard)
- ✅ `view_logs.py` (detailed logs)

**Start monitoring now:**
```bash
python scripts/monitor_performance.py
```

**And in Telegram:**
```
/autostart
/wallet
/positions
```

---

## 📝 **SAVE THESE COMMANDS:**

```bash
# Quick check
python scripts/bot_status.py

# Live monitor
python scripts/monitor_performance.py

# View logs
python scripts/view_logs.py -n 50

# Sniper activity
python scripts/view_logs.py --sniper -f

# Telegram
/wallet
/autostatus
/positions
```

**You're all set! Happy trading! 🎊**

