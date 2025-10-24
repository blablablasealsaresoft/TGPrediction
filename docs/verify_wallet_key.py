#!/usr/bin/env python3
"""
Check which wallet the private key corresponds to
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from solana.rpc.async_api import AsyncClient
from solders.keypair import Keypair
import base58
from src.config import get_config

async def check_wallet_from_private_key():
    """Check which wallet address the private key corresponds to"""
    print("\nPRIVATE KEY WALLET CHECK")
    print("=" * 50)
    
    config = get_config()
    client = AsyncClient(config.solana_rpc_url)
    
    try:
        # The private key you provided
        private_key_b58 = "2KBD49gknMGpsVSJWuUFbTPLsVLd4kMEN8n8cBERvJFML8sBzavGqpHH14mYUwDWYHZ6EdTx1DzHxto6PUsUVpke"
        
        # Decode and create keypair
        private_key_bytes = base58.b58decode(private_key_b58)
        keypair = Keypair.from_bytes(private_key_bytes)
        wallet_address = str(keypair.pubkey())
        
        print(f"Private Key: {private_key_b58[:20]}...")
        print(f"Corresponds to Wallet: {wallet_address}")
        
        # Check balance
        balance_response = await client.get_balance(keypair.pubkey())
        balance_sol = balance_response.value / 1_000_000_000
        
        print(f"Balance: {balance_sol:.6f} SOL")
        
        # Check if this matches your old wallet
        old_wallet_address = "mDSm6bqKdKc8ARbsdAkkHKzDzAqERuFxMChiGmuUDaR"
        
        if wallet_address == old_wallet_address:
            print(f"\n✅ CONFIRMED: This private key is for your OLD wallet!")
            print(f"Old wallet has {balance_sol:.6f} SOL")
        else:
            print(f"\n❌ MISMATCH: Private key doesn't match old wallet address")
            print(f"Expected: {old_wallet_address}")
            print(f"Got: {wallet_address}")
        
        await client.close()
        return wallet_address, balance_sol
        
    except Exception as e:
        print(f"Error: {e}")
        await client.close()
        return None, 0

async def main():
    print("WALLET ADDRESS VERIFICATION")
    print("=" * 60)
    
    wallet_address, balance = await check_wallet_from_private_key()
    
    if wallet_address == "mDSm6bqKdKc8ARbsdAkkHKzDzAqERuFxMChiGmuUDaR":
        print(f"\n🎉 PERFECT! We can now transfer {balance:.6f} SOL automatically!")
        print("Run: python automated_transfer.py")
    else:
        print("\n❌ Private key doesn't match the old wallet address")
        print("Please double-check the private key")

if __name__ == "__main__":
    asyncio.run(main())
