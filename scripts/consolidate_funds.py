#!/usr/bin/env python3
"""
Check all old wallets and transfer funds to new wallet
"""

import asyncio
import sys
import sqlite3
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from solana.rpc.async_api import AsyncClient
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.system_program import TransferParams, transfer
from solders.transaction import Transaction
from solders.message import Message
import base58

NEW_WALLET = "Fs2bohyETVLnSdo2v2JyKCoipMS8c5qhBqkTMhkjCgX"
RPC_URL = "https://mainnet.helius-rpc.com/?api-key=4177e73c-0edb-4e4a-9d22-4c99b9a3f8c1"

# Platform wallet private key from .env
PLATFORM_PRIVATE_KEY = "2KBD49gknMGpsVSJWuUFbTPLsVLd4kMEN8n8cBERvJFML8sBzavGqpHH14mYUwDWYHZ6EdTx1DzHxto6PUsUVpke"

async def check_platform_wallet():
    """Check if platform wallet has the 0.2 SOL"""
    client = AsyncClient(RPC_URL)
    
    try:
        # Decode private key
        pk_bytes = base58.b58decode(PLATFORM_PRIVATE_KEY)
        keypair = Keypair.from_bytes(pk_bytes)
        address = str(keypair.pubkey())
        
        print(f"\nPlatform Wallet:")
        print(f"Address: {address}")
        
        # Check balance
        response = await client.get_balance(keypair.pubkey())
        balance_sol = response.value / 1_000_000_000
        print(f"Balance: {balance_sol:.6f} SOL")
        
        # Check if this IS the old wallet
        old_wallet = "mDSm6bqKdKc8ARbsdAkkHKzDzAqERuFxMChiGmuUDaR"
        if address == old_wallet:
            print(f"✅ THIS IS YOUR OLD WALLET WITH 0.2 SOL!")
            return keypair, balance_sol
        else:
            print(f"Different wallet")
            
            # Check old wallet balance
            old_pubkey = Pubkey.from_string(old_wallet)
            resp = await client.get_balance(old_pubkey)
            old_balance = resp.value / 1_000_000_000
            print(f"\nOld Wallet ({old_wallet[:20]}...):")
            print(f"Balance: {old_balance:.6f} SOL")
            
            if balance_sol > 0:
                return keypair, balance_sol
            else:
                return None, 0
        
    except Exception as e:
        print(f"Error: {e}")
        return None, 0
    finally:
        await client.close()

async def transfer_to_new_wallet(keypair, amount_sol):
    """Transfer SOL to new wallet"""
    client = AsyncClient(RPC_URL)
    
    try:
        new_wallet_pubkey = Pubkey.from_string(NEW_WALLET)
        
        # Calculate transfer (leave rent)
        transfer_lamports = int((amount_sol - 0.000005) * 1_000_000_000)
        
        print(f"\n{'='*70}")
        print(f"TRANSFERRING")
        print(f"{'='*70}")
        print(f"From: {str(keypair.pubkey())}")
        print(f"To: {NEW_WALLET}")
        print(f"Amount: {transfer_lamports / 1e9:.6f} SOL")
        
        # Create transfer instruction
        ix = transfer(
            TransferParams(
                from_pubkey=keypair.pubkey(),
                to_pubkey=new_wallet_pubkey,
                lamports=transfer_lamports
            )
        )
        
        # Get recent blockhash
        recent_blockhash_resp = await client.get_latest_blockhash()
        recent_blockhash = recent_blockhash_resp.value.blockhash
        
        # Create transaction
        message = Message.new_with_blockhash([ix], keypair.pubkey(), recent_blockhash)
        transaction = Transaction([keypair], message, recent_blockhash)
        
        # Send
        result = await client.send_transaction(transaction)
        signature = str(result.value)
        
        print(f"\n✅ SUCCESS!")
        print(f"Signature: {signature}")
        print(f"Transferred: {transfer_lamports / 1e9:.6f} SOL")
        
        # Wait and verify
        await asyncio.sleep(3)
        
        new_balance_resp = await client.get_balance(new_wallet_pubkey)
        new_balance = new_balance_resp.value / 1_000_000_000
        
        print(f"\n✅ New wallet balance: {new_balance:.6f} SOL")
        print(f"\n🎉 Transfer complete! Check @gonehuntingbot with /balance")
        
    except Exception as e:
        print(f"❌ Transfer error: {e}")
    finally:
        await client.close()

async def main():
    print("\n" + "="*70)
    print("FUND CONSOLIDATION TOOL")
    print("="*70)
    print(f"New Wallet: {NEW_WALLET}")
    print("="*70)
    
    # Check platform wallet
    keypair, balance = await check_platform_wallet()
    
    if keypair and balance > 0.001:
        print(f"\n✅ Found {balance:.6f} SOL to transfer!")
        response = input(f"\nTransfer {balance:.6f} SOL to new wallet? (yes/no): ")
        
        if response.lower() == 'yes':
            await transfer_to_new_wallet(keypair, balance)
        else:
            print("Transfer cancelled")
    else:
        print("\n❌ No funds found to transfer")
        print("\nThe 0.2 SOL might be in user-specific encrypted wallets.")
        print("Those require the backup encryption key to decrypt.")

if __name__ == "__main__":
    asyncio.run(main())

