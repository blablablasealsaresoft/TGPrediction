"""
Move all 441 tracked wallets from user 1 to the correct admin user 8059844643
"""

import asyncio
import sqlite3

async def main():
    correct_user = 8059844643  # YOU
    test_user = 1               # Where wallets were added
    
    print(f"\n🔄 MOVING TRACKED WALLETS TO YOUR ACCOUNT")
    print("="*70)
    
    conn = sqlite3.connect('trading_bot.db')
    cursor = conn.cursor()
    
    # Count current wallets
    cursor.execute('SELECT COUNT(*) FROM tracked_wallets WHERE user_id = ?', (test_user,))
    test_count = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM tracked_wallets WHERE user_id = ?', (correct_user,))
    your_count = cursor.fetchone()[0]
    
    print(f"Before transfer:")
    print(f"  User 1 (test): {test_count} wallets")
    print(f"  User {correct_user} (YOU): {your_count} wallets")
    
    # Transfer all wallets
    cursor.execute('UPDATE tracked_wallets SET user_id = ? WHERE user_id = ?', 
                   (correct_user, test_user))
    
    transferred = cursor.rowcount
    conn.commit()
    
    # Verify
    cursor.execute('SELECT COUNT(*) FROM tracked_wallets WHERE user_id = ?', (correct_user,))
    final_count = cursor.fetchone()[0]
    
    conn.close()
    
    print(f"\n✅ Transfer complete!")
    print(f"  Transferred: {transferred} wallets")
    print(f"  You now have: {final_count} wallets")
    print("="*70)
    
    print(f"\n📱 Test in Telegram:")
    print(f"  /rankings")
    print(f"\nShould now show top wallets with scores!")

if __name__ == "__main__":
    asyncio.run(main())

