#!/usr/bin/env python3
"""
Automatically restore old wallet from backup
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

async def restore_old_wallet():
    """Automatically restore the old wallet from backup"""
    print("\nAUTOMATIC WALLET RESTORATION")
    print("=" * 50)
    
    config = get_config()
    client = AsyncClient(config.solana_rpc_url)
    
    try:
        conn = sqlite3.connect('trading_bot.db.backup')
        cursor = conn.cursor()
        
        # Find the old wallet
        old_wallet_address = "mDSm6bqKdKc8ARbsdAkkHKzDzAqERuFxMChiGmuUDaR"
        cursor.execute('SELECT public_key, encrypted_private_key, created_at FROM user_wallets WHERE public_key=?', (old_wallet_address,))
        row = cursor.fetchone()
        
        if row:
            public_key, encrypted_key, created_at = row
            
            print(f"Found old wallet in backup:")
            print(f"Address: {public_key}")
            print(f"Created: {created_at}")
            print(f"Encrypted Key: {encrypted_key[:20]}...")
            
            # Check balance
            pubkey = Pubkey.from_string(public_key)
            response = await client.get_balance(pubkey)
            balance_sol = response.value / 1e9
            print(f"Balance: {balance_sol:.6f} SOL")
            
            if balance_sol > 0:
                print(f"\nRestoring wallet with {balance_sol:.6f} SOL...")
                
                # Import here to avoid circular imports
                from src.modules.database import DatabaseManager, UserWallet
                from sqlalchemy import delete
                
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
                        encrypted_private_key=encrypted_key
                    )
                    session.add(wallet)
                    await session.commit()
                    print(f"Wallet restored successfully!")
                
                print(f"\nSUCCESS! WALLET RESTORED!")
                print(f"=" * 60)
                print(f"Address: {public_key}")
                print(f"Balance: {balance_sol:.6f} SOL")
                print(f"=" * 60)
                
                print(f"\nYour bot is now ready to trade!")
                print(f"Next steps:")
                print(f"1. Start the bot: python scripts/run_bot.py")
                print(f"2. Use /autostart in Telegram to begin auto-trading")
                print(f"3. Monitor with: python scripts/monitor_wallet_scanning_24hr.py")
                
                await client.close()
                await db.dispose()
                return True
            else:
                print(f"Wallet has no funds to restore")
        else:
            print(f"Old wallet not found in backup")
            
        conn.close()
        await client.close()
        return False
        
    except Exception as e:
        print(f"Error restoring wallet: {e}")
        await client.close()
        return False

async def main():
    print("AUTOMATIC WALLET RESTORATION")
    print("=" * 60)
    print(f"Restoring wallet: mDSm6bqKdKc8ARbsdAkkHKzDzAqERuFxMChiGmuUDaR")
    print(f"With balance: 0.2 SOL")
    print("=" * 60)
    
    success = await restore_old_wallet()
    
    if success:
        print(f"\nWALLET RESTORATION COMPLETE!")
        print(f"You can now start trading with your 0.2 SOL!")
    else:
        print(f"\nRestoration failed")
        print(f"Please check the backup file or fund a new wallet")

if __name__ == "__main__":
    asyncio.run(main())
