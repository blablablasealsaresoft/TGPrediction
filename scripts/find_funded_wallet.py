"""
Check all wallets and find which one has 0.2 SOL
"""

import asyncio
import sqlite3
from solana.rpc.async_api import AsyncClient
from solders.pubkey import Pubkey
import os
from dotenv import load_dotenv

load_dotenv()

async def main():
    rpc_url = os.getenv('SOLANA_RPC_URL')
    client = AsyncClient(rpc_url)
    
    # Get all wallets from database
    conn = sqlite3.connect('trading_bot.db')
    cursor = conn.cursor()
    cursor.execute('SELECT user_id, public_key FROM user_wallets')
    wallets = cursor.fetchall()
    conn.close()
    
    print("\n💰 CHECKING BALANCES FOR ALL WALLETS:")
    print("="*70)
    
    funded_wallet = None
    
    for user_id, address in wallets:
        try:
            pubkey = Pubkey.from_string(address)
            response = await client.get_balance(pubkey)
            balance_sol = response.value / 1e9
            
            print(f"\nUser {user_id}:")
            print(f"  Address: {address}")
            print(f"  Balance: {balance_sol:.6f} SOL")
            
            if balance_sol >= 0.2:
                print(f"  ✅ THIS ONE HAS FUNDS!")
                funded_wallet = (user_id, address, balance_sol)
        except Exception as e:
            print(f"  Error: {e}")
    
    await client.close()
    
    print("\n" + "="*70)
    
    if funded_wallet:
        user_id, address, balance = funded_wallet
        print(f"\n✅ FOUND FUNDED WALLET!")
        print(f"  User: {user_id}")
        print(f"  Address: {address}")
        print(f"  Balance: {balance:.6f} SOL")
        
        if user_id != 6594416344:
            print(f"\n⚠️ This wallet belongs to user {user_id}, not admin (6594416344)")
            print(f"\nTo transfer to admin:")
            print(f"  python scripts/transfer_wallet_to_admin.py {address}")
        else:
            print(f"\n✅ This IS the admin wallet - already correct!")
    else:
        print(f"\n❌ No funded wallets found!")
        print(f"\nAll wallets have 0 SOL")

if __name__ == "__main__":
    asyncio.run(main())

