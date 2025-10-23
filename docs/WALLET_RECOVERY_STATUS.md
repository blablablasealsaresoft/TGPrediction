# 💰 Wallet Recovery Status

## ✅ GOOD NEWS: Wallet Found & Restored!

### Restored Wallet:
```
Address: GopttzS692Y7srtZ6EhCzzuNznEwGqDrA2rU4HfgVC1b
Balance: 0.105000 SOL ✅
Status: RESTORED from backup
```

**This wallet is now active in your bot!**

---

## 📊 Your Old Wallet Status

### Wallet from Yesterday:
```
Address: mDSm6bqKdKc8ARbsdAkkHKzDzAqERuFxMChiGmuUDaR  
Balance: 0.200000 SOL (still on-chain!)
Status: NOT in database (needs private key to recover)
```

**The 0.2 SOL is still there on-chain!**

---

## 🚀 QUICK START (Use Restored Wallet)

### Step 1: Restart Bot
```bash
python scripts/run_bot.py
```

### Step 2: Verify in Telegram
```
/wallet
```

**Should now show:**
```
Address: GopttzS692Y7srtZ6EhCzzuNznEwGqDrA2rU4HfgVC1b
Balance: 0.105000 SOL ✅
```

### Step 3: Start Trading
```
/autostart      # Starts copy trading + sniper
```

**DONE!** ✅ You're trading with 0.105 SOL

---

## 💡 To Recover Your 0.2 SOL Wallet

If you have the private key for `mDSm6bqKdKc8ARbsdAkkHKzDzAqERuFxMChiGmuUDaR`:

### Check Export Files

Look for export files from yesterday:
```bash
dir export_*.csv
```

These contain wallet private keys!

### Or Use /export_wallet Log

Check your Telegram chat history for `/export_wallet` command from yesterday.

### Import That Wallet

If you find the private key:
```python
# Create import_my_wallet.py
import asyncio
from src.modules.database import DatabaseManager, UserWallet
from src.modules.wallet_manager import WalletEncryption

async def import_wallet():
    db = DatabaseManager()
    encryption = WalletEncryption()
    
    # YOUR PRIVATE KEY HERE
    private_key = "your_private_key_here"
    public_key = "mDSm6bqKdKc8ARbsdAkkHKzDzAqERuFxMChiGmuUDaR"
    
    encrypted = encryption.encrypt_key(private_key)
    
    async with db.async_session() as session:
        # Delete old
        from sqlalchemy import delete
        await session.execute(delete(UserWallet).where(UserWallet.user_id == 6594416344))
        
        # Add new
        wallet = UserWallet(
            user_id=6594416344,
            public_key=public_key,
            encrypted_private_key=encrypted
        )
        session.add(wallet)
        await session.commit()
    
    print(f"✅ Wallet restored with 0.2 SOL!")

asyncio.run(import_wallet())
```

---

## 📋 Summary

### Current Situation:
- ✅ **Restored wallet:** 0.105 SOL (active now)
- ⚠️ **Old wallet:** 0.2 SOL (need private key)
- **Total you have:** 0.305 SOL

### What to Do:

**Option A: Use Current Wallet (0.105 SOL)**
```bash
python scripts/run_bot.py
# Then /wallet and /autostart
```

**Option B: Recover 0.2 SOL Wallet**
1. Check export files: `dir export_*.csv`
2. Or check Telegram history for `/export_wallet`
3. Find private key for `mDSm6bqKdKc8ARbsdAkkHKzDzAqERuFxMChiGmuUDaR`
4. Let me know and I'll import it

**Option C: Combine Both**
1. Use current wallet (0.105 SOL)
2. If you find old wallet key, transfer the 0.2 SOL to current wallet
3. Then you have 0.305 SOL total!

---

## ✅ Recommended: Start Trading NOW

You have **0.105 SOL** which is enough to start!

```bash
python scripts/run_bot.py
```

Then in Telegram:
```
/wallet       # Verify shows 0.105 SOL
/autostart    # Start trading!
```

**You're ready to trade!** 🚀

---

**Check export files for the 0.2 SOL wallet key, or just start trading with 0.105 SOL now!**

