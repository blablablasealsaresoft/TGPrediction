import sqlite3

print("\n🔄 RESTORING WALLET FROM BACKUP")
print("="*70)

# Copy wallet from backup to main database
src = sqlite3.connect('trading_bot.db.backup')
dst = sqlite3.connect('trading_bot.db')

src_cursor = src.cursor()
dst_cursor = dst.cursor()

# Find the 0.2 SOL wallet in backup
src_cursor.execute('''
    SELECT user_id, public_key, encrypted_private_key, created_at 
    FROM user_wallets 
    WHERE public_key = ?
''', ('mDSm6bqKdKc8ARbsdAkkHKzDzAqERuFxMChiGmuUDaR',))

row = src_cursor.fetchone()

if not row:
    print("❌ Wallet not in backup!")
    src.close()
    dst.close()
    exit(1)

print(f"✅ Found in backup:")
print(f"   User: {row[0]}")
print(f"   Address: {row[1]}")

# Delete all wallets for user 8059844643 in main DB
dst_cursor.execute('DELETE FROM user_wallets WHERE user_id = ?', (8059844643,))
print(f"\n✅ Cleared wallets for user 8059844643")

# Insert the backup wallet for user 8059844643
dst_cursor.execute('''
    INSERT INTO user_wallets (user_id, public_key, encrypted_private_key, created_at)
    VALUES (?, ?, ?, ?)
''', (8059844643, row[1], row[2], row[3]))

dst.commit()
print(f"✅ Wallet restored!")

# Verify
dst_cursor.execute('SELECT public_key FROM user_wallets WHERE user_id = ?', (8059844643,))
verify = dst_cursor.fetchone()

src.close()
dst.close()

print(f"\n✅ VERIFIED:")
print(f"="*70)
print(f"User: 8059844643")
print(f"Wallet: {verify[0] if verify else 'NOT FOUND'}")
print(f"="*70)
print(f"\nNow restart bot and it MUST use this wallet!")

