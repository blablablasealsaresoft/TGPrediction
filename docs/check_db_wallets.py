#!/usr/bin/env python3
"""
Check database for old wallet
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from solana.rpc.async_api import AsyncClient
from solders.pubkey import Pubkey
from sqlalchemy import select
from src.modules.database import DatabaseManager, UserWallet
from src.config import get_config

async def check_database_for_wallets():
    """Check database for wallets"""
    print("\nDATABASE WALLET CHECK")
    print("=" * 50)
    
    config = get_config()
    db = DatabaseManager(config.database_url)
    await db.init_db()
    
    client = AsyncClient(config.solana_rpc_url)
    
    admin_id = config.admin_chat_id
    
    print(f"Searching for wallets for user {admin_id}...")
    
    # Check all wallets in database
    async with db.async_session() as session:
        result = await session.execute(select(UserWallet).where(UserWallet.user_id == admin_id))
        wallets = result.scalars().all()
    
    print(f"Found {len(wallets)} wallet(s) in database:")
    
    old_wallet_address = "mDSm6bqKdKc8ARbsdAkkHKzDzAqERuFxMChiGmuUDaR"
    found_old = False
    
    for i, wallet in enumerate(wallets, 1):
        # Check balance
        try:
            pubkey = Pubkey.from_string(wallet.public_key)
            response = await client.get_balance(pubkey)
            balance_sol = response.value / 1e9
        except:
            balance_sol = 0
        
        print(f"\n{i}. Address: {wallet.public_key}")
        print(f"   Balance: {balance_sol:.6f} SOL")
        print(f"   Created: {wallet.created_at}")
        
        if wallet.public_key == old_wallet_address:
            found_old = True
            print(f"   *** THIS IS YOUR OLD WALLET! ***")
    
    if not found_old:
        print(f"\nOld wallet ({old_wallet_address}) NOT in database")
        
        # Check if it exists on-chain
        print(f"\nChecking if wallet exists on-chain...")
        try:
            pubkey = Pubkey.from_string(old_wallet_address)
            response = await client.get_balance(pubkey)
            balance_sol = response.value / 1e9
            print(f"Wallet exists on-chain!")
            print(f"Balance: {balance_sol:.6f} SOL")
            
            if balance_sol > 0:
                print(f"\nYour 0.2 SOL is still there!")
                print(f"But you need the private key to access it")
        except Exception as e:
            print(f"Could not check wallet: {e}")
    
    await client.close()
    await db.dispose()

async def main():
    print("WALLET DATABASE CHECK")
    print("=" * 60)
    
    await check_database_for_wallets()

if __name__ == "__main__":
    asyncio.run(main())
