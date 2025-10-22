"""
Discover affiliated/side wallets for your tracked wallets
Uses FREE public Solana RPC - NO PAID API REQUIRED!
"""

import asyncio
import sys
sys.path.insert(0, 'C:/Users/ckthe/sol')

from src.modules.affiliated_wallet_detector import AffiliatedWalletDetector
from src.modules.database import DatabaseManager
from solana.rpc.async_api import AsyncClient

async def main():
    print("=" * 70)
    print("AFFILIATED WALLET DISCOVERY")
    print("Using FREE Public Solana RPC - No API Key Required!")
    print("=" * 70)
    
    # Your tracked wallets
    main_wallets = [
        "3S8TjEDc2iiYivfjegWXi5kRuxKS5BEDiyeK2PjcUdqn",
        "9nNLzq7ccL4nvDAMVP7aPoUv8Ti3qXZqnNaee8Qp57WE",
    ]
    
    user_id = 8059844643
    
    # Initialize
    client = AsyncClient("https://api.mainnet-beta.solana.com")
    db = DatabaseManager("sqlite+aiosqlite:///trading_bot.db")
    detector = AffiliatedWalletDetector(client)
    
    print(f"\nAnalyzing {len(main_wallets)} main wallets...")
    print("This may take 30-60 seconds...\n")
    
    # Auto-discover and add affiliated wallets
    added_count = await detector.auto_discover_and_track(
        main_wallets,
        db,
        user_id,
        max_to_add=5  # Add up to 5 affiliated wallets per main wallet
    )
    
    # Show results
    print(f"\n" + "=" * 70)
    print(f"RESULTS")
    print(f"=" * 70)
    
    print(f"\n[SUCCESS] Auto-discovered and added {added_count} affiliated wallets!")
    
    # Show all tracked wallets
    all_tracked = await db.get_tracked_wallets(user_id)
    print(f"\nTotal wallets now tracked: {len(all_tracked)}")
    
    for wallet in all_tracked:
        print(f"  • {wallet.wallet_address[:8]}...{wallet.wallet_address[-6:]} - {wallet.label}")
    
    print(f"\n" + "=" * 70)
    print(f"[INFO] Detection Methods Used (100% FREE):")
    print(f"       - Transfer pattern analysis")
    print(f"       - Fund flow tracking")
    print(f"       - Transaction history correlation")
    print(f"\n[NEXT] Restart bot and run /autostart to activate new wallets!")
    print(f"=" * 70)
    
    await client.close()

if __name__ == '__main__':
    asyncio.run(main())

