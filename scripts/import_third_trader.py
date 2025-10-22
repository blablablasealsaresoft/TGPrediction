"""
Add third pro trader and affiliated wallets from CSV
"""

import asyncio
import csv
from collections import Counter
import sys
sys.path.insert(0, 'C:/Users/ckthe/sol')

from src.modules.database import DatabaseManager
from datetime import datetime

# Main wallet from CSV
MAIN_WALLET = "F4SkBcN7VoyA27dY96A3k9QzEMrFju7PwPY6tswRjmKX"

# Exclude these (protocols, DEXs, etc.)
EXCLUDE = {
    "u6PJ8DtQuPFnfmwHbGFULQ4u4EgjDiyYKjVEsynXq2w",  # Common destination
    "So11111111111111111111111111111111111111112",
    "5Q544fKrFoe6tsEbD7S8EmxGTJYAKtTVhAW5Q5pge4j1",
    "CB9VbuXPziRjvUMcrrekeK6V8KDrR9f7q2LaSkaFMFE",
    "GSSU8kxA4RJfhPz68NT6bHNkMRtoKKgQW28HEU94oi8t",
    "7ghUjHdUzFsFRU7nGpGJbs5ZktnrReEJsZGmcQLNECNs",
    "G2YxRa6wt1qePMwfJzdXZG62ej4qaTC7YURzuh2Lwd3t",
    "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
    MAIN_WALLET
}

async def main():
    print("="*70)
    print("ADDING THIRD PRO TRADER + AFFILIATED WALLETS")
    print("="*70)
    
    user_id = 8059844643
    db = DatabaseManager("sqlite+aiosqlite:///trading_bot.db")
    
    # Add main trader first
    print("\n[STEP 1] Adding main pro trader...")
    try:
        trader_data = {
            'user_id': user_id,
            'wallet_address': MAIN_WALLET,
            'label': "Pro Trader #3",
            'score': 80.0,  # Good score
            'total_trades': 0,
            'profitable_trades': 0,
            'win_rate': 0.0,
            'total_pnl': 0.0,
            'copy_enabled': True,
            'copy_amount_sol': 0.1,
            'added_at': datetime.utcnow(),
            'last_checked': datetime.utcnow()
        }
        
        await db.add_tracked_wallet(trader_data)
        print(f"[SUCCESS] Added Pro Trader #3")
        print(f"          Address: {MAIN_WALLET[:10]}...{MAIN_WALLET[-6:]}")
    
    except Exception as e:
        print(f"[SKIP] Pro Trader #3: {str(e)[:50]}")
    
    # Parse CSV for affiliated wallets
    print("\n[STEP 2] Parsing CSV for affiliated wallets...")
    
    csv_file = "export_transfer_F4SkBcN7VoyA27dY96A3k9QzEMrFju7PwPY6tswRjmKX_1761137805436.csv"
    
    wallets = Counter()
    
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                from_addr = row.get('From', '').strip()
                to_addr = row.get('To', '').strip()
                
                if from_addr and from_addr not in EXCLUDE and len(from_addr) > 32:
                    wallets[from_addr] += 1
                
                if to_addr and to_addr not in EXCLUDE and len(to_addr) > 32:
                    wallets[to_addr] += 1
        
        print(f"  Found {len(wallets)} unique wallets")
    
    except Exception as e:
        print(f"  Error: {e}")
        return
    
    # Get top wallets
    affiliated = [(w, c) for w, c in wallets.items() if c >= 2]
    affiliated.sort(key=lambda x: x[1], reverse=True)
    
    print(f"\n[STEP 3] Top affiliated wallets:")
    for i, (wallet, count) in enumerate(affiliated[:10], 1):
        print(f"  {i:2}. {wallet[:8]}...{wallet[-6:]} - {count} interactions")
    
    # Add top 5 to database
    print(f"\n[STEP 4] Adding top 5 to database...")
    added = 0
    
    for wallet_addr, count in affiliated[:5]:
        try:
            wallet_data = {
                'user_id': user_id,
                'wallet_address': wallet_addr,
                'label': f"Affiliated with Trader #3 ({count} int.)",
                'score': min(60.0 + (count * 3), 85.0),
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
            print(f"  [SUCCESS] {wallet_addr[:8]}...{wallet_addr[-6:]} (Score: {wallet_data['score']:.0f})")
            added += 1
        
        except Exception as e:
            print(f"  [SKIP] {wallet_addr[:8]}...: {str(e)[:30]}")
    
    # Show final count
    all_tracked = await db.get_tracked_wallets(user_id)
    
    print(f"\n{'='*70}")
    print(f"FINAL SUMMARY")
    print(f"{'='*70}")
    print(f"\nTotal Wallets Tracked: {len(all_tracked)}")
    print(f"  - 3 Main pro traders")
    print(f"  - {len(all_tracked) - 3} Affiliated wallets")
    
    print(f"\n[SUCCESS] Added 1 main trader + {added} affiliated wallets")
    print(f"[TOTAL] Now tracking {len(all_tracked)} wallets!")
    print(f"\n[NEXT] Restart bot and run /autostart in Telegram")
    print(f"[EXPECTED] 'Scanned {len(all_tracked)} top wallets for opportunities'")

if __name__ == '__main__':
    asyncio.run(main())

