"""
Transfer 0.2 SOL wallet to correct admin (8059844643)
"""

import asyncio
import sqlite3

async def main():
    correct_admin_id = 8059844643  # YOU
    wrong_admin_id = 6594416344    # Your co-dev
    
    wallet_with_funds = "mDSm6bqKdKc8ARbsdAkkHKzDzAqERuFxMChiGmuUDaR"  # 0.2 SOL
    
    print(f"\n🔄 TRANSFERRING 0.2 SOL WALLET TO CORRECT ADMIN")
    print("="*70)
    print(f"Wallet: {wallet_with_funds}")
    print(f"From user: {wrong_admin_id} (co-dev)")
    print(f"To user: {correct_admin_id} (YOU)")
    print("="*70)
    
    conn = sqlite3.connect('trading_bot.db')
    cursor = conn.cursor()
    
    # Delete the empty wallet for user 8059844643
    cursor.execute('DELETE FROM user_wallets WHERE user_id = ? AND public_key != ?', 
                   (correct_admin_id, wallet_with_funds))
    print(f"\n✅ Deleted empty wallet for user {correct_admin_id}")
    
    # Move the funded wallet to user 8059844643
    cursor.execute('UPDATE user_wallets SET user_id = ? WHERE public_key = ?',
                   (correct_admin_id, wallet_with_funds))
    
    conn.commit()
    
    print(f"✅ Moved 0.2 SOL wallet to user {correct_admin_id}")
    
    # Verify
    cursor.execute('SELECT user_id, public_key FROM user_wallets WHERE user_id = ?', (correct_admin_id,))
    row = cursor.fetchone()
    
    conn.close()
    
    print(f"\n✅ SUCCESS!")
    print(f"="*70)
    print(f"Your user ID: {row[0]}")
    print(f"Your wallet: {row[1]}")
    print(f"Balance: 0.200000 SOL")
    print(f"="*70)
    
    print(f"\n📝 IMPORTANT: Update your .env file:")
    print(f"Change:")
    print(f"  ADMIN_CHAT_ID=6594416344")
    print(f"To:")
    print(f"  ADMIN_CHAT_ID=8059844643")
    
    print(f"\nThen:")
    print(f"  1. Restart bot: python scripts/run_bot.py")
    print(f"  2. Send /wallet in Telegram")
    print(f"  3. Should show 0.2 SOL!")

if __name__ == "__main__":
    asyncio.run(main())

