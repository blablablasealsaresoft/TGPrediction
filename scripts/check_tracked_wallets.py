"""
Check if wallets from unique_wallets_list.txt are tracked in database
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.modules.database import DatabaseManager

async def check_tracked_wallets():
    """Check how many wallets are tracked"""
    db = DatabaseManager()
    
    # Read wallets from file
    wallets_from_file = []
    with open('unique_wallets_list.txt', 'r') as f:
        for line in f:
            line = line.strip()
            # Extract wallet addresses (skip headers/numbers)
            if len(line) > 30 and not line.startswith('=') and not line.startswith('COMPREHENSIVE'):
                # Remove the number prefix
                parts = line.split('. ')
                if len(parts) > 1:
                    wallet = parts[1].strip()
                    if len(wallet) >= 32:  # Valid Solana address
                        wallets_from_file.append(wallet)
    
    print(f"\n📊 WALLET TRACKING STATUS")
    print("=" * 60)
    print(f"Wallets in unique_wallets_list.txt: {len(wallets_from_file)}")
    
    # Check database for user 1 (default test user)
    tracked_in_db = await db.get_tracked_wallets(user_id=1)
    
    print(f"Wallets tracked in database (user 1): {len(tracked_in_db)}")
    
    # Get tracked addresses
    tracked_addresses = set(w['wallet_address'] for w in tracked_in_db)
    file_addresses = set(wallets_from_file)
    
    # Find which are missing
    missing = file_addresses - tracked_addresses
    
    print(f"\n📈 Coverage: {len(tracked_addresses)}/{len(file_addresses)} ({len(tracked_addresses)/len(file_addresses)*100:.1f}%)")
    print(f"Missing from database: {len(missing)}")
    
    if missing:
        print(f"\n⚠️ {len(missing)} wallets need to be added!")
        print("\nFirst 10 missing wallets:")
        for wallet in list(missing)[:10]:
            print(f"  • {wallet}")
        
        return False, missing
    else:
        print("\n✅ ALL WALLETS ARE TRACKED!")
        return True, set()

async def main():
    all_tracked, missing = await check_tracked_wallets()
    
    if not all_tracked:
        print(f"\n{'='*60}")
        print("📝 TO ADD MISSING WALLETS:")
        print("=" * 60)
        print("Run: python scripts/add_all_unique_wallets.py")
        print("=" * 60)
    
    return all_tracked

if __name__ == "__main__":
    asyncio.run(main())

