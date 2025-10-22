"""
Add pro trader wallets to tracking system with database persistence
"""

import asyncio
import sys
sys.path.insert(0, 'C:/Users/ckthe/sol')

from src.modules.database import DatabaseManager
from datetime import datetime

# IMPORTANT: First two addresses are ETHEREUM (0x...), not Solana!
# Only adding the valid Solana addresses
SOLANA_WALLETS_TO_TRACK = [
    {
        'address': "3S8TjEDc2iiYivfjegWXi5kRuxKS5BEDiyeK2PjcUdqn",
        'label': "Pro Trader #1",
        'notes': "High-volume trader"
    },
    {
        'address': "9nNLzq7ccL4nvDAMVP7aPoUv8Ti3qXZqnNaee8Qp57WE",
        'label': "Pro Trader #2",
        'notes': "Successful track record"
    },
]

async def main():
    print("=" * 70)
    print("ADDING PRO TRADER WALLETS TO TRACKING SYSTEM")
    print("=" * 70)
    
    # Note about Ethereum addresses
    print("\n[WARNING] The first two addresses you provided are Ethereum addresses (0x...)")
    print("          Solana addresses use base58 encoding and don't start with 0x")
    print("          Only adding the 2 valid Solana addresses.\n")
    
    # Initialize database
    db = DatabaseManager("sqlite+aiosqlite:///trading_bot.db")
    
    # Your user ID (from logs)
    user_id = 8059844643
    
    print(f"Adding {len(SOLANA_WALLETS_TO_TRACK)} Solana wallets for user {user_id}...")
    
    added_count = 0
    for wallet in SOLANA_WALLETS_TO_TRACK:
        try:
            wallet_data = {
                'user_id': user_id,
                'wallet_address': wallet['address'],
                'label': wallet['label'],
                'score': 75.0,  # Good initial score (above threshold)
                'total_trades': 0,
                'profitable_trades': 0,
                'win_rate': 0.0,
                'total_pnl': 0.0,
                'copy_enabled': True,  # Enable copying from these wallets
                'copy_amount_sol': 0.1,  # Copy with 0.1 SOL per trade
                'added_at': datetime.utcnow(),
                'last_checked': datetime.utcnow()
            }
            
            result = await db.add_tracked_wallet(wallet_data)
            
            print(f"\n[SUCCESS] Added: {wallet['label']}")
            print(f"   Address: {wallet['address']}")
            print(f"   Database ID: {result.id}")
            
            added_count += 1
            
        except Exception as e:
            print(f"\n[ERROR] Failed to add {wallet['label']}: {e}")
    
    # Verify wallets in database
    print(f"\n" + "=" * 70)
    print(f"VERIFICATION")
    print(f"=" * 70)
    
    tracked = await db.get_tracked_wallets(user_id)
    print(f"\nTotal tracked wallets in database: {len(tracked)}")
    
    for wallet in tracked:
        print(f"  • {wallet.wallet_address[:8]}...{wallet.wallet_address[-6:]} - {wallet.label or 'No label'}")
    
    print(f"\n" + "=" * 70)
    print(f"SUCCESS! Added {added_count} wallets")
    print(f"=" * 70)
    print(f"\n[INFO] The automated trading bot will now:")
    print(f"       1. Scan these {len(tracked)} wallets every 10 seconds")
    print(f"       2. Detect when they buy tokens")
    print(f"       3. Copy their trades if confidence is high")
    print(f"       4. Auto-manage positions with stop loss/take profit")
    
    print(f"\n[NEXT STEPS]")
    print(f"       1. Restart the bot to load these wallets")
    print(f"       2. Run /autostart in Telegram")
    print(f"       3. Watch the 'Scanned X top wallets' messages increase from 0!")

if __name__ == '__main__':
    asyncio.run(main())

