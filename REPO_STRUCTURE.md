# 📁 APOLLO TGPrediction - Clean Repository Structure

**GitHub:** https://github.com/blablablasealsaresoft/TGPrediction  
**Status:** ✅ CLEAN & ORGANIZED

---

## 🗂️ Folder Structure

```
TGPrediction/
├── 📂 public/                    # Web frontend (MAIN PAGES)
│   ├── dashboard.html            # Main trading dashboard
│   ├── prediction-market.html    # Tournaments & markets
│   ├── user-profile.html         # Epic user profile page ⭐
│   ├── user-dashboard-example.html # Dashboard with commands
│   ├── waitlist.html             # Waitlist signup
│   ├── index.html                # Landing page
│   ├── docs.html                 # API documentation
│   └── static/
│       ├── css/apollo-enhanced-style.css
│       └── js/apollo-enhanced-effects.js
│
├── 📂 src/                       # Backend Python code
│   ├── bot/main.py               # Telegram bot
│   ├── modules/
│   │   ├── database.py           # Database models & manager
│   │   ├── web_api.py            # Web API server ⭐
│   │   ├── wallet_manager.py     # User wallet management
│   │   ├── trade_execution.py    # Trade executor
│   │   ├── ai_prediction.py      # AI engine
│   │   ├── token_sniper.py       # Auto-sniper
│   │   ├── social_trading.py     # Copy trading
│   │   └── ... (30+ modules)
│   ├── ops/probes.py             # Health checks
│   └── config.py                 # Configuration
│
├── 📂 scripts/                   # Utility scripts
│   ├── run_bot.py                # Main bot runner ⭐
│   ├── monitor_performance.py    # Performance monitoring
│   ├── bot_status.py             # Status checker
│   └── ... (60+ scripts)
│
├── 📂 docs/                      # Documentation
│   ├── API_QUICK_REFERENCE.md    # API endpoints ⭐
│   ├── WEB_DASHBOARD_USER_SYSTEM.md # User system docs ⭐
│   ├── QUICK_START.md            # Quick start guide
│   ├── TELEGRAM_BOT_SETUP.md     # Bot setup
│   ├── status-reports/           # Historical status reports
│   └── ... (200+ doc files)
│
├── 📂 tests/                     # Test files
│   ├── test_web_api.py           # API tests
│   └── ... (15 test files)
│
├── 📂 requirements/              # Python dependencies
│   ├── base.in                   # Base requirements
│   └── dev.lock                  # Locked versions
│
├── 📂 data/                      # Local data storage
│   └── trading_bot.db            # SQLite (local dev)
│
├── 📂 logs/                      # Application logs
│
├── 📂 deploy/                    # Deployment configs
│   ├── systemd/                  # Systemd service
│   └── logrotate/                # Log rotation
│
├── 📂 importantdocs/             # Critical documentation
│
├── 📂 enhancements/              # Enhancement proposals
│
├── 📂 vendor/                    # Third-party code
│
├── 🐳 docker-compose.yml         # Docker orchestration
├── 🐳 docker-compose.prod.yml    # Production compose
├── 🐳 Dockerfile                 # Container definition
├── 📋 requirements.txt           # Python packages
├── 📄 README.md                  # Main readme
├── 📄 .env                       # Environment variables
├── 📄 .gitignore                 # Git ignore rules
└── 📄 PRODUCTION_READY_REPORT.md # Production status
```

---

## ⭐ Key Files You Need to Know

### **Web Frontend:**
- `public/user-profile.html` - **THE EPIC PROFILE PAGE**
- `public/dashboard.html` - Main dashboard
- `public/prediction-market.html` - Markets & tournaments
- `public/user-dashboard-example.html` - Dashboard with trading

### **Backend Core:**
- `src/modules/web_api.py` - **11 NEW USER API ENDPOINTS**
- `src/bot/main.py` - Telegram bot
- `src/modules/database.py` - Database with user profiles
- `scripts/run_bot.py` - Main entry point

### **Documentation:**
- `docs/WEB_DASHBOARD_USER_SYSTEM.md` - **COMPLETE API DOCS**
- `docs/API_QUICK_REFERENCE.md` - Quick reference
- `README.md` - Main readme

### **Configuration:**
- `.env` - Your API keys and settings
- `docker-compose.yml` - Container setup
- `requirements.txt` - Python dependencies

---

## 🚀 What Got Pushed to GitHub

### **New Features:**
✅ Complete user profile system  
✅ Twitter + Telegram + Wallet integration  
✅ Comprehensive PnL tracking  
✅ Global rankings and leaderboards  
✅ Wallet connect button on every page  
✅ My Profile button with pulsing glow  
✅ 11 new API endpoints for web dashboard  
✅ Full command execution from web  
✅ Epic animated profile page  
✅ Unified theme across all pages  

### **Cleaned Up:**
✅ Removed .claude temp folder  
✅ Removed duplicate HTML files  
✅ Removed apollo-dashboard duplicate  
✅ Moved 40+ status reports to docs/status-reports/  
✅ Organized all documentation  
✅ Removed temporary files  
✅ Clean folder structure  

---

## 📊 Repository Stats

**Total Files:** ~500+  
**Python Code:** 34 modules  
**Web Pages:** 7 HTML pages  
**Documentation:** 200+ docs  
**Scripts:** 60+ utility scripts  
**Tests:** 15 test files  

**Lines of Code:**
- Python: ~15,000 lines
- HTML/CSS/JS: ~8,000 lines
- Documentation: ~50,000 lines

---

## 🎯 Quick Access

### **GitHub Repository:**
https://github.com/blablablasealsaresoft/TGPrediction

### **Live URLs (Local):**
- Dashboard: http://localhost:8080/dashboard
- Profile: http://localhost:8080/profile?user_id=8059844643
- Markets: http://localhost:8080/prediction-market
- User Dashboard: http://localhost:8080/user-dashboard-example.html

### **Your Wallet:**
- Address: `DbjdbXRrfoqGmUYb4MXLTQ9H1bhqFKiP3g2sPanhucNx`
- Telegram: @CKFidel
- User ID: 8059844643

---

## ✅ What's Clean Now

**Removed:**
- ❌ .claude/ folder (temp files)
- ❌ Duplicate HTML files in root
- ❌ apollo-dashboard/ duplicate
- ❌ frontend/ duplicate
- ❌ nginx/ duplicate (kept in deploy/)
- ❌ Old dashboard files
- ❌ Temporary wallet backup
- ❌ Bot output logs

**Organized:**
- ✅ All status reports → `docs/status-reports/`
- ✅ User guides → `docs/`
- ✅ Web pages → `public/`
- ✅ Python code → `src/`
- ✅ Scripts → `scripts/`
- ✅ Tests → `tests/`

**Kept in Root (Important):**
- ✅ README.md (main readme)
- ✅ PRODUCTION_READY_REPORT.md (status)
- ✅ PRODUCTION_DEPLOYMENT_OPTIONS.md (deploy guide)
- ✅ QUICK_REFERENCE.md (quick ref)
- ✅ Docker files
- ✅ Requirements
- ✅ .env

---

**Your repo is now CLEAN, ORGANIZED, and PUSHED to GitHub!** 🎉

**GitHub:** https://github.com/blablablasealsaresoft/TGPrediction

