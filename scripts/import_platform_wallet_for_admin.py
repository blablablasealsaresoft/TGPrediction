"""
Import platform wallet for admin user
Allows admin to use the funded wallet from WALLET_PRIVATE_KEY instead of a new wallet
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

load_dotenv()

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from solana.rpc.async_api import AsyncClient
from solders.keypair import Keypair
from src.modules.database import DatabaseManager
from src.modules.wallet_manager import UserWalletManager

async def import_platform_wallet():
    """Import platform wallet for admin user"""
    
    print("\n🔐 IMPORT PLATFORM WALLET FOR ADMIN")
    print("="*60)
    
    # Get credentials from .env
    admin_user_id = int(os.getenv('ADMIN_CHAT_ID', '0'))
    wallet_private_key = os.getenv('WALLET_PRIVATE_KEY')
    rpc_url = os.getenv('SOLANA_RPC_URL')
    
    if not admin_user_id:
        print("❌ ADMIN_CHAT_ID not set in .env")
        return False
    
    if not wallet_private_key:
        print("❌ WALLET_PRIVATE_KEY not set in .env")
        return False
    
    print(f"✅ Admin User ID: {admin_user_id}")
    print(f"✅ RPC URL: {rpc_url[:50]}...")
    
    # Parse keypair
    try:
        keypair = Keypair.from_base58_string(wallet_private_key)
        public_key = str(keypair.pubkey())
        print(f"✅ Platform Wallet: {public_key}")
    except Exception as e:
        print(f"❌ Invalid WALLET_PRIVATE_KEY: {e}")
        return False
    
    # Initialize
    client = AsyncClient(rpc_url)
    db = DatabaseManager()
    wallet_manager = UserWalletManager(db, client)
    
    # Check balance
    try:
        response = await client.get_balance(keypair.pubkey())
        balance_lamports = response.value
        balance_sol = balance_lamports / 1e9
        print(f"✅ Current Balance: {balance_sol:.6f} SOL")
    except Exception as e:
        print(f"⚠️ Could not check balance: {e}")
        balance_sol = 0
    
    # Import wallet for admin user
    print(f"\n🔄 Importing wallet for user {admin_user_id}...")
    
    try:
        # Check if user already has a wallet
        existing_address = await wallet_manager.get_user_wallet_address(admin_user_id)
        
        if existing_address:
            print(f"\n⚠️ User already has wallet: {existing_address}")
            response = input("Replace with platform wallet? (yes/no): ")
            
            if response.lower() != 'yes':
                print("❌ Import cancelled")
                await client.close()
                return False
            
            # Delete existing wallet
            print(f"🗑️ Removing old wallet...")
            await wallet_manager._delete_user_wallet(admin_user_id)
        
        # Import the platform wallet
        encrypted_key = wallet_manager.encryption.encrypt(wallet_private_key.encode())
        
        await wallet_manager._save_wallet_to_db(
            user_id=admin_user_id,
            public_key=public_key,
            encrypted_private_key=encrypted_key
        )
        
        print(f"\n✅ WALLET IMPORTED SUCCESSFULLY!")
        print(f"="*60)
        print(f"User ID: {admin_user_id}")
        print(f"Wallet: {public_key}")
        print(f"Balance: {balance_sol:.6f} SOL")
        print(f"="*60)
        
        print(f"\n✅ Now when you use the bot, it will use THIS wallet!")
        print(f"\nTest it:")
        print(f"  1. Send /start to your bot")
        print(f"  2. Send /wallet")
        print(f"  3. Should show: {public_key}")
        print(f"  4. Should show: {balance_sol:.6f} SOL")
        
        await client.close()
        return True
        
    except Exception as e:
        print(f"\n❌ Error importing wallet: {e}")
        import traceback
        traceback.print_exc()
        await client.close()
        return False

async def main():
    success = await import_platform_wallet()
    return success

if __name__ == "__main__":
    asyncio.run(main())

