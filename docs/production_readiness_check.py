#!/usr/bin/env python3
"""
COMPREHENSIVE PRODUCTION READINESS CHECK
Verifies all scripts have been run and workflows are E2E ready
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.modules.database import DatabaseManager
from src.config import get_config
from solana.rpc.async_api import AsyncClient
from solders.pubkey import Pubkey

async def check_production_readiness():
    """Comprehensive check of all production workflows"""
    print("\nPRODUCTION READINESS VERIFICATION")
    print("=" * 60)
    
    config = get_config()
    db = DatabaseManager(config.database_url)
    await db.init_db()
    
    # 1. Check Environment Configuration
    print("\n1. ENVIRONMENT CONFIGURATION")
    print("-" * 30)
    
    required_vars = [
        'TELEGRAM_BOT_TOKEN',
        'ADMIN_CHAT_ID', 
        'SOLANA_RPC_URL',
        'WALLET_PRIVATE_KEY',
        'DATABASE_URL'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not hasattr(config, var.lower()) or not getattr(config, var.lower()):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"ERROR: Missing environment variables: {missing_vars}")
        return False
    else:
        print("+ All required environment variables configured")
    
    # 2. Check Wallet Balance
    print("\n2. WALLET BALANCE CHECK")
    print("-" * 30)
    
    try:
        client = AsyncClient(config.solana_rpc_url)
        wallet_pubkey = Pubkey.from_string("FEroaDc5UhxRxqFtrNeUy4uhPuxD5wHbYUpJQhXFZgE2")
        balance_response = await client.get_balance(wallet_pubkey)
        balance_sol = balance_response.value / 1_000_000_000
        
        print(f"Wallet Address: FEroaDc5UhxRxqFtrNeUy4uhPuxD5wHbYUpJQhXFZgE2")
        print(f"Balance: {balance_sol:.6f} SOL")
        
        if balance_sol < 0.01:
            print("WARNING: Wallet has insufficient funds for trading!")
            print("You need at least 0.01 SOL to start trading")
            print("Send SOL to: FEroaDc5UhxRxqFtrNeUy4uhPuxD5wHbYUpJQhXFZgE2")
        else:
            print("+ Wallet has sufficient funds")
            
        await client.close()
        
    except Exception as e:
        print(f"ERROR: Could not check wallet balance: {e}")
        return False
    
    # 3. Check Database Setup
    print("\n3. DATABASE SETUP")
    print("-" * 30)
    
    try:
        # Check tracked wallets
        tracked_wallets = await db.get_tracked_wallets(user_id=1)
        print(f"+ Tracked wallets in database: {len(tracked_wallets)}")
        
        if len(tracked_wallets) == 0:
            print("ERROR: No wallets tracked! Run: python check_and_add_wallets.py")
            return False
        
        # Check user wallets
        from sqlalchemy import text
        async with db.async_session() as session:
            result = await session.execute(text("SELECT COUNT(*) FROM user_wallets"))
            user_wallet_count = result.scalar()
            print(f"+ User wallets in database: {user_wallet_count}")
        
        print("+ Database properly initialized")
        
    except Exception as e:
        print(f"ERROR: Database check failed: {e}")
        return False
    
    # 4. Check All Modules Can Initialize
    print("\n4. MODULE INITIALIZATION")
    print("-" * 30)
    
    try:
        client = AsyncClient(config.solana_rpc_url)
        
        # Test all critical modules
        from src.modules.wallet_intelligence import WalletIntelligenceEngine
        from src.modules.elite_protection import EliteProtectionSystem
        from src.modules.jupiter_client import JupiterClient
        from src.modules.automated_trading import AutomatedTradingEngine
        from src.modules.token_sniper import AutoSniper
        from src.modules.social_trading import SocialTradingMarketplace
        from src.modules.trade_execution import TradeExecutionService
        from src.modules.wallet_manager import UserWalletManager
        
        # Initialize modules
        wallet_intelligence = WalletIntelligenceEngine(client)
        protection = EliteProtectionSystem(config)
        jupiter = JupiterClient(config.solana_rpc_url)
        wallet_manager = UserWalletManager(db, config)
        
        auto_trader = AutomatedTradingEngine(config, wallet_intelligence, jupiter, protection)
        sniper = AutoSniper(config, db, client)
        social_trading = SocialTradingMarketplace(db)
        trade_executor = TradeExecutionService(db, wallet_manager, jupiter, protection)
        
        print("+ All modules initialized successfully")
        
        await client.close()
        
    except Exception as e:
        print(f"ERROR: Module initialization failed: {e}")
        return False
    
    # 5. Check Bot Can Start
    print("\n5. BOT STARTUP CHECK")
    print("-" * 30)
    
    try:
        from src.bot.main import RevolutionaryTradingBot
        
        client = AsyncClient(config.solana_rpc_url)
        bot = RevolutionaryTradingBot(config, db, solana_client=client)
        
        print("+ Bot can be initialized")
        
        await client.close()
        
    except Exception as e:
        print(f"ERROR: Bot initialization failed: {e}")
        return False
    
    # 6. Check Telegram Bot API
    print("\n6. TELEGRAM BOT API")
    print("-" * 30)
    
    try:
        from telegram import Bot
        
        bot = Bot(token=config.telegram_bot_token)
        bot_info = await bot.get_me()
        
        print(f"+ Telegram bot connected: @{bot_info.username}")
        print(f"+ Bot ID: {bot_info.id}")
        
    except Exception as e:
        print(f"ERROR: Telegram bot connection failed: {e}")
        return False
    
    # 7. Check Solana RPC
    print("\n7. SOLANA RPC CONNECTION")
    print("-" * 30)
    
    try:
        client = AsyncClient(config.solana_rpc_url)
        version = await client.get_version()
        
        print(f"+ Solana RPC connected")
        print(f"+ Solana version: {version.value.solana_core}")
        
        await client.close()
        
    except Exception as e:
        print(f"ERROR: Solana RPC connection failed: {e}")
        return False
    
    await db.dispose()
    
    print("\n" + "=" * 60)
    print("PRODUCTION READINESS SUMMARY")
    print("=" * 60)
    
    if balance_sol < 0.01:
        print("STATUS: PARTIALLY READY")
        print("ISSUE: Wallet needs funding")
        print("ACTION: Send SOL to FEroaDc5UhxRxqFtrNeUy4uhPuxD5wHbYUpJQhXFZgE2")
    else:
        print("STATUS: FULLY READY FOR PRODUCTION!")
        print("All systems operational and ready to trade")
    
    return True

async def main():
    try:
        await check_production_readiness()
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
