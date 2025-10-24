#!/usr/bin/env python3
"""
Live Bot Monitoring Dashboard
"""

import asyncio
import os
import sys
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.config import get_config
from src.modules.database import DatabaseManager, UserWallet, TrackedWallet
from sqlalchemy import select

async def live_monitoring():
    """Live monitoring dashboard"""
    
    print("LIVE BOT MONITORING DASHBOARD")
    print("="*60)
    print("Press Ctrl+C to stop monitoring")
    print("="*60)
    
    config = get_config()
    admin_id = config.admin_chat_id
    
    db = DatabaseManager(config.database_url)
    await db.init_db()
    
    try:
        while True:
            # Clear screen (Windows)
            os.system('cls' if os.name == 'nt' else 'clear')
            
            print("LIVE BOT MONITORING DASHBOARD")
            print("="*60)
            print(f"Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
            print("="*60)
            
            # Check bot process
            import subprocess
            result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq python.exe'], 
                                  capture_output=True, text=True)
            
            if 'python.exe' in result.stdout:
                print("+ Bot Status: RUNNING")
            else:
                print("- Bot Status: STOPPED")
                break
            
            # Check wallet
            async with db.async_session() as session:
                result = await session.execute(
                    select(UserWallet).where(UserWallet.user_id == admin_id)
                )
                wallet = result.scalar_one_or_none()
                
                if wallet:
                    print(f"+ Wallet: {wallet.public_key}")
                    
                    # Check balance
                    from solana.rpc.async_api import AsyncClient
                    from solders.pubkey import Pubkey
                    
                    client = AsyncClient(config.solana_rpc_url)
                    try:
                        pubkey = Pubkey.from_string(wallet.public_key)
                        balance_response = await client.get_balance(pubkey)
                        balance_sol = balance_response.value / 1_000_000_000
                        print(f"+ Balance: {balance_sol:.6f} SOL")
                        
                        if balance_sol >= 0.01:
                            print("+ Trading Status: READY")
                        else:
                            print("- Trading Status: INSUFFICIENT FUNDS")
                            
                    except Exception as e:
                        print(f"- Balance Check Error: {e}")
                    finally:
                        await client.close()
                else:
                    print("- Wallet: NOT FOUND")
            
            # Check tracked wallets
            tracked_wallets = await db.get_tracked_wallets(user_id=1)
            print(f"+ Tracked Wallets: {len(tracked_wallets)}")
            
            print("\n" + "="*60)
            print("TELEGRAM COMMANDS TO TEST:")
            print("="*60)
            print("/wallet     - Check wallet address")
            print("/balance    - Check SOL balance")
            print("/autostart  - Start automated trading")
            print("/autostatus - Check trading status")
            print("/my_stats   - View performance")
            print("/positions  - Check open positions")
            print("/leaderboard - View top traders")
            
            print("\n" + "="*60)
            print("MONITORING REFRESHES EVERY 10 SECONDS")
            print("="*60)
            
            await asyncio.sleep(10)
            
    except KeyboardInterrupt:
        print("\n\nMonitoring stopped by user")
    finally:
        await db.dispose()

if __name__ == "__main__":
    asyncio.run(live_monitoring())
