# 🧪 Testing Guide

**Before risking real money, test everything!**

## Test Phases

### Phase 1: Devnet Testing (MANDATORY)

Devnet is Solana's test network with free fake SOL. Test here first!

#### Setup Devnet

1. **Edit .env:**
```bash
USE_DEVNET=true
DEVNET_RPC_URL=https://api.devnet.solana.com
```

2. **Get Devnet SOL (Free!):**
```bash
# Install Solana CLI
sh -c "$(curl -sSfL https://release.solana.com/stable/install)"

# Get free devnet SOL
solana airdrop 2 YOUR_WALLET_ADDRESS --url devnet
```

3. **Test All Features:**
```
✓ /start - Bot initializes
✓ /balance - Shows devnet SOL
✓ /buy - Execute test buy (will fail - no real tokens, that's OK)
✓ /sell - Test sell command
✓ /analyze - Test token analysis
✓ /track - Test wallet tracking
✓ /settings - Configure limits
```

#### What to Test on Devnet

- [ ] Bot starts without errors
- [ ] Commands respond correctly
- [ ] Balance check works
- [ ] Error handling (try invalid addresses)
- [ ] Settings persist
- [ ] Database operations work

### Phase 2: Mainnet Micro-Testing

After devnet works perfectly:

1. **Switch to Mainnet:**
```bash
USE_DEVNET=false
SOLANA_RPC_URL=https://rpc.helius.xyz/?api-key=YOUR_KEY
```

2. **Fund with TINY amount:**
   - Send 0.1 SOL only
   - This is for testing, not trading

3. **Test Real Operations:**

```
Test 1: Check Balance
Command: /balance
Expected: Shows 0.1 SOL (or whatever you sent)
```

```
Test 2: Analyze Safe Token (SOL)
Command: /analyze So11111111111111111111111111111111111111112
Expected: High safety score (90+)
```

```
Test 3: Micro Buy Test
Command: /buy USDC_MINT 0.01
Expected: Successful swap to USDC
Verify: /balance shows USDC
```

```
Test 4: Sell Back
Command: /sell USDC_MINT <amount>
Expected: Swap back to SOL
Verify: SOL balance increased
```

```
Test 5: Safety Checks
Command: /analyze <suspicious_token>
Expected: Warnings appear if risky
```

### Phase 3: Paper Trading

Simulate trades without executing:

```python
# In solana_trading_bot.py, add paper trading mode:

class Config:
    PAPER_TRADING = True  # Add this

# In execute_buy/execute_sell:
if Config.PAPER_TRADING:
    logger.info(f"PAPER TRADE: Would buy {amount} SOL of {token}")
    return {'success': True, 'paper_trade': True, ...}
```

Run for 1-2 weeks:
- Track simulated trades
- Calculate would-be PnL
- Refine strategy
- Fix any bugs

### Phase 4: Live Trading (Small)

If paper trading was profitable:

1. **Start Conservative:**
   - Max 0.05 SOL per trade
   - Daily limit: 0.5 SOL
   - Require confirmation: ON

2. **Watch Closely:**
   - Monitor every trade
   - Check for errors
   - Track actual PnL

3. **Run Checklist:**
   - [ ] Trades execute correctly
   - [ ] Safety checks work
   - [ ] Notifications arrive
   - [ ] PnL tracking accurate
   - [ ] Stop losses trigger
   - [ ] No unexpected errors

### Phase 5: Scale Testing

Only after 50+ successful trades:

1. **Gradually increase:**
   - Week 1: 0.05 SOL per trade
   - Week 2: 0.1 SOL per trade
   - Week 3: 0.2 SOL per trade
   - Continue if profitable

2. **Monitor metrics:**
   - Win rate > 55%
   - Average win > average loss
   - Consistent profits

## Automated Testing

### Unit Tests

Create `test_bot.py`:

```python
import pytest
from solana_trading_bot import SolanaTradingBot, Config

@pytest.mark.asyncio
async def test_balance_check():
    """Test balance checking"""
    bot = SolanaTradingBot()
    balance = await bot.trading_engine._get_balance()
    assert balance >= 0

@pytest.mark.asyncio
async def test_token_analysis():
    """Test token safety analysis"""
    bot = SolanaTradingBot()
    # Test with SOL (should be safe)
    result = await bot.token_analyzer.check_token_safety(
        "So11111111111111111111111111111111111111112"
    )
    assert result['score'] > 70

@pytest.mark.asyncio
async def test_safety_limits():
    """Test safety limit enforcement"""
    bot = SolanaTradingBot()
    # Try to exceed max trade size
    result = await bot.trading_engine._pre_trade_checks(10.0)
    assert result == False  # Should block oversized trade
```

Run tests:
```bash
pytest test_bot.py -v
```

### Integration Tests

Test full workflows:

