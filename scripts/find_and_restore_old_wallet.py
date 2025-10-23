"""
Find the old wallet (mDSm6bq...) and restore it
"""

import asyncio
import os
import sys
import sqlite3
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from solana.rpc.async_api import AsyncClient
from solders.pubkey import Pubkey
from sqlalchemy import select, delete
from src.modules.database import DatabaseManager, UserWallet
from src.modules.wallet_manager import WalletEncryption

async def check_backup_database():
    """Check backup database for old wallet"""
    
    print("\n🔍 Checking backup database...")
    
    try:
        conn = sqlite3.connect('trading_bot.db.backup')
        cursor = conn.cursor()
        
        # Find wallets for admin user
        cursor.execute('SELECT public_key, encrypted_private_key, created_at FROM user_wallets WHERE user_id=6594416344')
        rows = cursor.fetchall()
        
        if rows:
            print(f"✅ Found {len(rows)} wallet(s) in backup:\n")
            for row in rows:
                print(f"   Address: {row[0]}")
                print(f"   Created: {row[2]}")
                print()
            conn.close()
            return rows
        else:
            print("❌ No wallets found in backup")
            conn.close()
            return None
            
    except Exception as e:
        print(f"❌ Error reading backup: {e}")
        return None

async def restore_wallet_from_backup(wallet_data):
    """Restore wallet to current database"""
    
    public_key = wallet_data[0]
    encrypted_private_key = wallet_data[1]
    admin_id = int(os.getenv('ADMIN_CHAT_ID'))
    
    print(f"\n🔄 Restoring wallet {public_key[:8]}...")
    
    db = DatabaseManager()
    
    # Delete any existing wallets for this user
    async with db.async_session() as session:
        await session.execute(delete(UserWallet).where(UserWallet.user_id == admin_id))
        await session.commit()
        print(f"✅ Cleared existing wallets")
    
    # Add the old wallet back
    async with db.async_session() as session:
        wallet = UserWallet(
            user_id=admin_id,
            public_key=public_key,
            encrypted_private_key=encrypted_private_key
        )
        session.add(wallet)
        await session.commit()
        print(f"✅ Wallet restored!")
    
    # Verify
    rpc_url = os.getenv('SOLANA_RPC_URL')
    client = AsyncClient(rpc_url)
    
    try:
        pubkey = Pubkey.from_string(public_key)
        response = await client.get_balance(pubkey)
        balance_sol = response.value / 1e9
        
        print(f"\n✅ WALLET RESTORED SUCCESSFULLY!")
        print(f"="*60)
        print(f"Address: {public_key}")
        print(f"Balance: {balance_sol:.6f} SOL")
        print(f"="*60)
        
        print(f"\nNow restart your bot and send /wallet")
        print(f"It should show this wallet with {balance_sol:.6f} SOL!")
        
    except Exception as e:
        print(f"⚠️ Error checking balance: {e}")
    
    await client.close()

async def main():
    print("\n🔍 WALLET RECOVERY TOOL")
    print("="*60)
    print(f"Looking for wallet: mDSm6bqKdKc8ARbsdAkkHKzDzAqERuFxMChiGmuUDaR")
    print(f"With balance: 0.2 SOL")
    print("="*60)
    
    # Check backup
    backup_wallets = await check_backup_database()
    
    if backup_wallets:
        # Find the right wallet
        old_wallet = "mDSm6bqKdKc8ARbsdAkkHKzDzAqERuFxMChiGmuUDaR"
        
        for wallet_data in backup_wallets:
            if wallet_data[0] == old_wallet:
                print(f"\n✅ FOUND YOUR WALLET IN BACKUP!")
                
                response = input(f"\nRestore this wallet? (yes/no): ")
                
                if response.lower() == 'yes':
                    await restore_wallet_from_backup(wallet_data)
                    return True
                else:
                    print("❌ Restore cancelled")
                    return False
        
        print(f"\n❌ Wallet {old_wallet[:8]}... not in backup")
        print(f"\nBut found these wallets - restore one?")
        
        for i, wallet_data in enumerate(backup_wallets, 1):
            print(f"{i}. {wallet_data[0]}")
        
        choice = input("\nEnter number to restore (or 'n' to skip): ")
        
        if choice.isdigit() and 1 <= int(choice) <= len(backup_wallets):
            await restore_wallet_from_backup(backup_wallets[int(choice)-1])
            return True
    
    print(f"\n❌ Could not find wallet in backup")
    print(f"\nYour options:")
    print(f"  1. Check other backups")
    print(f"  2. Use /export_wallet if you exported the key")
    print(f"  3. Create new wallet and fund it")
    
    return False

if __name__ == "__main__":
    asyncio.run(main())

