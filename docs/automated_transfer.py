#!/usr/bin/env python3
"""
Automated fund transfer from old wallet to current trading wallet
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

async def transfer_funds_automated():
    """Automated transfer from old wallet to current trading wallet"""
    print("\nAUTOMATED FUND TRANSFER")
    print("=" * 50)
    
    config = get_config()
    client = AsyncClient(config.solana_rpc_url)
    
    try:
        # Old wallet (has 0.2 SOL)
        old_private_key_b58 = "2KBD49gknMGpsVSJWuUFbTPLsVLd4kMEN8n8cBERvJFML8sBzavGqpHH14mYUwDWYHZ6EdTx1DzHxto6PUsUVpke"
        old_private_key_bytes = base58.b58decode(old_private_key_b58)
        old_keypair = Keypair.from_bytes(old_private_key_bytes)
        old_address = str(old_keypair.pubkey())
        
        print(f"Old Wallet (Source): {old_address}")
        
        # Current trading wallet (destination)
        current_private_key_b58 = "2KBD49gknMGpsVSJWuUFbTPLsVLd4kMEN8n8cBERvJFML8sBzavGqpHH14mYUwDWYHZ6EdTx1DzHxto6PUsUVpke"
        current_private_key_bytes = base58.b58decode(current_private_key_b58)
        current_keypair = Keypair.from_bytes(current_private_key_bytes)
        current_address = str(current_keypair.pubkey())
        
        print(f"Current Wallet (Destination): {current_address}")
        
        # Check balances
        old_balance_response = await client.get_balance(old_keypair.pubkey())
        old_balance = old_balance_response.value / 1_000_000_000
        
        current_balance_response = await client.get_balance(current_keypair.pubkey())
        current_balance = current_balance_response.value / 1_000_000_000
        
        print(f"\nOld Wallet Balance: {old_balance:.6f} SOL")
        print(f"Current Wallet Balance: {current_balance:.6f} SOL")
        
        if old_balance == 0:
            print("No funds to transfer!")
            return
        
        # Calculate transfer amount (keep 0.01 SOL for fees)
        transfer_amount_sol = old_balance - 0.01
        transfer_amount_lamports = int(transfer_amount_sol * 1_000_000_000)
        
        print(f"\nTransferring {transfer_amount_sol:.6f} SOL")
        print(f"Keeping 0.01 SOL for transaction fees")
        
        # Get recent blockhash
        recent_blockhash = await client.get_latest_blockhash()
        
        # Create transfer instruction
        transfer_instruction = transfer(
            TransferParams(
                from_pubkey=old_keypair.pubkey(),
                to_pubkey=current_keypair.pubkey(),
                lamports=transfer_amount_lamports
            )
        )
        
        # Create transaction
        message = MessageV0.try_compile(
            payer=old_keypair.pubkey(),
            instructions=[transfer_instruction],
            address_lookup_table_accounts=[],
            recent_blockhash=recent_blockhash.value.blockhash
        )
        
        transaction = Transaction(message, [old_keypair])
        
        # Send transaction
        print("\nSending transaction...")
        result = await client.send_transaction(transaction)
        
        print(f"Transaction signature: {result.value}")
        print("Waiting for confirmation...")
        
        # Wait for confirmation
        confirmation = await client.confirm_transaction(result.value)
        
        if confirmation.value[0].confirmation_status:
            print("✅ Transfer successful!")
            
            # Check new balances
            new_old_balance_response = await client.get_balance(old_keypair.pubkey())
            new_old_balance = new_old_balance_response.value / 1_000_000_000
            
            new_current_balance_response = await client.get_balance(current_keypair.pubkey())
            new_current_balance = new_current_balance_response.value / 1_000_000_000
            
            print(f"\nNew Balances:")
            print(f"Old Wallet: {new_old_balance:.6f} SOL")
            print(f"Current Wallet: {new_current_balance:.6f} SOL")
            
            print(f"\n🎉 SUCCESS! Your trading wallet now has {new_current_balance:.6f} SOL!")
            print("You can now start the bot and begin automated trading!")
            
        else:
            print("❌ Transfer failed!")
            
    except Exception as e:
        print(f"Error during transfer: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await client.close()

async def main():
    print("AUTOMATED FUND TRANSFER")
    print("=" * 60)
    print("Transferring funds from old wallet to current trading wallet")
    
    await transfer_funds_automated()
    
    print("\n" + "=" * 60)
    print("NEXT STEPS")
    print("=" * 60)
    print("1. Start the bot: python scripts/run_bot.py")
    print("2. Use /autostart in Telegram to begin auto-trading")
    print("3. Monitor with: python scripts/monitor_wallet_scanning_24hr.py")

if __name__ == "__main__":
    asyncio.run(main())
