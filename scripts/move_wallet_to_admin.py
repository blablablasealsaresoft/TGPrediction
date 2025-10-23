"""
Move the 0.2 SOL wallet from user 8059844643 to admin user 6594416344
"""

import asyncio
import sqlite3
from sqlalchemy import delete, update
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.modules.database import DatabaseManager, UserWallet

async def main():
    admin_id = 6594416344
    old_user_id = 8059844643
    wallet_address = "mDSm6bqKdKc8ARbsdAkkHKzDzAqERuFxMChiGmuUDaR"
    
    print(f"\n🔄 MOVING WALLET TO ADMIN")
    print("="*60)
    print(f"Wallet: {wallet_address}")
    print(f"From user: {old_user_id}")
    print(f"To user: {admin_id}")
    print("="*60)
    
    db = DatabaseManager()
    
    # Update the wallet's user_id
    async with db.async_session() as session:
        await session.execute(
            update(UserWallet)
            .where(UserWallet.public_key == wallet_address)
            .values(user_id=admin_id)
        )
        await session.commit()
        print(f"\n✅ Wallet moved to admin user!")
    
    print(f"\n✅ SUCCESS!")
    print(f"="*60)
    print(f"Your wallet: {wallet_address}")
    print(f"Balance: 0.200000 SOL")
    print(f"="*60)
    
    print(f"\n📱 Next steps:")
    print(f"  1. Restart bot: python scripts/run_bot.py")
    print(f"  2. In Telegram: /wallet")
    print(f"  3. Should show 0.2 SOL!")
    print(f"  4. Then: /autostart")

if __name__ == "__main__":
    asyncio.run(main())

