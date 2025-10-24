#!/usr/bin/env python3
"""
Quick bot status check
"""

import asyncio
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.config import get_config
from src.modules.database import DatabaseManager, UserWallet
from sqlalchemy import select

async def quick_status_check():
    """Quick status check"""
    
    print("QUICK BOT STATUS CHECK")
    print("="*40)
    
    # Check if bot process is running
    import subprocess
    result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq python.exe'], 
                          capture_output=True, text=True)
    
    if 'python.exe' in result.stdout:
        print("+ Bot process is running")
    else:
        print("- Bot process not running")
        return
    
    # Check database wallet
    config = get_config()
    admin_id = config.admin_chat_id
    
    db = DatabaseManager(config.database_url)
    await db.init_db()
    
    async with db.async_session() as session:
        result = await session.execute(
            select(UserWallet).where(UserWallet.user_id == admin_id)
        )
        wallet = result.scalar_one_or_none()
        
        if wallet:
            print(f"+ Database wallet: {wallet.public_key}")
            
            # Check balance
            from solana.rpc.async_api import AsyncClient
            from solders.pubkey import Pubkey
            
            client = AsyncClient(config.solana_rpc_url)
            try:
                pubkey = Pubkey.from_string(wallet.public_key)
                balance_response = await client.get_balance(pubkey)
                balance_sol = balance_response.value / 1_000_000_000
                print(f"+ Balance: {balance_sol:.6f} SOL")
                
                if wallet.public_key == "mDSm6bqKdKc8ARbsdAkkHKzDzAqERuFxMChiGmuUDaR":
                    print("+ CORRECT WALLET RESTORED!")
                else:
                    print("- WRONG WALLET - bot may be creating new one")
                    
            except Exception as e:
                print(f"- Error checking balance: {e}")
            finally:
                await client.close()
        else:
            print("- No wallet found in database")
    
    await db.dispose()
    
    print("\n" + "="*40)
    print("NEXT STEPS:")
    print("="*40)
    print("1. Test /wallet command in Telegram")
    print("2. If wrong wallet shown, restart bot")
    print("3. Send /autostart to begin trading")

if __name__ == "__main__":
    asyncio.run(quick_status_check())
