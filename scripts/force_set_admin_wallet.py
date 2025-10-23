"""
FORCE set admin wallet and delete all others
"""

import sqlite3

# Your correct info
ADMIN_USER_ID = 8059844643
WALLET_WITH_FUNDS = "mDSm6bqKdKc8ARbsdAkkHKzDzAqERuFxMChiGmuUDaR"

conn = sqlite3.connect('trading_bot.db')
cursor = conn.cursor()

print("\n🔧 FORCING ADMIN WALLET SETUP")
print("="*70)

# Delete ALL wallets for this user
cursor.execute('DELETE FROM user_wallets WHERE user_id = ?', (ADMIN_USER_ID,))
deleted = cursor.rowcount
print(f"✅ Deleted {deleted} existing wallets for user {ADMIN_USER_ID}")

# Get the wallet data from wherever it exists
cursor.execute('SELECT encrypted_private_key FROM user_wallets WHERE public_key = ?', (WALLET_WITH_FUNDS,))
row = cursor.fetchone()

if row:
    encrypted_key = row[0]
    
    # Insert as THE ONLY wallet for admin
    cursor.execute('''
        INSERT INTO user_wallets (user_id, public_key, encrypted_private_key, created_at)
        VALUES (?, ?, ?, datetime('now'))
    ''', (ADMIN_USER_ID, WALLET_WITH_FUNDS, encrypted_key))
    
    print(f"✅ Inserted wallet for user {ADMIN_USER_ID}")
else:
    print(f"❌ Could not find encrypted key for {WALLET_WITH_FUNDS}")
    print("Searching all wallets...")
    cursor.execute('SELECT user_id, public_key FROM user_wallets')
    all_wallets = cursor.fetchall()
    for w in all_wallets:
        print(f"  User {w[0]}: {w[1]}")

conn.commit()

# Verify
cursor.execute('SELECT user_id, public_key FROM user_wallets WHERE user_id = ?', (ADMIN_USER_ID,))
result = cursor.fetchone()

conn.close()

print("\n✅ VERIFICATION:")
print("="*70)
if result:
    print(f"User {result[0]}: {result[1]}")
    print(f"\n✅ SUCCESS! This wallet is now LOCKED to your account!")
else:
    print(f"❌ FAILED - wallet not set")

print("="*70)
print("\nRestart bot: python scripts/run_bot.py")
print("Then /start should show this wallet with 0.2 SOL")

