# Advanced Features Activation Guide

**When to use this:** After 1 week of stable operation

**Prerequisites:**
- ✅ Bot running 7+ days without critical issues
- ✅ 20+ successful manual trades executed
- ✅ Success rate >70%
- ✅ Comfortable with platform behavior
- ✅ Monitoring routines established

---

## ⚠️ Risk Assessment

### Medium Risk Features
- **Auto-Sniper** - Automatically catches new launches
- **Copy Trading** - Follows 441 elite wallets
- **Auto-Predictions** - Trades on ULTRA confidence (90%+)

### High Risk Features
- **Flash Loan Arbitrage** - 100x leverage
- **Launch Auto-Sniper** - Pre-launch execution
- **Full Automation** - 24/7 AI trading

---

## Feature 1: Auto-Sniper 🎯

### What It Does
- Monitors Pump.fun + DexScreener 24/7
- Detects new token launches in <100ms
- Analyzes with AI automatically
- Executes if confidence >65%
- Uses Jito bundles for MEV protection

### Enable Command

```
/snipe_enable
```

### Configuration (from ENV)
- Max per snipe: 0.5 SOL
- Daily limit: 10 snipes
- Min liquidity: 5 SOL
- AI confidence: Must be >65%

### Monitoring

**Watch for 24 hours:**
```powershell
docker-compose -f docker-compose.prod.yml logs -f trading-bot | Select-String "snipe"
```

**Look for:**
- ✅ "🎯 NEW LAUNCH DETECTED"
- ✅ "AI analyzing token..."
- ✅ "SNIPED! Entry: 0.5 SOL"

