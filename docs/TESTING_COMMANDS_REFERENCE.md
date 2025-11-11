# 📱 TESTING COMMANDS - Quick Reference

**Copy-paste these commands directly into Telegram!**

---

## 🎯 PHASE 2: CORE FEATURES

### 2.1 Core Functionality (5 commands)

```
/start
```
```
/wallet
```
```
/balance
```
```
/help
```
```
/metrics
```

### 2.2 AI & Analysis (2 commands + verification)

```
/ai EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v
```
```
/analyze EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v
```

### 2.3 Trading Flow (1 command - should fail safely)

```
/buy EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v 0.1
```

**Expected:** Error about broadcast not allowed ✅

### 2.4 Copy Trading (5 commands)

```
/leaderboard
```
```
/rankings
```
```
/copy 1928855074 0.1
```
```
/my_copies
```
```
/stop_copy 1928855074
```

---

## 🎯 PHASE 3: FEATURES VALIDATION

### 3.1 Phase 1: Probability Predictions (3 commands)

```
/predict So11111111111111111111111111111111111111112
```
```
/autopredictions
```
```
/prediction_stats
```

### 3.2 Phase 2: Flash Loan Arbitrage (3 commands)

```
/flash_arb
```
```
/flash_opportunities
```
```
/flash_stats
```

### 3.3 Phase 3: Bundle Launch Predictor (4 commands)

```
/launch_predictions
```
```
/launch_stats
```
```
/launch_monitor enable
```
```
/launch_monitor disable
```

### 3.4 Phase 4: Prediction Markets (3 commands)

```
/markets
```
```
/my_predictions
```
```
/market_leaderboard
```

---

## 📊 ADDITIONAL USEFUL COMMANDS

### General

```
/trending
```
```
/rewards
```
```
/strategies
```
```
/my_strategies
```
```
/autostatus
```
```
/sniper_status
```

### Analysis on Different Tokens

```
/ai So11111111111111111111111111111111111111112
```
```
/predict EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v
```

---

## 🔍 LOG VERIFICATION COMMANDS

**Run these in PowerShell to verify background activity:**

### Check Wallet Scanning

```powershell
docker-compose -f docker-compose.prod.yml logs trading-bot | Select-String -Pattern "wallet|scanning" | Select-Object -Last 20
```

### Check Transaction Parsing

```powershell
docker-compose -f docker-compose.prod.yml logs trading-bot | Select-String -Pattern "parse|Helius" | Select-Object -Last 20
```

### Check Sentiment Monitoring

```powershell
docker-compose -f docker-compose.prod.yml logs trading-bot | Select-String -Pattern "Twitter|Reddit|sentiment" | Select-Object -Last 20
```

### Check Flash Arbitrage Scanning

```powershell
docker-compose -f docker-compose.prod.yml logs trading-bot | Select-String -Pattern "flash|arbitrage" | Select-Object -Last 20
```

### Check Launch Detection

```powershell
docker-compose -f docker-compose.prod.yml logs trading-bot | Select-String -Pattern "launch|Birdeye|DexScreener" | Select-Object -Last 20
```

### Check for Any Errors

```powershell
docker exec trading-bot-app grep '"level": "ERROR"' logs/trading_bot.jsonl | Select-Object -Last 10
```

---

## ✅ QUICK CHECKLIST

**Just check these off as you test:**

### Core (5)
- [ ] `/start`
- [ ] `/wallet`
- [ ] `/balance`
- [ ] `/help`
- [ ] `/metrics`

### AI (2)
- [ ] `/ai`
- [ ] `/analyze`

### Copy Trading (5)
- [ ] `/leaderboard`
- [ ] `/rankings`
- [ ] `/copy`
- [ ] `/my_copies`
- [ ] `/stop_copy`

### Phase 1 (3)
- [ ] `/predict`
- [ ] `/autopredictions`
- [ ] `/prediction_stats`

### Phase 2 (3)
- [ ] `/flash_arb`
- [ ] `/flash_opportunities`
- [ ] `/flash_stats`

### Phase 3 (4)
- [ ] `/launch_predictions`
- [ ] `/launch_stats`
- [ ] `/launch_monitor enable`
- [ ] `/launch_monitor disable`

### Phase 4 (3)
- [ ] `/markets`
- [ ] `/my_predictions`
- [ ] `/market_leaderboard`

**Total: 25 commands to test**

---

## 📈 EXPECTED RESULTS

### What Should Work ✅

- All commands should respond (no timeouts)
- No "unknown command" errors
- Professional formatted output
- Clear explanations
- Helpful error messages (like for /buy)

### What's Normal

- **0 balances:** You haven't funded yet
- **0 stats:** Fresh database
- **No opportunities:** Markets are efficient
- **No launches:** Not always active
- **No markets:** None created yet
- **Low predictions:** Neural engine needs data

### What's NOT Normal ❌

- Command timeouts
- "Unknown command" errors
- Bot not responding
- Database connection errors
- Container crashes

---

## 🎯 START TESTING NOW!

**Copy commands from above and paste into Telegram!**

**Check them off as you go!**

**Report any issues!**

---

**Testing Guide:** `COMPREHENSIVE_TESTING_CHECKLIST.md`
**Quick Reference:** This file
**Need Help:** Check `docs/NEXT_STEPS_FOR_USER.md`

