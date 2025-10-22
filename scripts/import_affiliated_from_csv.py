"""
Import affiliated wallets from transaction CSV exports
Analyzes the From (E) and To (F) columns to find frequently interacting wallets
"""

import asyncio
import csv
from collections import Counter
import sys
sys.path.insert(0, 'C:/Users/ckthe/sol')

from src.modules.database import DatabaseManager
from datetime import datetime

# Main wallets (exclude these)
MAIN_WALLETS = {
    "3S8TjEDc2iiYivfjegWXi5kRuxKS5BEDiyeK2PjcUdqn",
    "9nNLzq7ccL4nvDAMVP7aPoUv8Ti3qXZqnNaee8Qp57WE"
}

# Common DEX/protocol addresses to exclude
EXCLUDE_ADDRESSES = {
    "5Q544fKrFoe6tsEbD7S8EmxGTJYAKtTVhAW5Q5pge4j1",  # Raydium
    "GpMZbSM2GgvTKHJirzeGfMFoaZ8UR2X7F4v8vHTvxFbL",  # Jupiter
    "WLHv2UAZm6z4KyaaELi5pjdbJh6RESMva1Rnn8pJVVh",  # Common swap pool
    "332gnyVz9JhxhBgNp3oph9xqUUJdnXmu1C5BTjScoyqe",  # Common swap pool
    "5MjAYB6am8yNR675vmRmiEUuiySjQA4GtHHyf7Nb1ifi",  # LP pool
    "KW5WKszirTFHQSWSZ1Fm7r1WtBusJyo4ytviqHhAx3X",   # LP pool
    "Caf1AhvmhGtJw8Az7m36MDAx2zwMZvmotKE4dAh5YpJN",  # LP pool
    "So11111111111111111111111111111111111111112",   # SOL token address
    "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # USDC
    "Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB",  # USDT
    "MaestroUL88UBnZr3wfoN7hqmNWFi3ZYCGqZoJJHE36",  # Maestro bot
    "TEMPaMeCRFAS9EKF53Jd6KpHxgL47uWLcpFArU1Fanq",  # Some protocol
    "EgGRhhJXcviuChGbi33q2GKh3fSJQF9xZ7wp7rwnp3Mi",  # Account creation
    "nextBLoCkPMgmG8ZgJtABeScP35qLa2AMCNKntAP7Xc",   # Protocol
    "6MeKUNKtz1muJCB2GsE2EHrwkSdpMHw5KF7kh1wtEnkp",  # Created account
    # Add more if needed
}

async def parse_csv_and_find_affiliates(csv_files, min_interactions=3):
    """Parse CSV files and find frequently interacting wallets"""
    
    all_wallets = Counter()  # wallet -> interaction count
    
    for csv_file in csv_files:
        print(f"\nParsing: {csv_file}")
        
        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                for row in reader:
                    # Get From (column E) and To (column F)
                    from_addr = row.get('From', '').strip()
                    to_addr = row.get('To', '').strip()
                    
                    # Count interactions with non-protocol wallets
                    if from_addr and from_addr not in MAIN_WALLETS and from_addr not in EXCLUDE_ADDRESSES:
                        if len(from_addr) > 32:  # Valid Solana address length
                            all_wallets[from_addr] += 1
                    
                    if to_addr and to_addr not in MAIN_WALLETS and to_addr not in EXCLUDE_ADDRESSES:
                        if len(to_addr) > 32:  # Valid Solana address length
                            all_wallets[to_addr] += 1
            
            print(f"  Found {len(all_wallets)} unique wallets")
        
        except Exception as e:
            print(f"  Error parsing file: {e}")
    
    # Filter by minimum interactions
    affiliated = [(wallet, count) for wallet, count in all_wallets.items() if count >= min_interactions]
    affiliated.sort(key=lambda x: x[1], reverse=True)  # Sort by interaction count
    
    return affiliated

async def add_to_database(affiliated_wallets, user_id=8059844643, max_to_add=10):
    """Add top affiliated wallets to database"""
    
    db = DatabaseManager("sqlite+aiosqlite:///trading_bot.db")
    
    print(f"\n{'='*70}")
    print(f"ADDING TOP {max_to_add} AFFILIATED WALLETS")
    print(f"{'='*70}")
    
    added_count = 0
    
    for wallet_addr, interaction_count in affiliated_wallets[:max_to_add]:
        try:
            wallet_data = {
                'user_id': user_id,
                'wallet_address': wallet_addr,
                'label': f"Affiliated ({interaction_count} interactions)",
                'score': min(50.0 + (interaction_count * 2), 85.0),  # Higher score for more interactions
                'total_trades': 0,
                'profitable_trades': 0,
                'win_rate': 0.0,
                'total_pnl': 0.0,
                'copy_enabled': True,
                'copy_amount_sol': 0.1,
                'added_at': datetime.utcnow(),
                'last_checked': datetime.utcnow()
            }
            
            await db.add_tracked_wallet(wallet_data)
            
            print(f"\n[SUCCESS] Added: {wallet_addr[:8]}...{wallet_addr[-6:]}")
            print(f"          Interactions: {interaction_count}")
            print(f"          Score: {wallet_data['score']:.0f}")
            
            added_count += 1
        
        except Exception as e:
            # Might already exist or other error
            print(f"\n[SKIP] {wallet_addr[:8]}...{wallet_addr[-6:]}: {str(e)[:50]}")
    
    # Show all tracked wallets
    all_tracked = await db.get_tracked_wallets(user_id)
    
    print(f"\n{'='*70}")
    print(f"FINAL WALLET COUNT: {len(all_tracked)}")
    print(f"{'='*70}")
    
    for wallet in all_tracked:
        print(f"  • {wallet.wallet_address[:8]}...{wallet.wallet_address[-6:]} - {wallet.label}")
    
    print(f"\n[SUCCESS] Added {added_count} new affiliated wallets!")
    print(f"[TOTAL] Now tracking {len(all_tracked)} wallets")
    
    return added_count

async def main():
    print("="*70)
    print("IMPORTING AFFILIATED WALLETS FROM CSV TRANSACTION DATA")
    print("="*70)
    
    # CSV file paths
    csv_files = [
        "export_transfer_3S8TjEDc2iiYivfjegWXi5kRuxKS5BEDiyeK2PjcUdqn_1761137302328.csv",
        "export_transfer_9nNLzq7ccL4nvDAMVP7aPoUv8Ti3qXZqnNaee8Qp57WE_1761137461582.csv"
    ]
    
    # Parse and find affiliated wallets
    affiliated = await parse_csv_and_find_affiliates(csv_files, min_interactions=3)
    
    print(f"\n{'='*70}")
    print(f"TOP AFFILIATED WALLETS (by interaction count):")
    print(f"{'='*70}")
    
    for i, (wallet, count) in enumerate(affiliated[:15], 1):
        print(f"{i:2}. {wallet[:8]}...{wallet[-6:]} - {count:3} interactions")
    
    # Add to database
    if affiliated:
        added = await add_to_database(affiliated, max_to_add=10)
        
        print(f"\n{'='*70}")
        print(f"[NEXT STEP] Restart bot and run /autostart in Telegram")
        print(f"[EXPECTED] 'Scanned {2 + added} top wallets for opportunities'")
        print(f"{'='*70}")
    else:
        print("\n[INFO] No affiliated wallets found (all were protocol addresses)")

if __name__ == '__main__':
    asyncio.run(main())

