#!/usr/bin/env python3
"""
Transfer all funds from old wallets to new wallet
Decrypts old wallets with backup key and sends SOL to new address
"""

import asyncio
import sys
import sqlite3
from pathlib import Path
from cryptography.fernet import Fernet

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from solana.rpc.async_api import AsyncClient
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.system_program import TransferParams, transfer
from solders.transaction import Transaction
from solders.message import Message
from src.config import get_config

# Backup encryption key that was used for old wallets
BACKUP_ENCRYPTION_KEY = b"kzqwCzrcVTdfOdWSUw4-eDm-QWtseuSoY9KZKIR4_08"

# New wallet to send all funds to
NEW_WALLET = "Fs2bohyETVLnSdo2v2JyKCoipMS8c5qhBqkTMhkjCgX"

async def transfer_from_old_wallets():
    """Transfer funds from all old wallets"""
    
    print("\n" + "="*70)
    print("TRANSFERRING FUNDS FROM OLD WALLETS")
    print("="*70)
    
    config = get_config()
    client = AsyncClient(config.solana_rpc_url)
    
    # Initialize Fernet with backup key
    try:
        fernet = Fernet(BACKUP_ENCRYPTION_KEY)
        print("✅ Backup encryption key loaded")
    except Exception as e:
        print(f"❌ Could not load backup encryption key: {e}")
        return
    
    # Connect to old database
    try:
        conn = sqlite3.connect('trading_bot.db.old')
        cursor = conn.cursor()
        cursor.execute('SELECT user_id, public_key, encrypted_private_key FROM user_wallets')
        old_wallets = cursor.fetchall()
        conn.close()
        
        print(f"✅ Found {len(old_wallets)} old wallets\n")
    except Exception as e:
        print(f"❌ Could not read old database: {e}")
        return
    
    new_wallet_pubkey = Pubkey.from_string(NEW_WALLET)
    total_transferred = 0
    
    # Process each old wallet
    for user_id, public_key, encrypted_private_key in old_wallets:
        print(f"\n{'='*70}")
        print(f"Wallet: {public_key[:20]}...")
        print(f"User: {user_id}")
        
        try:
            # Check balance first
            pubkey = Pubkey.from_string(public_key)
            response = await client.get_balance(pubkey)
            balance_lamports = response.value
            balance_sol = balance_lamports / 1_000_000_000
            
            print(f"Balance: {balance_sol:.6f} SOL")
            
            if balance_sol < 0.001:  # Skip if less than 0.001 SOL
                print("⏭️  Skipping (insufficient balance)")
                continue
            
            # Decrypt private key
            try:
                decrypted_bytes = fernet.decrypt(encrypted_private_key.encode())
                private_key_bytes = decrypted_bytes
                
                # Create keypair
                keypair = Keypair.from_bytes(private_key_bytes)
                
                print(f"✅ Decrypted private key")
                
                # Verify it matches
                if str(keypair.pubkey()) != public_key:
                    print(f"❌ Keypair mismatch!")
                    continue
                
                # Calculate transfer amount (leave 0.000005 for rent)
                transfer_lamports = balance_lamports - 5000
                transfer_sol = transfer_lamports / 1_000_000_000
                
                if transfer_lamports <= 0:
                    print("⏭️  Balance too low to transfer")
                    continue
                
                print(f"💸 Transferring {transfer_sol:.6f} SOL to new wallet...")
                
                # Create transfer instruction
                transfer_ix = transfer(
                    TransferParams(
                        from_pubkey=keypair.pubkey(),
                        to_pubkey=new_wallet_pubkey,
                        lamports=transfer_lamports
                    )
                )
                
                # Get recent blockhash
                recent_blockhash_resp = await client.get_latest_blockhash()
                recent_blockhash = recent_blockhash_resp.value.blockhash
                
                # Create and sign transaction
                message = Message.new_with_blockhash(
                    [transfer_ix],
                    keypair.pubkey(),
                    recent_blockhash
                )
                transaction = Transaction([keypair], message, recent_blockhash)
                
                # Send transaction
                result = await client.send_transaction(transaction)
                signature = str(result.value)
                
                print(f"✅ TRANSFERRED! Signature: {signature[:20]}...")
                print(f"   Amount: {transfer_sol:.6f} SOL")
                
                total_transferred += transfer_sol
                
                # Wait for confirmation
                await asyncio.sleep(2)
                
            except Exception as decrypt_error:
                print(f"❌ Could not decrypt wallet: {decrypt_error}")
                continue
                
        except Exception as e:
            print(f"❌ Error processing wallet: {e}")
            continue
    
    # Final summary
    print(f"\n{'='*70}")
    print(f"TRANSFER COMPLETE")
    print(f"{'='*70}")
    print(f"Total Transferred: {total_transferred:.6f} SOL")
    print(f"New Wallet: {NEW_WALLET}")
    print(f"\nCheck your new balance with: /balance on @gonehuntingbot")
    print(f"{'='*70}\n")
    
    await client.close()

if __name__ == "__main__":
    asyncio.run(transfer_from_old_wallets())

