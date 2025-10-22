"""
Auto cleanup tracked wallets - Keep only top 150 performers
Reduces from 558 wallets to top 150 based on performance
NO CONFIRMATION - Runs automatically!
"""

import asyncio
import sys
sys.path.insert(0, 'C:/Users/ckthe/sol')

from src.modules.database import DatabaseManager, TrackedWallet
from sqlalchemy import select
from datetime import datetime

async def cleanup_wallets():
    print("="*80)
    print(">>> AUTOMATIC WALLET CLEANUP")
    print("="*80)
    
    db = DatabaseManager("sqlite+aiosqlite:///trading_bot.db")
    user_id = 8059844643
    
    # Get all tracked wallets
    all_wallets = await db.get_tracked_wallets(user_id)
    
    print(f"\n[CURRENT STATUS]")
    print(f"   Total tracked wallets: {len(all_wallets)}")
    
    if len(all_wallets) <= 150:
        print(f"\n[INFO] You have {len(all_wallets)} wallets - within recommended range!")
        print(f"[INFO] No cleanup needed.")
        return
    
    print(f"\n[WARNING] Too many wallets! Recommended: 100-150")
    print(f"[WARNING] Current: {len(all_wallets)} (scanning will be slow!)")
    
    # Analyze wallets
    print(f"\n[ANALYZING] Wallet performance...")
    
    with_trades = sum(1 for w in all_wallets if w.total_trades > 0)
    without_trades = sum(1 for w in all_wallets if w.total_trades == 0)
    bulk_imports = sum(1 for w in all_wallets if 'Bulk import' in (w.label or ''))
    low_score = sum(1 for w in all_wallets if w.score < 70)
    
    print(f"\n[ANALYSIS]")
    print(f"   Wallets with trading history: {with_trades}")
    print(f"   Wallets with NO trades: {without_trades}")
    print(f"   Bulk imported wallets: {bulk_imports}")
    print(f"   Low score wallets: {low_score}")
    
    # Sort wallets by performance
    # Priority: total_trades > win_rate > score
    sorted_wallets = sorted(
        all_wallets,
        key=lambda w: (
            w.total_trades * 100,  # Prioritize trading activity
            w.win_rate * 10,
            w.score
        ),
        reverse=True
    )
    
    # Keep top 150
    keep_count = 150
    to_keep = sorted_wallets[:keep_count]
    to_remove = sorted_wallets[keep_count:]
    
    print(f"\n[PLAN]")
    print(f"   Keep: {len(to_keep)} top performers")
    print(f"   Disable: {len(to_remove)} low performers")
    
    # Show some examples
    print(f"\n[SAMPLE] Wallets to be disabled (first 10):")
    for i, wallet in enumerate(to_remove[:10], 1):
        addr = wallet.wallet_address or 'Unknown'
        label = wallet.label or 'N/A'
        trades = wallet.total_trades
        score = wallet.score
        print(f"   {i}. {addr[:8]}... - {label} - {trades} trades - Score: {score:.0f}")
    
    # AUTO-CONFIRM - No user input needed
    print(f"\n[AUTO-CONFIRM] Proceeding with cleanup...")
    
    # Disable wallets
    print(f"\n[PROCESSING] Disabling {len(to_remove)} wallets...")
    
    removed = 0
    
    try:
        async with db.async_session() as session:
            for wallet in to_remove:
                try:
                    # Get the wallet from the session and update it
                    stmt = select(TrackedWallet).where(TrackedWallet.id == wallet.id)
                    result = await session.execute(stmt)
                    db_wallet = result.scalar_one_or_none()
                    
                    if db_wallet:
                        db_wallet.copy_enabled = False
                        removed += 1
                        
                        if removed % 50 == 0:
                            print(f"  [OK] Disabled {removed}/{len(to_remove)}...")
                
                except Exception as e:
                    print(f"  [WARN] Failed to disable wallet {wallet.id}: {e}")
                    continue
            
            # Commit all changes at once
            await session.commit()
            print(f"  [OK] Committed all changes")
    
    except Exception as e:
        print(f"  [ERROR] Batch update failed: {e}")
        return
    
    # Final count
    remaining = await db.get_tracked_wallets(user_id)
    active = [w for w in remaining if w.copy_enabled]
    
    print(f"\n{'='*80}")
    print(f">>> CLEANUP COMPLETE!")
    print(f"{'='*80}")
    print(f"\n[RESULTS]")
    print(f"   Disabled: {removed} wallets")
    print(f"   Active tracking: {len(active)} wallets")
    print(f"   Total in DB: {len(remaining)} (includes disabled)")
    
    print(f"\n[PERFORMANCE] Expected improvements:")
    print(f"   + Scan time: 7-10 seconds (was 35-40 seconds)")
    print(f"   + RPC usage: ~{len(active) * 60}/hour (was ~{558 * 60}/hour)")
    print(f"   + Trade signals: 15-30/day (was 50-100/day)")
    print(f"   + Much easier to monitor!")
    
    print(f"\n[NEXT] Restart bot to apply changes:")
    print(f"   python scripts/run_bot.py")
    
    print(f"\n[TIP] You can re-enable wallets later if needed via Telegram")

if __name__ == '__main__':
    asyncio.run(cleanup_wallets())

