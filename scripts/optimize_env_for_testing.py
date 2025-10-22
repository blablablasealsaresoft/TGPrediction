"""
Optimize .env file for safe testing with small amounts (0.2 SOL balance)
"""

def optimize_env():
    print("="*70)
    print("OPTIMIZING .ENV FOR SAFE TESTING")
    print("="*70)
    
    # Read current .env
    with open('.env', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Settings to update
    updates = {
        'DEFAULT_BUY_AMOUNT': '0.05',  # REDUCED from 0.1 SOL
        'SNIPE_AMOUNT_SOL': '0.05',     # REDUCED from 0.5 SOL
        'MAX_POSITION_SIZE_SOL': '0.5', # REDUCED from 10.0 SOL
        'AUTO_TRADE_DAILY_LIMIT_SOL': '1.0',  # REDUCED from 100.0 SOL
        'MAX_DAILY_LOSS_SOL': '0.15',   # REDUCED from 50.0 SOL (75% of balance protected)
        'SNIPE_MAX_DAILY': '3',         # REDUCED from 10
        'AUTO_TRADE_MAX_DAILY_TRADES': '10',  # REDUCED from 50
        'MIN_LIQUIDITY_USD': '2000.0',  # REDUCED from 5000.0
        'SNIPE_MIN_LIQUIDITY_SOL': '2', # REDUCED from 10
        'MIN_WALLET_SCORE': '65.0',     # REDUCED from 70.0 (catch more wallets)
    }
    
    # Update lines
    new_lines = []
    updated = set()
    
    for line in lines:
        updated_line = line
        
        for key, value in updates.items():
            if line.startswith(f'{key}='):
                old_value = line.split('=', 1)[1].strip()
                updated_line = f'{key}={value}\n'
                print(f"[UPDATE] {key}: {old_value} -> {value}")
                updated.add(key)
                break
        
        new_lines.append(updated_line)
    
    # Add missing settings
    for key, value in updates.items():
        if key not in updated:
            new_lines.append(f'\n# Added for testing\n{key}={value}\n')
            print(f"[ADD] {key}={value}")
    
    # Write updated .env
    with open('.env', 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    
    print(f"\n{'='*70}")
    print(f"OPTIMIZATION COMPLETE")
    print(f"{'='*70}")
    print(f"\n[SAFE FOR 0.2 SOL BALANCE]")
    print(f"  • Buy amount: 0.05 SOL (can do 4 trades)")
    print(f"  • Snipe amount: 0.05 SOL")
    print(f"  • Daily limit: 1.0 SOL")
    print(f"  • Max daily loss: 0.15 SOL (75% protected)")
    print(f"  • Max trades: 10/day")
    print(f"  • Max snipes: 3/day")
    print(f"\n[PROTECTION]")
    print(f"  • Stop loss: -15%")
    print(f"  • Take profit: +50%")
    print(f"  • Trailing stop: 10%")
    print(f"  • Min liquidity: $2,000")
    print(f"  • AI confidence: 75%")
    print(f"\n[READY] Restart bot to apply new settings!")

if __name__ == '__main__':
    optimize_env()

