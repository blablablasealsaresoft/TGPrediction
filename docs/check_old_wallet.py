#!/usr/bin/env python3
"""
Check old wallet balance and transfer funds
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from solana.rpc.async_api import AsyncClient
from solders.pubkey import Pubkey
from solders.keypair import Keypair
from src.config import get_config

async def check_old_wallet():
    """Check balance of old wallet"""
    print("\nOLD WALLET BALANCE CHECK")
    print("=" * 50)
    
    config = get_config()
    client = AsyncClient(config.solana_rpc_url)
    
    # Your old wallet address
    old_wallet_address = "mDSm6bqKdKc8ARbsdAkkHKzDzAqERuFxMChiGmuUDaR"
    
    try:
        # Check balance
        wallet_pubkey = Pubkey.from_string(old_wallet_address)
        balance_response = await client.get_balance(wallet_pubkey)
        balance_sol = balance_response.value / 1_000_000_000
        
        print(f"Old Wallet Address: {old_wallet_address}")
        print(f"Balance: {balance_sol:.6f} SOL")
        
        if balance_sol > 0:
            print(f"\nFOUND {balance_sol:.6f} SOL in your old wallet!")
            print("This can be transferred to your trading wallet.")
        else:
            print("\nOld wallet has no funds.")
            
    except Exception as e:
        print(f"Error checking old wallet: {e}")
    
    await client.close()
    return balance_sol

async def check_current_wallet():
    """Check current trading wallet"""
    print("\nCURRENT TRADING WALLET")
    print("=" * 50)
    
    config = get_config()
    client = AsyncClient(config.solana_rpc_url)
    
    # Current wallet from private key
    try:
        from solders.keypair import Keypair
        
        # Decode the private key
        private_key_bytes = bytes.fromhex("2KBD49gknMGpsVSJWuUFbTPLsVLd4kMEN8n8cBERvJFML8sBzavGqpHH14mYUwDWYHZ6EdTx1DzHxto6PUsUVpke")
        keypair = Keypair.from_bytes(private_key_bytes)
        current_address = str(keypair.pubkey())
        
        # Check balance
        balance_response = await client.get_balance(keypair.pubkey())
        balance_sol = balance_response.value / 1_000_000_000
        
        print(f"Current Wallet Address: {current_address}")
        print(f"Balance: {balance_sol:.6f} SOL")
        
    except Exception as e:
        print(f"Error checking current wallet: {e}")
        current_address = None
        balance_sol = 0
    
    await client.close()
    return current_address, balance_sol

async def transfer_funds():
    """Transfer funds from old wallet to current wallet"""
    print("\nTRANSFER FUNDS")
    print("=" * 50)
    
    config = get_config()
    client = AsyncClient(config.solana_rpc_url)
    
    try:
        # Get old wallet keypair (you'll need to provide the private key)
        print("To transfer funds, you need to provide the private key for:")
        print("Old wallet: mDSm6bqKdKc8ARbsdAkkHKzDzAqERuFxMChiGmuUDaR")
        print("\nDo you have the private key for this wallet?")
        print("If yes, we can create a transfer script.")
        print("If no, you'll need to import it into a wallet like Phantom or Solflare.")
        
    except Exception as e:
        print(f"Error: {e}")
    
    await client.close()

async def main():
    print("WALLET FUNDS CHECK")
    print("=" * 60)
    
    # Check old wallet
    old_balance = await check_old_wallet()
    
    # Check current wallet
    current_address, current_balance = await check_current_wallet()
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Old Wallet (mDSm6bqKdKc8ARbsdAkkHKzDzAqERuFxMChiGmuUDaR): {old_balance:.6f} SOL")
    print(f"Current Wallet ({current_address}): {current_balance:.6f} SOL")
    
    if old_balance > 0:
        print(f"\nYou have {old_balance:.6f} SOL in your old wallet!")
        print("To use it for trading, you need to transfer it to your current wallet.")
        print("\nOptions:")
        print("1. Import old wallet into Phantom/Solflare and send to current wallet")
        print("2. Provide old wallet private key for automated transfer")
        print("3. Use a wallet recovery tool if you have the seed phrase")
    else:
        print("\nOld wallet has no funds to transfer.")

if __name__ == "__main__":
    asyncio.run(main())