```python
@pytest.mark.asyncio
async def test_full_trade_cycle():
    """Test complete buy -> sell cycle"""
    bot = SolanaTradingBot()
    
    # Get USDC mint
    usdc = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
    
    # Buy
    buy_result = await bot.trading_engine.execute_buy(usdc, 0.01)
    assert buy_result['success']
    
    # Verify position opened
    positions = await bot.db.get_open_positions(user_id=123)
    assert len(positions) > 0
    
    # Sell
    sell_result = await bot.trading_engine.execute_sell(
        usdc, 
        buy_result['tokens_received']
    )
    assert sell_result['success']
    
    # Verify position closed
    positions = await bot.db.get_open_positions(user_id=123)
    assert len(positions) == 0
```

### Load Testing

Test bot under load:

```python
import asyncio

async def stress_test():
    """Simulate multiple concurrent users"""
    bot = SolanaTradingBot()
    
    # Simulate 10 users making requests simultaneously
    tasks = []
    for i in range(10):
        task = bot.balance_command(mock_update, mock_context)
        tasks.append(task)
    
    results = await asyncio.gather(*tasks)
    assert all(r is not None for r in results)

asyncio.run(stress_test())
```

## Test Scenarios

### Scenario 1: Honeypot Detection

```
1. Find known honeypot token
2. Run: /analyze <honeypot_address>
3. Expected: High-risk warnings
4. Try: /buy <honeypot_address> 0.01
5. Expected: Bot refuses or warns heavily
```

### Scenario 2: Slippage Protection

```
1. Find volatile token
2. Set slippage: 1% (low)
3. Try: /buy <volatile_token> 0.01
4. Expected: May fail with slippage error
5. Increase slippage to 5%
6. Try again
7. Expected: Success
```

### Scenario 3: Loss Limit

```
1. Set daily loss limit: 0.1 SOL
2. Make losing trades totaling > 0.1 SOL
3. Expected: Bot stops trading
4. Try another trade
5. Expected: Bot refuses (limit reached)
```

### Scenario 4: Emergency Stop

```
1. Start a trade
2. Immediately: /stop
3. Expected: Ongoing trades complete, new ones blocked
```

## Safety Checklist

Before live trading:

### Technical
- [ ] All tests pass
- [ ] No errors in logs
- [ ] Database operations work
- [ ] RPC connection stable
- [ ] Telegram commands responsive

### Safety Features
- [ ] Honeypot detection works
- [ ] Slippage protection active
- [ ] Trade size limits enforced
- [ ] Daily loss limit enforced
- [ ] Confirmation required
- [ ] Token analysis accurate

### Security
- [ ] Private key secure
- [ ] .env not committed to git
- [ ] RPC endpoint reliable
- [ ] Wallet funded appropriately
- [ ] Backup recovery phrase stored safely

### Monitoring
- [ ] Logs being written
- [ ] Can check balance
- [ ] Can see transaction history
- [ ] Alerts working (if enabled)

## Common Issues & Solutions

### Issue: Transactions always fail

**Diagnoses:**
- Check wallet has SOL for fees
- Verify RPC URL correct
- Ensure token mint address valid

**Fix:**
```bash
# Check balance
/balance

# Send more SOL for fees
# Need at least 0.005 SOL per transaction
```

### Issue: Bot not responding

**Diagnoses:**
- Check bot process running
- Verify Telegram token correct
- Check logs for errors

**Fix:**
```bash
# Check if running
ps aux | grep python

# Restart bot
python3 solana_trading_bot.py

# Check logs
tail -f trading_bot.log
```

### Issue: "Safety checks failed"

**Diagnoses:**
- Trade exceeds limits
- Daily loss limit reached
- Insufficient balance

**Fix:**
```bash
# Check limits
/settings

# Adjust if needed
# Or wait for daily reset
```

## Performance Benchmarks

Target metrics:

### Response Time
- Command response: < 1 second
- Balance check: < 2 seconds
- Token analysis: < 5 seconds
- Trade execution: < 10 seconds

### Reliability
- Uptime: > 99%
- Success rate: > 95%
- Error rate: < 5%

### Trading
- Win rate: > 55%
- Average profit > average loss
- Sharpe ratio: > 1.0

## Continuous Testing

Even after going live:

### Daily
- Check bot status
- Review error logs
- Verify balance matches expected
- Check recent trades

### Weekly
- Run test trade
- Review performance metrics
- Update tracked wallets
- Optimize strategies

### Monthly
- Full system test
- Security audit
- Update dependencies
- Backup database

## Test Log Template

Keep a testing log:

```
Date: 2024-01-15
Phase: Mainnet Micro-Testing
Amount Risked: 0.1 SOL

Tests:
✓ Balance check - OK
✓ Token analysis - OK
✓ Buy 0.01 SOL USDC - OK (tx: abc123)
✓ Sell USDC - OK (tx: def456)
✗ Stop loss trigger - FAILED (investigating)

Notes:
- Stop loss not triggering when expected
- Need to fix price monitoring
- Otherwise working well

Next: Fix stop loss, retest
```

## Ready for Live?

Only proceed if:
- ✅ All devnet tests passed
- ✅ Mainnet micro-tests succeeded
- ✅ Paper trading was profitable
- ✅ All safety features work
- ✅ You understand all risks
- ✅ You can afford to lose the money

If any ❌, keep testing!

Remember: **Time spent testing saves money lost trading.**
