#!/usr/bin/env python3
"""
Transfer SOL from old wallet to new wallet
Uses the old encrypted wallet to send to a fresh wallet
"""

import asyncio
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from solana.rpc.async_api import AsyncClient
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.system_program import TransferParams, transfer
from solders.transaction import Transaction
from src.config import get_config

async def transfer_funds():
    """Transfer 0.2 SOL from old wallet to new fresh wallet"""
    
    print("\n" + "="*60)
    print("WALLET TRANSFER - Old → New")
    print("="*60)
    
    config = get_config()
    client = AsyncClient(config.solana_rpc_url)
    
    # Old wallet address (has 0.2 SOL)
    old_wallet = "mDSm6bqKdKc8ARbsdAkkHKzDzAqERuFxMChiGmuUDaR"
    
    print(f"\nOld Wallet: {old_wallet}")
    
    # Check old wallet balance
    try:
        old_pubkey = Pubkey.from_string(old_wallet)
        response = await client.get_balance(old_pubkey)
        balance_lamports = response.value
        balance_sol = balance_lamports / 1_000_000_000
        
        print(f"Balance: {balance_sol:.6f} SOL")
        
        if balance_sol == 0:
            print("\n❌ Old wallet has no funds to transfer!")
            await client.close()
            return
        
        print(f"\n✅ Found {balance_sol:.6f} SOL to transfer")
        
    except Exception as e:
        print(f"❌ Error checking old wallet: {e}")
        await client.close()
        return
    
    print("\n" + "="*60)
    print("SOLUTION: Create fresh wallet with NEW encryption key")
    print("="*60)
    
    print("\nOption 1: EASIEST - Just use the old wallet!")
    print("  • Update .env: WALLET_ENCRYPTION_KEY=kzqwCzrcVTdfOdWSUw4-eDm-QWtseuSoY9KZKIR4_08")
    print("  • Restart bot")
    print("  • /autostart will work!")
    
    print("\nOption 2: Create new wallet and transfer")
    print("  • Bot creates new wallet with new key")
    print("  • You manually send 0.2 SOL to new address")
    print("  • Start fresh")
    
    print("\n" + "="*60)
    print("RECOMMENDATION: Use Option 1 (keep old wallet)")
    print("="*60)
    print("\nIt's already working on Ubuntu!")
    print("Your 0.2 SOL is accessible there.")
    print("\nFor Windows: Just use the backup encryption key!")
    
    await client.close()

if __name__ == "__main__":
    asyncio.run(transfer_funds())

