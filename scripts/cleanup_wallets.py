"""
Clean up tracked wallets - Keep only top performers
Reduces from 558 wallets to top 100-150 based on performance
"""

import asyncio
import sys
sys.path.insert(0, 'C:/Users/ckthe/sol')

from src.modules.database import DatabaseManager
from datetime import datetime

async def cleanup_wallets():
    print("="*80)
    print(">>> WALLET CLEANUP TOOL")
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
    
    # Group wallets by category
    with_trades = []
    without_trades = []
    bulk_imports = []
    old_wallets = []
    
    for wallet in all_wallets:
        if wallet.get('total_trades', 0) > 0:
            with_trades.append(wallet)
        else:
            without_trades.append(wallet)
        
        if 'Bulk import' in wallet.get('label', ''):
            bulk_imports.append(wallet)
        
        # Check if wallet is from old tracking (before bulk import)
        if wallet.get('score', 0) < 70:
            old_wallets.append(wallet)
    
    print(f"\n[ANALYSIS]")
    print(f"   Wallets with trading history: {len(with_trades)}")
    print(f"   Wallets with NO trades: {len(without_trades)}")
    print(f"   Bulk imported wallets: {len(bulk_imports)}")
    print(f"   Low score wallets: {len(old_wallets)}")
    
    # Strategy: Keep top 150 by performance
    print(f"\n[STRATEGY] Keep top 150 wallets based on:")
    print(f"   1. Trading activity (total_trades)")
    print(f"   2. Win rate")
    print(f"   3. Score")
    
    # Sort wallets by performance
    sorted_wallets = sorted(
        all_wallets,
        key=lambda w: (
            w.get('total_trades', 0) * 100,  # Prioritize trading activity
            w.get('win_rate', 0) * 10,
            w.get('score', 0)
        ),
        reverse=True
    )
    
    # Keep top 150
    keep_count = 150
    to_keep = sorted_wallets[:keep_count]
    to_remove = sorted_wallets[keep_count:]
    
    print(f"\n[PLAN]")
    print(f"   Keep: {len(to_keep)} top performers")
    print(f"   Remove: {len(to_remove)} low performers")
    
    # Show some examples of what will be removed
    print(f"\n[SAMPLE] Wallets to be removed (first 10):")
    for i, wallet in enumerate(to_remove[:10], 1):
        addr = wallet.get('wallet_address', 'Unknown')
        label = wallet.get('label', 'N/A')
        trades = wallet.get('total_trades', 0)
        score = wallet.get('score', 0)
        print(f"   {i}. {addr[:8]}... - {label} - {trades} trades - Score: {score:.0f}")
    
    # Confirm
    print(f"\n[CONFIRMATION]")
    response = input(f"Remove {len(to_remove)} wallets? (yes/no): ").strip().lower()
    
    if response != 'yes':
        print(f"\n[CANCELLED] No wallets removed.")
        return
    
    # Remove wallets
    print(f"\n[REMOVING] Deleting {len(to_remove)} wallets...")
    
    removed = 0
    for wallet in to_remove:
        try:
            # Delete from database
            # Note: We need to add a delete method to DatabaseManager
            # For now, we'll just mark them as disabled
            wallet_id = wallet.get('id')
            if wallet_id:
                # Disable the wallet instead of deleting
                # This preserves history but stops tracking
                await db.execute(
                    "UPDATE tracked_wallets SET copy_enabled = 0 WHERE id = ?",
                    (wallet_id,)
                )
                removed += 1
                
                if removed % 50 == 0:
                    print(f"  [OK] Disabled {removed}/{len(to_remove)}...")
        
        except Exception as e:
            print(f"  [ERROR] Failed to disable wallet: {e}")
    
    # Final count
    remaining = await db.get_tracked_wallets(user_id)
    active = [w for w in remaining if w.get('copy_enabled', False)]
    
    print(f"\n{'='*80}")
    print(f">>> CLEANUP COMPLETE!")
    print(f"{'='*80}")
    print(f"\n[RESULTS]")
    print(f"   Disabled: {removed} wallets")
    print(f"   Active tracking: {len(active)} wallets")
    print(f"   Total in DB: {len(remaining)} (includes disabled)")
    
    print(f"\n[PERFORMANCE] Expected improvements:")
    print(f"   + Scan time: 7-10 seconds (was 35-40 seconds)")
    print(f"   + RPC usage: 9,000/hour (was 33,000/hour)")
    print(f"   + Trade signals: 15-30/day (was 50-100/day)")
    print(f"   + Much easier to monitor!")
    
    print(f"\n[NEXT] Restart bot to apply changes:")
    print(f"   python scripts/run_bot.py")

if __name__ == '__main__':
    asyncio.run(cleanup_wallets())

