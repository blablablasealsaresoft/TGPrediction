import asyncio
import os
from dotenv import load_dotenv
load_dotenv()

from solana.rpc.async_api import AsyncClient
from solders.keypair import Keypair

async def main():
    wallet_key = os.getenv('WALLET_PRIVATE_KEY')
    rpc_url = os.getenv('SOLANA_RPC_URL')
    
    keypair = Keypair.from_base58_string(wallet_key)
    client = AsyncClient(rpc_url)
    
    response = await client.get_balance(keypair.pubkey())
    balance_sol = response.value / 1e9
    
    print(f"\nWallet from WALLET_PRIVATE_KEY:")
    print(f"Address: {keypair.pubkey()}")
    print(f"Balance: {balance_sol:.6f} SOL")
    
    if balance_sol > 0:
        print(f"\n✅ This wallet HAS funds!")
        print(f"\nTo use this wallet in the bot, run:")
        print(f"python scripts/use_platform_wallet_simple.py")
    else:
        print(f"\n❌ This wallet has NO funds!")
        print(f"\nYou need to send SOL to this address.")
    
    await client.close()

asyncio.run(main())

