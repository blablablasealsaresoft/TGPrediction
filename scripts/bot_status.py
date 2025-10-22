"""
Quick Bot Status Check
Run this anytime to see current configuration and status
"""

import asyncio
import os
from dotenv import load_dotenv
load_dotenv()

import sys
sys.path.insert(0, 'C:/Users/ckthe/sol')

from src.modules.database import DatabaseManager
from solana.rpc.async_api import AsyncClient
from solders.pubkey import Pubkey

async def main():
    print("=" * 70)
    print("SOLANA TRADING BOT - STATUS CHECK")
    print("=" * 70)
    
    # Bot configuration
    print("\n[BOT CONFIGURATION]")
    print(f"  Helius API: {'[OK] Configured' if os.getenv('HELIUS_API_KEY') else '[X] Not configured'}")
    print(f"  Twitter API: {'[OK] Configured' if os.getenv('TWITTER_BEARER_TOKEN') else '[X] Not configured'}")
    print(f"  Reddit API: {'[OK] Configured' if os.getenv('REDDIT_CLIENT_ID') else '[X] Not configured'}")
    print(f"  Discord Bot: {'[OK] Configured' if os.getenv('DISCORD_TOKEN') else '[X] Not configured'}")
    print(f"  Wallet Encryption: {'[OK] Configured' if os.getenv('WALLET_ENCRYPTION_KEY') else '[X] Not configured'}")
    
    # Database wallets
    print("\n[TRACKED WALLETS]")
    db = DatabaseManager("sqlite+aiosqlite:///trading_bot.db")
    user_id = 8059844643
    
    tracked = await db.get_tracked_wallets(user_id)
    print(f"  Total Tracked: {len(tracked)}")
    for wallet in tracked:
        print(f"    • {wallet.wallet_address[:10]}...{wallet.wallet_address[-6:]} - {wallet.label} (Score: {wallet.score:.0f})")
    
    # User wallet
    print("\n[YOUR WALLET]")
    rpc_url = os.getenv('SOLANA_RPC_URL', 'https://api.mainnet-beta.solana.com')
    client = AsyncClient(rpc_url)
    
    wallet_address = "mDSm6bqKdKc8ARbsdAkkHKzDzAqERuFxMChiGmuUDaR"
    try:
        pubkey = Pubkey.from_string(wallet_address)
        balance_response = await client.get_balance(pubkey)
        balance_sol = balance_response.value / 1_000_000_000
        print(f"  Address: {wallet_address}")
        print(f"  Balance: {balance_sol:.6f} SOL")
        print(f"  RPC: {'Helius' if 'helius' in rpc_url else 'Public'}")
    except Exception as e:
        print(f"  [ERROR] Could not check balance: {e}")
    
    await client.close()
    
    # Bot process
    print("\n[BOT PROCESS]")
    import subprocess
    try:
        result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq python.exe', '/FO', 'CSV'], 
                              capture_output=True, text=True)
        if 'python.exe' in result.stdout:
            print(f"  Status: [OK] Running")
            lines = result.stdout.strip().split('\n')
            if len(lines) > 1:
                # Count Python processes
                process_count = len([l for l in lines[1:] if l.strip()])
                print(f"  Processes: {process_count}")
        else:
            print(f"  Status: [X] Not running")
    except:
        print(f"  Status: Unknown")
    
    # Sniper settings
    print("\n[SNIPER SETTINGS]")
    print(f"  Min Liquidity: $2,000")
    print(f"  Min AI Confidence: 65%")
    print(f"  Detection Window: 2 hours")
    print(f"  Check Frequency: Every 10 seconds")
    
    # Auto-sell settings
    print("\n[AUTO-SELL SETTINGS]")
    print(f"  Stop Loss: -15%")
    print(f"  Take Profit: +50%")
    print(f"  Trailing Stop: 10% from peak")
    
    print("\n" + "=" * 70)
    print("[NEXT STEPS]")
    print("  1. Run /autostart in Telegram (if not already running)")
    print("  2. Run /snipe to verify sniper is enabled")
    print("  3. Run /wallet to check balance")
    print("=" * 70)

if __name__ == '__main__':
    asyncio.run(main())

