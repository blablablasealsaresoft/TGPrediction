"""
Simple script to import platform wallet for admin user
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from solana.rpc.async_api import AsyncClient
from solders.keypair import Keypair
from sqlalchemy import select, delete
from src.modules.database import DatabaseManager, UserWallet
from src.modules.wallet_manager import WalletEncryption

async def main():
    admin_id = int(os.getenv('ADMIN_CHAT_ID'))
    wallet_key = os.getenv('WALLET_PRIVATE_KEY')
    rpc_url = os.getenv('SOLANA_RPC_URL')

    keypair = Keypair.from_base58_string(wallet_key)
    public_key = str(keypair.pubkey())

    client = AsyncClient(rpc_url)
    db = DatabaseManager()
    encryption = WalletEncryption()
    
    # Get balance
    response = await client.get_balance(keypair.pubkey())
    balance_sol = response.value / 1e9
    
    print(f"\n✅ Platform Wallet: {public_key}")
    print(f"✅ Balance: {balance_sol:.6f} SOL")
    print(f"✅ Importing for admin user: {admin_id}\n")
    
    # Delete existing wallet
    async with db.async_session() as session:
        await session.execute(delete(UserWallet).where(UserWallet.user_id == admin_id))
        await session.commit()
    
    # Add platform wallet
    encrypted = encryption.encrypt_private_key(bytes(keypair))
    
    async with db.async_session() as session:
        wallet = UserWallet(
            user_id=admin_id,
            public_key=public_key,
            encrypted_private_key=encrypted
        )
        session.add(wallet)
        await session.commit()
    
    print(f"✅ DONE! Your bot now uses your funded wallet!")
    print(f"\nVerify in Telegram:")
    print(f"  /wallet - Should show {public_key}")
    print(f"  /balance - Should show {balance_sol:.6f} SOL")
    
    await client.close()

if __name__ == "__main__":
    asyncio.run(main())

