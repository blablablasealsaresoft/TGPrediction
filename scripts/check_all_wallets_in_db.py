import sqlite3

print("\n🔍 Checking BOTH databases for all wallets...\n")

# Check current database
print("="*60)
print("CURRENT DATABASE (trading_bot.db)")
print("="*60)
try:
    conn = sqlite3.connect('trading_bot.db')
    cursor = conn.cursor()
    cursor.execute('SELECT user_id, public_key, created_at FROM user_wallets')
    rows = cursor.fetchall()
    
    if rows:
        for row in rows:
            print(f"User {row[0]}: {row[1]} (created: {row[2]})")
    else:
        print("No wallets found")
    conn.close()
except Exception as e:
    print(f"Error: {e}")

# Check backup database
print(f"\n" + "="*60)
print("BACKUP DATABASE (trading_bot.db.backup)")
print("="*60)
try:
    conn = sqlite3.connect('trading_bot.db.backup')
    cursor = conn.cursor()
    cursor.execute('SELECT user_id, public_key, created_at FROM user_wallets')
    rows = cursor.fetchall()
    
    if rows:
        for row in rows:
            print(f"User {row[0]}: {row[1]} (created: {row[2]})")
            
            # Check if this is the wallet we're looking for
            if row[1] == "mDSm6bqKdKc8ARbsdAkkHKzDzAqERuFxMChiGmuUDaR":
                print(f"   ✅ THIS IS THE 0.2 SOL WALLET!")
    else:
        print("No wallets found")
    conn.close()
except Exception as e:
    print(f"Error: {e}")

print(f"\n" + "="*60)

