"""
Check and restore user's wallet from database
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from solana.rpc.async_api import AsyncClient
from solders.pubkey import Pubkey
from sqlalchemy import select
from src.modules.database import DatabaseManager, UserWallet

async def main():
    admin_id = int(os.getenv('ADMIN_CHAT_ID'))
    rpc_url = os.getenv('SOLANA_RPC_URL')
    
    db = DatabaseManager()
    client = AsyncClient(rpc_url)
    
    print(f"\n🔍 Searching for wallets for user {admin_id}...")
    print("="*60)
    
    # Check all wallets in database
    async with db.async_session() as session:
        result = await session.execute(select(UserWallet).where(UserWallet.user_id == admin_id))
        wallets = result.scalars().all()
    
    print(f"\nFound {len(wallets)} wallet(s) in database:\n")
    
    for i, wallet in enumerate(wallets, 1):
        # Check balance
        try:
            pubkey = Pubkey.from_string(wallet.public_key)
            response = await client.get_balance(pubkey)
            balance_sol = response.value / 1e9
        except:
            balance_sol = 0
        
        print(f"{i}. Address: {wallet.public_key}")
        print(f"   Balance: {balance_sol:.6f} SOL")
        print(f"   Created: {wallet.created_at}")
        print()
    
    # Check for the old wallet
    old_wallet_address = "mDSm6bqKdKc8ARbsdAkkHKzDzAqERuFxMChiGmuUDaR"
    
    found_old = False
    for wallet in wallets:
        if wallet.public_key == old_wallet_address:
            found_old = True
            print(f"✅ FOUND YOUR OLD WALLET!")
            print(f"   Address: {old_wallet_address}")
            
            # Check its balance
            try:
                pubkey = Pubkey.from_string(old_wallet_address)
                response = await client.get_balance(pubkey)
                balance_sol = response.value / 1e9
                print(f"   Balance: {balance_sol:.6f} SOL")
                
                if balance_sol > 0:
                    print(f"\n🎉 Your wallet still has {balance_sol:.6f} SOL!")
                else:
                    print(f"\n⚠️ Wallet has 0 SOL now")
            except Exception as e:
                print(f"   Error checking balance: {e}")
    
    if not found_old:
        print(f"❌ Old wallet ({old_wallet_address}) NOT in database")
        print(f"\nPossible reasons:")
        print(f"  1. Database was reset")
        print(f"  2. Wallet was deleted")
        print(f"  3. Different user ID")
        
        # Check if it exists on-chain
        print(f"\n🔍 Checking if wallet exists on-chain...")
        try:
            pubkey = Pubkey.from_string(old_wallet_address)
            response = await client.get_balance(pubkey)
            balance_sol = response.value / 1e9
            print(f"✅ Wallet exists on-chain!")
            print(f"   Balance: {balance_sol:.6f} SOL")
            
            if balance_sol > 0:
                print(f"\n💡 Your 0.2 SOL is still there!")
                print(f"   But you need the private key to access it")
                print(f"\nDo you have the private key for this wallet?")
        except Exception as e:
            print(f"❌ Could not check wallet: {e}")
    
    await client.close()

if __name__ == "__main__":
    asyncio.run(main())

