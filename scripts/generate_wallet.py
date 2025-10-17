#!/usr/bin/env python3
"""
Generate a new Solana wallet for the trading bot
IMPORTANT: Keep the private key secure!
"""

from solders.keypair import Keypair
import base58
import json

def generate_wallet():
    """Generate a new Solana keypair"""
    
    # Generate new keypair
    keypair = Keypair()
    
    # Get public key (address)
    public_key = str(keypair.pubkey())
    
    # Get private key (Base58 encoded for .env file)
    private_key_bytes = bytes(keypair)
    private_key_base58 = base58.b58encode(private_key_bytes).decode('utf-8')
    
    # Also get as array (for Phantom/Solflare import)
    private_key_array = list(private_key_bytes)
    
    print("=" * 70)
    print("NEW SOLANA WALLET GENERATED")
    print("=" * 70)
    print()
    print("Public Address (share this to receive SOL):")
    print(f"  {public_key}")
    print()
    print("Private Key for .env file (KEEP SECRET!):")
    print(f"  {private_key_base58}")
    print()
    print("Private Key as JSON array (for wallet import):")
    print(f"  {json.dumps(private_key_array)}")
    print()
    print("=" * 70)
    print("SECURITY WARNINGS")
    print("=" * 70)
    print("1. NEVER share your private key with anyone!")
    print("2. Store it securely (password manager, encrypted file)")
    print("3. Add to .env file as: WALLET_PRIVATE_KEY=<private_key>")
    print("4. Never commit .env to git")
    print("5. Fund this wallet with SOL before running the bot")
    print()
    print("=" * 70)
    print("NEXT STEPS")
    print("=" * 70)
    print("1. Copy the private key above")
    print("2. Open your .env file")
    print("3. Set: WALLET_PRIVATE_KEY=<private_key_from_above>")
    print("4. Send SOL to:", public_key)
    print("5. Run the bot!")
    print("=" * 70)
    
    return {
        'public_key': public_key,
        'private_key_base58': private_key_base58,
        'private_key_array': private_key_array
    }

if __name__ == "__main__":
    wallet = generate_wallet()

