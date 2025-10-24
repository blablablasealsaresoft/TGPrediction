#!/usr/bin/env python3
"""
Transfer funds from old wallet to current trading wallet
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
from solders.system_program import TransferParams, transfer
from solders.transaction import Transaction
from solders.message import MessageV0
from solders.hash import Hash
from solders.signature import Signature
import base58
from src.config import get_config

async def get_current_wallet():
    """Get current trading wallet from config"""
    config = get_config()
    
    # The private key in your .env is base58 encoded, not hex
    private_key_b58 = "2KBD49gknMGpsVSJWuUFbTPLsVLd4kMEN8n8cBERvJFML8sBzavGqpHH14mYUwDWYHZ6EdTx1DzHxto6PUsUVpke"
    
    try:
        # Decode base58 private key
        private_key_bytes = base58.b58decode(private_key_b58)
        keypair = Keypair.from_bytes(private_key_bytes)
        address = str(keypair.pubkey())
        
        print(f"Current Trading Wallet: {address}")
        return keypair, address
        
    except Exception as e:
        print(f"Error decoding current wallet private key: {e}")
        return None, None

async def check_balances():
    """Check balances of both wallets"""
    print("\nWALLET BALANCE CHECK")
    print("=" * 50)
    
    config = get_config()
    client = AsyncClient(config.solana_rpc_url)
    
    # Old wallet
    old_address = "mDSm6bqKdKc8ARbsdAkkHKzDzAqERuFxMChiGmuUDaR"
    old_pubkey = Pubkey.from_string(old_address)
    old_balance_response = await client.get_balance(old_pubkey)
    old_balance = old_balance_response.value / 1_000_000_000
    
    print(f"Old Wallet: {old_address}")
    print(f"Balance: {old_balance:.6f} SOL")
    
    # Current wallet
    current_keypair, current_address = await get_current_wallet()
    if current_keypair:
        current_balance_response = await client.get_balance(current_keypair.pubkey())
        current_balance = current_balance_response.value / 1_000_000_000
        
        print(f"Current Wallet: {current_address}")
        print(f"Balance: {current_balance:.6f} SOL")
    else:
        current_balance = 0
        print("Could not decode current wallet")
    
    await client.close()
    return old_balance, current_balance, current_keypair, current_address

async def transfer_funds():
    """Transfer funds from old wallet to current wallet"""
    print("\nFUND TRANSFER")
    print("=" * 50)
    
    old_balance, current_balance, current_keypair, current_address = await check_balances()
    
    if old_balance == 0:
        print("No funds to transfer from old wallet.")
        return
    
    if not current_keypair:
        print("Cannot transfer - current wallet private key issue.")
        return
    
    print(f"\nReady to transfer {old_balance:.6f} SOL")
    print(f"From: mDSm6bqKdKc8ARbsdAkkHKzDzAqERuFxMChiGmuUDaR")
    print(f"To: {current_address}")
    
    print("\nTo complete the transfer, you need:")
    print("1. The private key for the old wallet (mDSm6bqKdKc8ARbsdAkkHKzDzAqERuFxMChiGmuUDaR)")
    print("2. Or import the old wallet into Phantom/Solflare and send manually")
    
    print("\nManual transfer steps:")
    print("1. Open Phantom or Solflare wallet")
    print("2. Import wallet with private key/seed phrase")
    print("3. Send 0.2 SOL to: " + current_address)
    print("4. Keep 0.01 SOL for transaction fees")
    
    print(f"\nRecommended transfer amount: {old_balance - 0.01:.6f} SOL")
    print("(Keep 0.01 SOL for fees)")

async def main():
    print("WALLET FUND TRANSFER UTILITY")
    print("=" * 60)
    
    await transfer_funds()
    
    print("\n" + "=" * 60)
    print("NEXT STEPS")
    print("=" * 60)
    print("1. Transfer funds from old wallet to current wallet")
    print("2. Start the bot: python scripts/run_bot.py")
    print("3. Use /autostart in Telegram to begin trading")
    print("4. Monitor with: python scripts/monitor_wallet_scanning_24hr.py")

if __name__ == "__main__":
    asyncio.run(main())