### Safety Limits
- Max 10 snipes per day (can't exceed)
- Max 0.5 SOL per snipe (configured)
- AI must approve (confidence check)
- Daily loss limit still applies

### Disable If Needed

```
/snipe_disable
```

---

## Feature 2: Automated Trading 🤖

### What It Does
- Monitors 441 elite wallets continuously
- Detects when elite wallets buy tokens
- Analyzes with AI (must be >75% confidence)
- Copies trades automatically
- Manages stop-loss/take-profit

### Enable Command

```
/autostart
```

### Configuration (from ENV)
- Min confidence: 75%
- Max daily trades: 25
- Daily limit: 10 SOL
- Copy amount: Per wallet settings

### Monitoring

**Watch for 1 hour first:**
```powershell
docker-compose -f docker-compose.prod.yml logs -f trading-bot | Select-String "automated"
```

**Look for:**
- ✅ "Scanning X wallets for activity"
- ✅ "Opportunity found: confidence X%"
- ✅ "Executing automated trade"

**Check status:**
```
/autostatus
```

### Disable If Needed

```
/autostop
```

---

## Feature 3: Flash Loan Arbitrage ⚡

### Requirements
- **Tier:** Gold, Platinum, or Elite
- **Points:** 2000+ (Gold tier)
- **Experience:** 50+ successful trades

### What It Does
- Scans for price differences across DEXs every 2s
- Borrows up to 50 SOL (Gold) via flash loan
- Executes atomic arbitrage
- Repays loan + fees
- Keeps profit (minus 5% platform fee)

### Enable Command

```
/flash_enable
```

⚠️ **Only enable after:**
- 1 week stable operation
- Gold tier achieved
- Manual trades successful
- Understanding how it works

### Monitoring

**First 24 hours - watch closely:**
```powershell
docker-compose -f docker-compose.prod.yml logs -f trading-bot | Select-String "flash"
```

**Look for:**
- ✅ "Arbitrage opportunity found"
- ✅ "Simulating flash loan transaction"
- ✅ "Flash loan executed successfully"
- ❌ Any errors (stop immediately if errors)

### Safety
- All transactions are atomic (all-or-nothing)
- Can't lose borrowed funds
- Only risk is gas fees
- Platform fee: 5% of profits

---

## Feature 4: Auto-Predictions 📊

### What It Does
- Continuously generates predictions
- Auto-trades on ULTRA confidence (90%+)
- Uses Kelly Criterion position sizing
- Maximum risk management

### Enable Command

```
/autopredictions
```

### Configuration
- ULTRA only: 90%+ confidence required
- Position sizing: Kelly Criterion (0.25 fraction)
- Max positions: 5 concurrent
- Stop-loss: 15% (from ENV)
- Take-profit: 75% (from ENV)

### Monitoring

**Check prediction performance:**
```
/prediction_stats
```

**Look for:**
- Accuracy >65%
- ULTRA predictions winning >80%
- Position sizes appropriate

---

## Feature 5: Launch Monitor 🚀

### What It Does
- Monitors Twitter/Reddit for launch announcements
- Tracks 441 elite wallets for pre-launch interest
- Verifies team credentials
- Alerts 2-6 hours BEFORE launch
- Auto-snipes ULTRA confidence (90%+)

### Enable Command

```
/launch_monitor enable
```

### What to Expect
- Notifications for upcoming launches
- Pre-launch confidence scores
- Team verification results
- Automatic snipe preparation

### Monitoring

```
/launch_predictions
/launch_stats
```

**Look for:**
- High-confidence launches (ULTRA)
- Team verified ✅
- Whale interest confirmed
- Liquidity commitment locked

---

## Activation Timeline

### Week 2: Low-Risk Features
1. **Enable auto-sniper** (`/snipe_enable`)
   - Monitor for 24 hours
   - Check snipe success rate
   - Adjust if needed

2. **Test copy trading** (`/copy <trader> 0.1`)
   - Copy 1-2 elite traders
   - Monitor for 24 hours
   - Verify trades detected

### Week 3: Medium-Risk Features
3. **Enable automation** (`/autostart`)
   - Monitor for 24 hours
   - Check trade quality
   - Verify signals accurate

4. **Enable predictions** (`/autopredictions`)
   - Watch for ULTRA signals
   - Verify position sizing
   - Check win rate

### Week 4+: Advanced Features
5. **Launch monitoring** (`/launch_monitor enable`)
   - Needs stable operation first
   - Requires team verification working
   - Monitor closely for first week

6. **Flash loans** (`/flash_enable` - IF Gold tier)
   - Only when tier achieved
   - Watch very closely
   - Start with simulations

---

## Monitoring Dashboard

### Commands to Run Daily (When Automated)

```
/autostatus       ← Automation status
/sniper_status    ← Sniper performance  
/prediction_stats ← Prediction accuracy
/flash_stats      ← Arbitrage performance (if enabled)
/launch_stats     ← Launch predictions (if enabled)
/stats            ← Overall performance
```

### What Good Looks Like

**Auto-Sniper:**
- 2-5 snipes per day
- Success rate >70%
- Profitable >60% of time

**Automation:**
- 5-15 trades per day
- Success rate >70%
- Following high-score wallets

**Predictions:**
- ULTRA accuracy >80%
- HIGH accuracy >70%
- Overall accuracy >65%

**Flash Loans:**
- 1-5 opportunities per week
- 100% success rate (atomic)
- Small but consistent profits

---

## Emergency Procedures

### Disable Everything

```
/autostop
/snipe_disable
/flash_disable  (if was enabled)
/launch_monitor disable  (if was enabled)
```

**Or stop the bot:**
```powershell
docker-compose -f docker-compose.prod.yml stop trading-bot
```

### Investigate Issues

**Check what happened:**
```powershell
# Last 100 log lines
docker-compose -f docker-compose.prod.yml logs --tail=100 trading-bot

# All errors
docker exec trading-bot-app grep '"level": "ERROR"' logs/trading_bot.jsonl | tail -20

# Recent trades
docker exec -it trading-bot-db psql -U trader -d trading_bot -c "
SELECT timestamp, trade_type, token_symbol, amount_sol, success, error_message
FROM trades 
WHERE timestamp > NOW() - INTERVAL '1 hour'
ORDER BY timestamp DESC;
"
```

---

## Performance Optimization

### If Auto-Sniper Missing Launches

**Possible causes:**
- Scan interval too slow (currently 10s)
- AI rejection (confidence <65%)
- Daily limit reached (10 snipes)
- Liquidity requirements (5 SOL minimum)

**Check:**
```
/sniper_status
```

### If Automation Not Finding Trades

**Possible causes:**
- Confidence threshold too high (75%)
- Elite wallets not active recently
- Markets are quiet
- RPC rate limiting

**Check:**
```
/autostatus
```

**Review wallet activity:**
```powershell
docker-compose -f docker-compose.prod.yml logs trading-bot | Select-String "opportunity"
```

### If Flash Loans Finding Nothing

**Normal!** Arbitrage opportunities are rare:
- Appear during high volatility
- Usually 1-5 per week
- More common during:
  - New launches
  - Market volatility
  - High trading volume

**Check:**
```
/flash_opportunities
/flash_stats
```

---

## Best Practices

### Feature Activation Order

1. ✅ **Week 1:** Manual trading only
2. ✅ **Week 2:** Auto-sniper (lowest risk)
3. ✅ **Week 3:** Automation (medium risk)
4. ⚠️ **Week 4:** Predictions (medium-high risk)
5. ⚠️ **Week 5+:** Flash loans (high leverage)

### Golden Rules

1. **One feature at a time** - Enable, monitor 24h, then next
2. **Start conservative** - Small amounts, high confidence only
3. **Monitor closely** - First 24 hours are critical
4. **Be ready to disable** - Keep emergency stop handy
5. **Track performance** - Use `/stats` and `/metrics` daily

### Success Metrics

**After enabling each feature:**
- Monitor for 24 hours
- Success rate should be >70%
- No critical errors
- Profitable or break-even minimum
- Comfortable with behavior

**If ANY feature shows:**
- Success rate <50%
- Critical errors
- Unexpected losses
- Strange behavior

**→ DISABLE immediately and investigate**

---

## 📞 Support

### Logs Location
- Local: `logs/trading_bot.jsonl`
- Docker: `docker logs trading-bot-app`

### Database Access
```powershell
docker exec -it trading-bot-db psql -U trader -d trading_bot
```

### Emergency Contact
Send `/metrics` on Telegram to see current status

---

## ✅ Activation Checklist

**Before enabling any advanced feature:**

- [ ] Bot stable >7 days
- [ ] Success rate >70%
- [ ] No recent critical errors
- [ ] Daily monitoring routine established
- [ ] Comfortable with current features
- [ ] Emergency stop procedure ready
- [ ] Backup created recently

**Then activate ONE feature at a time and monitor for 24 hours.**

---

**Remember:** You can always disable features and return to manual trading if needed!

**Success is:** Slow, steady, profitable automation. Not rushing into everything at once.

---

**Last Updated:** 2025-01-11
**Version:** 1.0.0

