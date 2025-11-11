# ⚡ QUICK START - Get Bot Running in 5 Minutes

## 🎯 Bot Not Responding? Fix It Now!

---

## ✅ STEP 1: Check .env File (1 minute)

```powershell
cd C:\Users\ckthe\sol\TGbot
notepad .env
```

**Verify these lines exist:**
```env
TELEGRAM_BOT_TOKEN=8490397863:AAGg9W6CJTdvfLCSA8Cm7J4NCSzcey1FnRc
ADMIN_CHAT_ID=8059844643
SOLANA_RPC_URL=https://mainnet.helius-rpc.com/?api-key=4177e73c-0edb-4e4a-9d22-4c99b9a3f8c1
WALLET_PRIVATE_KEY=2KBD49gknMGpsVSJWuUFbTPLsVLd4kMEN8n8cBERvJFML8sBzavGqpHH14mYUwDWYHZ6EdTx1DzHxto6PUsUVpke
```

If missing, copy from `ENV_PRODUCTION_READY.txt`

---

## ✅ STEP 2: Kill Any Running Bot (30 seconds)

```powershell
# Kill any Python processes
Get-Process python* | Stop-Process -Force

# Wait
Start-Sleep -Seconds 3
```

---

## ✅ STEP 3: Start Bot Fresh (1 minute)

```powershell
cd C:\Users\ckthe\sol\TGbot

# Activate venv
.\.venv\Scripts\Activate.ps1

# Start bot
python scripts\run_bot.py --network mainnet
```

**Should see:**
```
{"event": "SOLANA REVOLUTIONARY TRADING BOT"}
{"event": "🔍 Active Scanner: Twitter=✅ Reddit=✅"}
{"event": "🧠 Unified Neural Engine initialized"}
{"event": "Bot is now listening for commands..."}
{"event": "HTTP Request: ... 200 OK"}
```

**If you see "200 OK" → Bot is working!** ✅

---

## ✅ STEP 4: Test on Telegram (1 minute)

**Open Telegram → Message @gonehuntingbot:**

```
/start
```

**Should get:**
- Instant response (<1 sec)
- Enterprise UI welcome
- Your wallet address
- Beautiful buttons

**If no response:**
- Check bot terminal for errors
- Verify TELEGRAM_BOT_TOKEN correct
- Try: `curl https://api.telegram.org/bot8490397863:AAGg9W6CJTdvfLCSA8Cm7J4NCSzcey1FnRc/getMe`

---

## ✅ STEP 5: Keep It Running (1 minute)

**Option A: Keep PowerShell Open**
- Just minimize the window
- Bot runs as long as PowerShell is open

**Option B: Run as Background Service (Windows)**
```powershell
# Install NSSM (Non-Sucking Service Manager)
# Download from: nssm.cc

# Install as service
nssm install TradingBot "C:\Users\ckthe\sol\TGbot\.venv\Scripts\python.exe" "C:\Users\ckthe\sol\TGbot\scripts\run_bot.py" "--network" "mainnet"

# Start service
nssm start TradingBot

# Now runs 24/7, auto-restarts on reboot
```

---

## 🔥 TROUBLESHOOTING

### **Error: "ModuleNotFoundError"**
```powershell
pip install -r requirements.txt
```

### **Error: "TELEGRAM_BOT_TOKEN not found"**
```powershell
# Check .env exists:
Test-Path .env

# If not, create it:
Copy-Item ENV_PRODUCTION_READY.txt .env
notepad .env
# Add your tokens
```

### **Error: "Database locked"**
```powershell
# Remove lock
Remove-Item trading_bot.db-shm -ErrorAction SilentlyContinue
Remove-Item trading_bot.db-wal -ErrorAction SilentlyContinue
```

### **Bot starts but Telegram doesn't respond:**
```powershell
# Delete webhook
curl "https://api.telegram.org/bot8490397863:AAGg9W6CJTdvfLCSA8Cm7J4NCSzcey1FnRc/deleteWebhook?drop_pending_updates=true"

# Wait 30 seconds
Start-Sleep -Seconds 30

# Restart bot
```

---

## 🌐 WEBSITE PLAN (Saturday)

### **Quick Website (3-4 Hours):**

**I'll generate:**
1. Complete Next.js website
2. All pages designed
3. Responsive & beautiful
4. Ready to deploy

**You:**
1. Copy files
2. Deploy to Vercel (10 minutes)
3. Live at: yourbot.vercel.app

**Features:**
- Dark theme (crypto-style)
- Animated hero
- Feature showcase
- Pricing tiers
- CTA to bot
- Mobile responsive
- SEO optimized

**Want me to build it? Just say "yes" and I'll generate the complete website!**

---

## 🎯 WEEKEND SUCCESS CHECKLIST

**Friday/Saturday:**
- [ ] Bot running on Windows
- [ ] All commands tested
- [ ] No errors
- [ ] Telegram responsive

**Saturday/Sunday:**
- [ ] Website designed
- [ ] Website deployed
- [ ] Domain connected (optional)
- [ ] Social accounts created

**Sunday Night:**
- [ ] Bot operational ✅
- [ ] Website live ✅
- [ ] 10 beta users invited ✅
- [ ] First testimonials ✅
- [ ] Ready for launch Monday ✅

---

## 🚀 IMMEDIATE ACTION

**RUN THIS NOW:**

```powershell
cd C:\Users\ckthe\sol\TGbot
.\.venv\Scripts\Activate.ps1
python scripts\run_bot.py --network mainnet
```

**Then test:** Message @gonehuntingbot with `/start`

**Once working, I'll build your website!** 🌐💎

---

**Let's make it happen! 🔥**

