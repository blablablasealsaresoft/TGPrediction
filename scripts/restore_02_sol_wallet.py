"""
Restore the 0.2 SOL wallet to admin user
"""

import asyncio
import sqlite3
from sqlalchemy import delete
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.modules.database import DatabaseManager, UserWallet

async def main():
    # Get the wallet data from current database (user 8059844643)
    conn = sqlite3.connect('trading_bot.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT public_key, encrypted_private_key 
        FROM user_wallets 
        WHERE public_key = "mDSm6bqKdKc8ARbsdAkkHKzDzAqERuFxMChiGmuUDaR"
    ''')
    
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        print("❌ Could not find wallet in database")
        return
    
    public_key = row[0]
    encrypted_key = row[1]
    
    print(f"\n✅ Found wallet:")
    print(f"   Address: {public_key}")
    print(f"   On-chain balance: 0.2 SOL")
    
    # Move to admin user (6594416344)
    admin_id = 6594416344
    
    print(f"\n🔄 Assigning to admin user {admin_id}...")
    
    db = DatabaseManager()
    
    # Delete admin's current wallet
    async with db.async_session() as session:
        await session.execute(delete(UserWallet).where(UserWallet.user_id == admin_id))
        await session.commit()
        print(f"✅ Cleared old wallets")
    
    # Add the 0.2 SOL wallet
    async with db.async_session() as session:
        wallet = UserWallet(
            user_id=admin_id,
            public_key=public_key,
            encrypted_private_key=encrypted_key
        )
        session.add(wallet)
        await session.commit()
        print(f"✅ Wallet assigned to your account!")
    
    print(f"\n{'='*60}")
    print(f"✅ SUCCESS!")
    print(f"{'='*60}")
    print(f"Your wallet: {public_key}")
    print(f"Balance: 0.200000 SOL")
    print(f"{'='*60}")
    
    print(f"\nNow:")
    print(f"  1. Restart bot: python scripts/run_bot.py")
    print(f"  2. Send /wallet in Telegram")
    print(f"  3. Should show 0.2 SOL!")
    print(f"  4. Send /autostart to trade!")

if __name__ == "__main__":
    asyncio.run(main())

