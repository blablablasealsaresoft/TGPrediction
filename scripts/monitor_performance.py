"""
Real-time performance monitoring dashboard
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta
sys.path.insert(0, 'C:/Users/ckthe/sol')

from src.modules.database import DatabaseManager
from solana.rpc.async_api import AsyncClient
from solders.pubkey import Pubkey
from dotenv import load_dotenv

load_dotenv()

async def monitor_performance():
    """Monitor bot performance in real-time"""
    
    print("="*70)
    print("TRADING BOT - LIVE PERFORMANCE MONITOR")
    print("="*70)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("Press Ctrl+C to stop")
    print("="*70)
    
    # Initialize
    db = DatabaseManager("sqlite+aiosqlite:///trading_bot.db")
    rpc_url = os.getenv('SOLANA_RPC_URL', 'https://api.mainnet-beta.solana.com')
    client = AsyncClient(rpc_url)
    
    user_id = 8059844643
    wallet_address = "mDSm6bqKdKc8ARbsdAkkHKzDzAqERuFxMChiGmuUDaR"
    
    try:
        iteration = 0
        while True:
            iteration += 1
            os.system('cls' if os.name == 'nt' else 'clear')
            
            print("="*70)
            print(f"LIVE PERFORMANCE MONITOR - Update #{iteration}")
            print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("="*70)
            
            # Get wallet balance
            try:
                pubkey = Pubkey.from_string(wallet_address)
                balance_response = await client.get_balance(pubkey)
                balance_sol = balance_response.value / 1_000_000_000
                
                print(f"\n[WALLET]")
                print(f"  Balance: {balance_sol:.6f} SOL")
                print(f"  Address: {wallet_address[:10]}...{wallet_address[-6:]}")
            except Exception as e:
                print(f"\n[WALLET] Error: {e}")
            
            # Get tracked wallets
            tracked = await db.get_tracked_wallets(user_id)
            print(f"\n[WALLET TRACKING]")
            print(f"  Total Wallets: {len(tracked)}")
            print(f"  Top 5 by score:")
            for wallet in sorted(tracked, key=lambda w: w.score or 0, reverse=True)[:5]:
                print(f"    • {wallet.wallet_address[:8]}... - {wallet.label[:30]} (Score: {wallet.score:.0f})")
            
            # Check bot process
            print(f"\n[BOT STATUS]")
            import subprocess
            try:
                result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq python.exe', '/FO', 'CSV'], 
                                      capture_output=True, text=True)
                if 'python.exe' in result.stdout:
                    process_count = len([l for l in result.stdout.strip().split('\n')[1:] if l.strip()])
                    print(f"  Status: [OK] Running")
                    print(f"  Processes: {process_count}")
                else:
                    print(f"  Status: [X] NOT RUNNING!")
            except:
                print(f"  Status: Unknown")
            
            # Recent activity from logs
            print(f"\n[RECENT ACTIVITY (Last 10 log entries)]")
            try:
                with open('logs/trading_bot.log', 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                    recent = [l.strip() for l in lines[-10:] if l.strip()]
                    
                    if recent:
                        for line in recent:
                            # Shorten long lines
                            display_line = line[:100] + '...' if len(line) > 100 else line
                            print(f"  {display_line}")
                    else:
                        print(f"  No recent activity")
            except:
                print(f"  Log file empty or not found")
            
            # Key metrics
            print(f"\n[SETTINGS]")
            print(f"  Buy Amount: 0.05 SOL")
            print(f"  Max Daily Loss: 0.15 SOL")
            print(f"  Max Trades/Day: 10")
            print(f"  Max Snipes/Day: 3")
            print(f"  Stop Loss: -15%")
            print(f"  Take Profit: +50%")
            
            print(f"\n{'='*70}")
            print(f"Next update in 10 seconds... (Ctrl+C to stop)")
            print(f"{'='*70}")
            
            await asyncio.sleep(10)
    
    except KeyboardInterrupt:
        print(f"\n\n{'='*70}")
        print(f"Monitor stopped")
        print(f"{'='*70}")
    
    finally:
        await client.close()

if __name__ == '__main__':
    asyncio.run(monitor_performance())

