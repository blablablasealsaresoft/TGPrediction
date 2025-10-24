#!/usr/bin/env python3
"""
Check backup database for old wallet
"""

import asyncio
import sys
import sqlite3
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from solana.rpc.async_api import AsyncClient
from solders.pubkey import Pubkey
from src.config import get_config

async def check_backup_database():
    """Check backup database for old wallet"""
    print("\nBACKUP DATABASE CHECK")
    print("=" * 50)
    
    config = get_config()
    client = AsyncClient(config.solana_rpc_url)
    
    try:
        conn = sqlite3.connect('trading_bot.db.backup')
        cursor = conn.cursor()
        
        # Find wallets for admin user
        admin_id = config.admin_chat_id
        cursor.execute('SELECT public_key, encrypted_private_key, created_at FROM user_wallets WHERE user_id=?', (admin_id,))
        rows = cursor.fetchall()
        
        if rows:
            print(f"Found {len(rows)} wallet(s) in backup:")
            
            old_wallet_address = "mDSm6bqKdKc8ARbsdAkkHKzDzAqERuFxMChiGmuUDaR"
            found_old = False
            
            for i, row in enumerate(rows, 1):
                public_key = row[0]
                encrypted_key = row[1]
                created_at = row[2]
                
                print(f"\n{i}. Address: {public_key}")
                print(f"   Created: {created_at}")
                
                # Check balance
                try:
                    pubkey = Pubkey.from_string(public_key)
                    response = await client.get_balance(pubkey)
                    balance_sol = response.value / 1e9
                    print(f"   Balance: {balance_sol:.6f} SOL")
                    
                    if public_key == old_wallet_address:
                        found_old = True
                        print(f"   *** THIS IS YOUR OLD WALLET! ***")
                        print(f"   Encrypted Key: {encrypted_key[:20]}...")
                        
                except Exception as e:
                    print(f"   Error checking balance: {e}")
            
            if found_old:
                print(f"\nFOUND YOUR OLD WALLET IN BACKUP!")
                print(f"Address: {old_wallet_address}")
                print(f"We can restore it to the current database")
                
                response = input(f"\nRestore this wallet? (yes/no): ")
                
                if response.lower() == 'yes':
                    await restore_wallet_from_backup(rows[0] if len(rows) == 1 else next(row for row in rows if row[0] == old_wallet_address))
                    return True
                else:
                    print("Restore cancelled")
                    return False
            else:
                print(f"\nOld wallet ({old_wallet_address}) not found in backup")
                print(f"But found these wallets - restore one?")
                
                for i, row in enumerate(rows, 1):
                    print(f"{i}. {row[0]}")
                
                choice = input("\nEnter number to restore (or 'n' to skip): ")
                
                if choice.isdigit() and 1 <= int(choice) <= len(rows):
                    await restore_wallet_from_backup(rows[int(choice)-1])
                    return True
        else:
            print("No wallets found in backup")
            
        conn.close()
        await client.close()
        return False
        
    except Exception as e:
        print(f"Error reading backup: {e}")
        await client.close()
        return False

async def restore_wallet_from_backup(wallet_data):
    """Restore wallet to current database"""
    print(f"\nRESTORING WALLET")
    print("=" * 50)
    
    public_key = wallet_data[0]
    encrypted_private_key = wallet_data[1]
    
    print(f"Restoring wallet: {public_key}")
    
    # Import here to avoid circular imports
    from src.modules.database import DatabaseManager, UserWallet
    from sqlalchemy import delete
    
    config = get_config()
    db = DatabaseManager(config.database_url)
    await db.init_db()
    
    admin_id = config.admin_chat_id
    
    # Delete any existing wallets for this user
    async with db.async_session() as session:
        await session.execute(delete(UserWallet).where(UserWallet.user_id == admin_id))
        await session.commit()
        print(f"Cleared existing wallets")
    
    # Add the old wallet back
    async with db.async_session() as session:
        wallet = UserWallet(
            user_id=admin_id,
            public_key=public_key,
            encrypted_private_key=encrypted_private_key
        )
        session.add(wallet)
        await session.commit()
        print(f"Wallet restored!")
    
    # Verify
    client = AsyncClient(config.solana_rpc_url)
    
    try:
        pubkey = Pubkey.from_string(public_key)
        response = await client.get_balance(pubkey)
        balance_sol = response.value / 1e9
        
        print(f"\nWALLET RESTORED SUCCESSFULLY!")
        print(f"=" * 60)
        print(f"Address: {public_key}")
        print(f"Balance: {balance_sol:.6f} SOL")
        print(f"=" * 60)
        
        print(f"\nNow restart your bot and send /wallet")
        print(f"It should show this wallet with {balance_sol:.6f} SOL!")
        
    except Exception as e:
        print(f"Error checking balance: {e}")
    
    await client.close()
    await db.dispose()

async def main():
    print("BACKUP WALLET RECOVERY")
    print("=" * 60)
    print(f"Looking for wallet: mDSm6bqKdKc8ARbsdAkkHKzDzAqERuFxMChiGmuUDaR")
    print(f"With balance: 0.2 SOL")
    print("=" * 60)
    
    success = await check_backup_database()
    
    if success:
        print(f"\nSUCCESS! Wallet restored from backup")
        print(f"Your bot is now ready to trade!")
    else:
        print(f"\nCould not find wallet in backup")
        print(f"Your options:")
        print(f"  1. Check other backups")
        print(f"  2. Fund the current database wallet")
        print(f"  3. Create new wallet and fund it")

if __name__ == "__main__":
    asyncio.run(main())
