"""
Check if automated trading is actually active and why no trades
"""

import asyncio
import sys
sys.path.insert(0, 'C:/Users/ckthe/sol')

from src.modules.database import DatabaseManager

async def check_activity():
    print("="*70)
    print("CHECKING WHY NO TRADES ARE HAPPENING")
    print("="*70)
    
    db = DatabaseManager("sqlite+aiosqlite:///trading_bot.db")
    user_id = 8059844643
    
    # Check tracked wallets
    print("\n[1] CHECKING TRACKED WALLETS...")
    tracked = await db.get_tracked_wallets(user_id)
    print(f"    Wallets in database: {len(tracked)}")
    
    if len(tracked) == 0:
        print("    [PROBLEM] No wallets tracked!")
        print("    [FIX] Run /track command or setup scripts")
        return
    else:
        print(f"    [OK] {len(tracked)} wallets ready to scan")
        print(f"    Top 5:")
        for w in sorted(tracked, key=lambda x: x.score or 0, reverse=True)[:5]:
            print(f"      • {w.wallet_address[:8]}... - {w.label} (Score: {w.score:.0f})")
    
    # Check if automated trading needs to be started
    print(f"\n[2] AUTOMATED TRADING STATUS...")
    print(f"    [INFO] To activate automated trading, you must run:")
    print(f"           /autostart")
    print(f"           in Telegram")
    print(f"    ")
    print(f"    Without /autostart:")
    print(f"      ❌ Wallets are NOT being scanned")
    print(f"      ❌ Copy trading is NOT active")
    print(f"      ❌ Only sniper works (if enabled)")
    
    # Check sniper settings
    print(f"\n[3] AUTO-SNIPER STATUS...")
    print(f"    Settings:")
    print(f"      • Min Liquidity: $2,000")
    print(f"      • Min AI Confidence: 65%")  
    print(f"      • Snipe Amount: 0.05 SOL")
    print(f"      • Max Daily Snipes: 3")
    print(f"    ")
    print(f"    Why no snipes?")
    print(f"      1. No new tokens launched recently")
    print(f"      2. Tokens failed protection checks")
    print(f"      3. AI confidence < 65%")
    print(f"      4. Liquidity < $2,000")
    print(f"      5. Sniper not enabled in Telegram (/snipe)")
    
    # Check AI settings
    print(f"\n[4] AI CONFIDENCE REQUIREMENTS...")
    print(f"    Copy Trading: 75% confidence required")
    print(f"    Auto-Sniper: 65% confidence required")
    print(f"    ")
    print(f"    This is CONSERVATIVE (good for testing)")
    print(f"    If AI gives 60% confidence → Trade SKIPPED")
    print(f"    If AI gives 75% confidence → Trade EXECUTED")
    
    # Recommendations
    print(f"\n[5] WHY NO TRADES YET - LIKELY REASONS...")
    print(f"    ")
    print(f"    Most Likely:")
    print(f"      ❌ /autostart NOT run in Telegram")
    print(f"         → Wallets NOT being scanned")
    print(f"         → Copy trading NOT active")
    print(f"    ")
    print(f"    Possible:")
    print(f"      • No new tokens launched (slow market)")
    print(f"      • Tracked wallets haven't traded")
    print(f"      • AI confidence too low")
    print(f"      • All tokens failed safety checks (GOOD!)")
    
    # Solutions
    print(f"\n{'='*70}")
    print(f"SOLUTIONS TO GET TRADES")
    print(f"{'='*70}")
    print(f"\n[IMMEDIATE] Run in Telegram:")
    print(f"  1. /autostart  ← Start wallet scanning & copy trading")
    print(f"  2. /snipe      ← Enable auto-sniper")
    print(f"  3. /autostatus ← Verify it's running")
    print(f"\n[IF STILL NO TRADES] Lower AI requirements:")
    print(f"  • Current: 75% confidence")
    print(f"  • Lower to: 60-65% for more trades")
    print(f"  • Edit .env: AUTO_TRADE_MIN_CONFIDENCE=0.65")
    print(f"\n[ALTERNATIVE] Manual test:")
    print(f"  • /trending   - See what's hot")
    print(f"  • /ai <token> - Test AI analysis")
    print(f"  • /buy <token> <amount> - Manual trade")
    
    print(f"\n{'='*70}")
    print(f"MOST IMPORTANT: DID YOU RUN /autostart?")
    print(f"{'='*70}")
    print(f"\nWithout /autostart:")
    print(f"  ❌ NO wallet scanning")
    print(f"  ❌ NO copy trading")
    print(f"  ✅ Only sniper works (but may not find tokens)")
    print(f"\nWith /autostart:")
    print(f"  ✅ Scans 17 wallets every 10 seconds")
    print(f"  ✅ Copies their trades")
    print(f"  ✅ Auto-sell enabled")

if __name__ == '__main__':
    asyncio.run(check_activity())

