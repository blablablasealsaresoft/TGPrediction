# 🚨 Enable Live Trading - Step-by-Step Guide

**⚠️ CAUTION:** This enables real SOL transactions. Follow carefully!

---

## Prerequisites

Before enabling live trading, ensure:
- ✅ Bot running stable for at least 1 hour
- ✅ All test commands work (Phase 1-4)
- ✅ You understand the risks
- ✅ Wallet funded with test amount (0.5-1.0 SOL)

---

## Step 1: Fund Your Wallet

### Get Your Deposit Address

On Telegram, send:
```
/deposit
```

**Your wallet:** `DbjdbXRrfoqGmUYb4MXLTQ9H1bhqFKiP3g2sPanhucNx`

### Send Test Funds

**Recommended first funding:** 0.5-1.0 SOL

Send from:
- Phantom wallet
- Solflare wallet
- Exchange (Coinbase, Binance, etc.)

### Verify Balance

```
/balance
```

**Expected:** Shows your SOL balance

---

## Step 2: Enable Broadcast Mode

### Update .env File

**Find this line:**
```bash
ALLOW_BROADCAST=false
```

**Change to:**
```bash
ALLOW_BROADCAST=true
```

**Save the file.**

---

## Step 3: Restart Bot

```powershell
docker-compose -f docker-compose.prod.yml restart trading-bot
```

**Monitor the restart:**
```powershell
docker-compose -f docker-compose.prod.yml logs -f trading-bot
```

**Look for:**
```
Broadcast allowed: true  ← Should now say TRUE
```

---

## Step 4: Test Small Trade

### Pick a Safe Token

**Recommended test token (USDC):**
```
EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v
```

### Execute Test Buy

**IMPORTANT:** Must include confirm token!

```
/buy EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v 0.05 confirm=lYBjdXRJLcMFCLKCcOmTCCUniHOdi31A
```

**What happens:**
1. Bot analyzes token with AI
2. Checks 6-layer protection
3. Routes through Jupiter
4. Executes via Jito bundle (MEV protected)
5. Records to database
6. Shows you transaction signature

### Monitor Execution

**Watch logs:**
```powershell
docker-compose -f docker-compose.prod.yml logs -f trading-bot | Select-String "execute_buy"
```

**Check on Solscan:**
- Go to: https://solscan.io/tx/[your_signature]
- Verify: Transaction succeeded
- Check: Tokens received

---

## Step 5: Test Sell

### View Your Position

```
/positions
```

**Expected:** Shows your open position with current PnL

### Execute Sell

```
/sell EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v 100% confirm=lYBjdXRJLcMFCLKCcOmTCCUniHOdi31A
```

**What happens:**
1. Bot calculates position size
2. Routes through Jupiter for best price
3. Executes sell
4. Closes position
5. Shows PnL

---

## Safety Checklist

### Before Each Trade

- [ ] Check token with `/ai <token>` first
- [ ] Use small amounts (0.05-0.1 SOL)
- [ ] Always include confirm token
- [ ] Watch logs for execution
- [ ] Verify on blockchain (Solscan)

### Daily Limits (Configured)

- Max trade size: 5.0 SOL
- Max daily loss: 2.0 SOL
- Max trades per hour: 30
- Circuit breaker: 5 consecutive losses

### Emergency Stop

**If something goes wrong:**
```powershell
# Immediate stop
docker-compose -f docker-compose.prod.yml stop trading-bot

# Or disable broadcast
ALLOW_BROADCAST=false  # in .env
# Then restart
```

---

## Risk Management

### Start Small
- Week 1: 0.05-0.1 SOL per trade
- Week 2: 0.2-0.5 SOL per trade
- Week 3+: Up to configured limits (5 SOL max)

### Tokens to Avoid Initially
- ❌ New launches (<24 hours old)
- ❌ Low liquidity (<$10,000)
- ❌ Tokens with warnings from AI
- ❌ Honeypots (AI will detect)

### Safe Test Tokens
- ✅ USDC (EPjFWdd5...)
- ✅ USDT (Es9vMF...)
- ✅ Major Solana tokens with high liquidity

---

## Monitoring Live Trading

### Watch Logs Continuously (First Hour)

