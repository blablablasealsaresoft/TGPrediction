#!/usr/bin/env python3
"""
Check and add all wallets from unique_wallets_list.txt
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.modules.database import DatabaseManager
from src.config import get_config

async def check_and_add_wallets():
    """Check current wallets and add missing ones"""
    print("\nBULK WALLET IMPORT")
    print("=" * 60)
    
    config = get_config()
    db = DatabaseManager(config.database_url)
    await db.init_db()
    
    # Read wallets from file
    wallets_to_add = []
    
    print("Reading unique_wallets_list.txt...")
    
    with open('unique_wallets_list.txt', 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            # Extract wallet addresses (skip headers/numbers/empty lines)
            if not line or line.startswith('=') or line.startswith('COMPREHENSIVE') or line.startswith('Total:'):
                continue
            
            # Remove the number prefix (e.g., "1. " or "  10. ")
            parts = line.split('. ', 1)
            if len(parts) > 1:
                wallet = parts[1].strip()
                # Validate it looks like a Solana address (32-44 chars, alphanumeric)
                if 32 <= len(wallet) <= 44 and wallet.replace('_', '').isalnum():
                    wallets_to_add.append(wallet)
    
    print(f"Found {len(wallets_to_add)} valid wallet addresses")
    
    # Check which are already tracked
    existing = await db.get_tracked_wallets(user_id=1)
    existing_addresses = set(w.wallet_address for w in existing)
    
    print(f"Already tracked: {len(existing_addresses)}")
    
    # Find new wallets to add
    new_wallets = [w for w in wallets_to_add if w not in existing_addresses]
    
    print(f"New wallets to add: {len(new_wallets)}")
    
    if not new_wallets:
        print("\nALL WALLETS ALREADY TRACKED!")
        print(f"Total tracked: {len(existing_addresses)}")
        await db.dispose()
        return True
    
    # Add new wallets
    print(f"\nAdding {len(new_wallets)} wallets to database...")
    
    added_count = 0
    failed_count = 0
    
    for i, wallet in enumerate(new_wallets, 1):
        try:
            wallet_data = {
                'user_id': 1,
                'wallet_address': wallet,
                'label': f"Copy trading wallet {i}",
                'score': 0.0,  # Will be calculated by wallet intelligence
                'copy_enabled': True,  # Enable copy trading
                'copy_amount_sol': 0.05,  # Default 0.05 SOL per copy trade
                'total_trades': 0,
                'profitable_trades': 0,
                'win_rate': 0.0,
                'total_pnl': 0.0
            }
            await db.add_tracked_wallet(wallet_data)
            added_count += 1
            
            if i % 50 == 0:
                print(f"   Progress: {i}/{len(new_wallets)} wallets added...")
        
        except Exception as e:
            failed_count += 1
            if failed_count <= 5:  # Only show first 5 errors
                print(f"   Failed to add {wallet[:8]}...: {e}")
    
    # Final stats
    print(f"\n{'='*60}")
    print(f"WALLET IMPORT COMPLETE!")
    print(f"{'='*60}")
    print(f"Successfully added: {added_count}")
    print(f"Failed: {failed_count}")
    print(f"Total now tracked: {len(existing_addresses) + added_count}")
    print(f"{'='*60}")
    
    # Verify
    final_tracked = await db.get_tracked_wallets(user_id=1)
    print(f"Verified: {len(final_tracked)} wallets in database")
    
    await db.dispose()
    return True

async def main():
    try:
        result = await check_and_add_wallets()
        return result
    except FileNotFoundError:
        print("\nError: unique_wallets_list.txt not found!")
        print("Make sure you're in the project root directory.")
        return False
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = asyncio.run(main())
    
    if result:
        print("\nAll wallets are now being tracked!")
        print("\nNext steps:")
        print("  1. Start the bot: python scripts/run_bot.py")
        print("  2. Use /autostart in Telegram to begin auto-trading")
        print("  3. Monitor with: python scripts/monitor_wallet_scanning_24hr.py")
    else:
        print("\nImport failed - check errors above")
