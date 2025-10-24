#!/usr/bin/env python3
"""
Debug wallet issue - check all wallets for admin user
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

async def debug_wallet_issue():
    """Debug why bot shows different wallet"""
    
    print("DEBUGGING WALLET ISSUE")
    print("="*60)
    
    config = get_config()
    admin_id = config.admin_chat_id
    
    print(f"Admin Chat ID: {admin_id}")
    
    db = DatabaseManager(config.database_url)
    await db.init_db()
    
    # Check ALL wallets for admin user
    async with db.async_session() as session:
        result = await session.execute(
            select(UserWallet).where(UserWallet.user_id == admin_id)
        )
        wallets = result.scalars().all()
        
        print(f"\nFound {len(wallets)} wallet(s) for admin user:")
        
        for i, wallet in enumerate(wallets, 1):
            print(f"\n{i}. Address: {wallet.public_key}")
            print(f"   Created: {wallet.created_at}")
            print(f"   Last Used: {wallet.last_used}")
            print(f"   Username: {wallet.telegram_username}")
            
            # Check balance
            from solana.rpc.async_api import AsyncClient
            from solders.pubkey import Pubkey
            
            client = AsyncClient(config.solana_rpc_url)
            try:
                pubkey = Pubkey.from_string(wallet.public_key)
                balance_response = await client.get_balance(pubkey)
                balance_sol = balance_response.value / 1_000_000_000
                print(f"   Balance: {balance_sol:.6f} SOL")
                
                if wallet.public_key == "mDSm6bqKdKc8ARbsdAkkHKzDzAqERuFxMChiGmuUDaR":
                    print("   *** THIS IS THE CORRECT WALLET WITH 0.2 SOL ***")
                elif wallet.public_key == "E4QHJq2iQ18a8PqLfL7hoNLgu4hk4H7G9TZ4Xq3DJJQR":
                    print("   *** THIS IS THE WRONG WALLET SHOWN BY BOT ***")
                    
            except Exception as e:
                print(f"   Error checking balance: {e}")
            finally:
                await client.close()
    
    await db.dispose()
    
    print("\n" + "="*60)
    print("ANALYSIS:")
    print("="*60)
    
    if len(wallets) > 1:
        print("PROBLEM: Multiple wallets found for admin user!")
        print("SOLUTION: Delete the wrong wallet, keep only the correct one")
        
        # Delete the wrong wallet
        async with db.async_session() as session:
            wrong_wallet = await session.execute(
                select(UserWallet).where(
                    UserWallet.user_id == admin_id,
                    UserWallet.public_key == "E4QHJq2iQ18a8PqLfL7hoNLgu4hk4H7G9TZ4Xq3DJJQR"
                )
            )
            wrong_wallet_obj = wrong_wallet.scalar_one_or_none()
            
            if wrong_wallet_obj:
                await session.delete(wrong_wallet_obj)
                await session.commit()
                print("+ Deleted wrong wallet: E4QHJq2iQ18a8PqLfL7hoNLgu4hk4H7G9TZ4Xq3DJJQR")
            else:
                print("- Wrong wallet not found in database")
        
        await db.dispose()
        
    else:
        print("Only one wallet found - this should be correct")
    
    print("\nNext step: Restart the bot to use the correct wallet")

if __name__ == "__main__":
    asyncio.run(debug_wallet_issue())