```powershell
docker-compose -f docker-compose.prod.yml logs -f trading-bot
```

**Look for:**
- ✅ "Trade executed successfully"
- ✅ "Position opened"
- ✅ Transaction signatures
- ❌ Any ERROR messages

### Check Telegram /metrics

Every 15 minutes:
```
/metrics
```

**Monitor:**
- Success rate (should stay >90%)
- Failed trades (should be 0-1)
- Recent errors (should be 0)

### Verify on Blockchain

For each trade, check Solscan:
- Transaction succeeded?
- Correct amount?
- MEV protection (Jito bundle)?
- Slippage within limits?

---

## Common Issues & Solutions

### Issue: "Confirmation required"

**Problem:** You forgot the confirm token

**Solution:** Add to command:
```
confirm=lYBjdXRJLcMFCLKCcOmTCCUniHOdi31A
```

### Issue: "Insufficient balance"

**Problem:** Not enough SOL or tokens

**Solution:** Check balance with `/balance`, fund if needed

### Issue: "Token failed safety check"

**Problem:** AI detected risks (honeypot, low liquidity, etc.)

**Solution:** Don't trade this token. Use `/ai <token>` to see why.

### Issue: Trade times out

**Problem:** RPC issues or network congestion

**Solution:**
- Wait and retry
- Check logs for RPC errors
- Verify Helius API key active

---

## Rollback to Safe Mode

**If you want to disable live trading:**

1. **Stop live trades:**
```powershell
docker-compose -f docker-compose.prod.yml stop trading-bot
```

2. **Disable broadcast:**
Change in `.env`:
```bash
ALLOW_BROADCAST=false
```

3. **Restart:**
```powershell
docker-compose -f docker-compose.prod.yml start trading-bot
```

4. **Verify:**
```
/metrics
```
Should show broadcast disabled

---

## Success Criteria

### First Live Trade ✅

- [ ] Trade executed without errors
- [ ] Transaction found on Solscan
- [ ] Tokens received in wallet
- [ ] Position recorded in database
- [ ] PnL tracked correctly

### First Week Live ✅

- [ ] 10+ successful trades
- [ ] Win rate >60%
- [ ] No critical errors
- [ ] Daily loss limit not exceeded
- [ ] No honeypot/rug trades

---

## Next Steps After Live Trading Works

### Week 1: Manual Trading Only
- Test buy/sell manually
- Learn token analysis
- Build confidence
- Watch patterns

### Week 2: Enable Automation
- `/snipe_enable` - Catch launches
- `/autostart` - AI trading
- `/copy <trader>` - Copy elite wallets

### Week 3+: Advanced Features
- `/flash_enable` - Flash loan arbitrage
- `/autopredictions` - Auto-trade on ULTRA
- `/launch_monitor enable` - Pre-launch detection

---

## 💡 Pro Tips

### Best Practices
- Always analyze with `/ai` before buying
- Start trading during market hours (not 3am)
- Check liquidity first (>$10,000)
- Use stop-loss on volatile tokens
- Take profits incrementally (sell 50%, 50%)

### What to Monitor
- Success rate (aim for >70%)
- Average profit per trade
- Time to execution (<2 seconds)
- Slippage (should be <2%)

### When to Stop
- If success rate drops below 50%
- If daily loss limit hit
- If multiple errors in row
- If something feels wrong

---

## 🎯 Your First Real Trade Template

```bash
# 1. Analyze
/ai EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v

# 2. Wait for AI analysis (should show HIGH score for USDC)

# 3. Buy small amount
/buy EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v 0.05 confirm=lYBjdXRJLcMFCLKCcOmTCCUniHOdi31A

# 4. Check position
/positions

# 5. Sell when ready
/sell EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v 100% confirm=lYBjdXRJLcMFCLKCcOmTCCUniHOdi31A

# 6. Check results
/stats
```

---

**Ready to go live?** Follow the steps above carefully! 🚀

**Not ready?** Keep testing in read-only mode (ALLOW_BROADCAST=false)

---

**Remember:** You can always revert to safe mode by setting `ALLOW_BROADCAST=false` and restarting.

**Confirm token:** `lYBjdXRJLcMFCLKCcOmTCCUniHOdi31A` (save this!)

