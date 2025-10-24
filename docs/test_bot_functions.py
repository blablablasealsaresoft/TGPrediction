#!/usr/bin/env python3
"""
Comprehensive End-to-End Testing for Trading Bot
Tests all core functionality systematically
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.config import get_config
from src.modules.database import DatabaseManager
from solana.rpc.async_api import AsyncClient
from solders.pubkey import Pubkey

async def test_all_functions():
    print("COMPREHENSIVE END-TO-END TESTING")
    print("=" * 50)
    
    # Test 1: Configuration Loading
    print("\n1. Testing Configuration Loading...")
    try:
        config = get_config()
        print("+ Config loaded successfully")
        print(f"   - Telegram Bot Token: {config.telegram_bot_token[:10]}...")
        print(f"   - Admin Chat ID: {config.admin_chat_id}")
        print(f"   - Solana RPC: {config.solana_rpc_url}")
        print(f"   - Database URL: {config.database_url}")
    except Exception as e:
        print(f"- Config loading failed: {e}")
        return False
    
    # Test 2: Database Connection
    print("\n2. Testing Database Connection...")
    try:
        db_manager = DatabaseManager(config.database_url)
        await db_manager.init_db()
        print("+ Database initialized successfully")
        
        # Test database operations
        from sqlalchemy import text
        async with db_manager.async_session() as session:
            result = await session.execute(text('SELECT 1'))
            print("+ Database query executed successfully")
        
        await db_manager.dispose()
    except Exception as e:
        print(f"- Database test failed: {e}")
        return False
    
    # Test 3: Solana RPC Connection
    print("\n3. Testing Solana RPC Connection...")
    try:
        client = AsyncClient(config.solana_rpc_url)
        
        # Test basic RPC call
        version = await client.get_version()
        solana_version = version.value.solana_core if hasattr(version.value, 'solana_core') else 'Unknown'
        print("+ Solana RPC connected successfully")
        print(f"   - Solana version: {solana_version}")
        
        # Test account lookup
        test_pubkey = Pubkey.from_string('11111111111111111111111111111112')
        account_info = await client.get_account_info(test_pubkey)
        print("+ Account info retrieval working")
        
        await client.close()
    except Exception as e:
        print(f"- Solana RPC test failed: {e}")
        return False
    
    # Test 4: Core Module Imports
    print("\n4. Testing Core Module Imports...")
    try:
        from src.modules.wallet_manager import UserWalletManager
        from src.modules.token_sniper import AutoSniper
        from src.modules.ai_strategy_engine import MLPredictionEngine
        from src.modules.elite_protection import EliteProtectionSystem
        from src.modules.social_trading import SocialTradingMarketplace
        from src.modules.wallet_intelligence import WalletIntelligenceEngine
        print("+ All core modules imported successfully")
    except Exception as e:
        print(f"- Module import test failed: {e}")
        return False
    
    # Test 5: Bot Initialization
    print("\n5. Testing Bot Initialization...")
    try:
        from src.bot.main import RevolutionaryTradingBot
        
        # Reinitialize database for bot
        db_manager = DatabaseManager(config.database_url)
        await db_manager.init_db()
        
        client = AsyncClient(config.solana_rpc_url)
        
        bot = RevolutionaryTradingBot(config, db_manager, solana_client=client)
        print("+ Bot initialized successfully")
        
        await client.close()
        await db_manager.dispose()
    except Exception as e:
        print(f"- Bot initialization test failed: {e}")
        return False
    
    print("\nALL CORE TESTS PASSED!")
    print("=" * 50)
    return True

async def test_telegram_functionality():
    """Test Telegram bot specific functionality"""
    print("\n6. Testing Telegram Bot Functionality...")
    try:
        from telegram import Bot
        from telegram.ext import Application
        
        config = get_config()
        
        # Test bot creation
        bot = Bot(token=config.telegram_bot_token)
        print("+ Telegram bot created successfully")
        
        # Test bot info
        bot_info = await bot.get_me()
        print(f"+ Bot info retrieved: @{bot_info.username}")
        
        # Test application creation
        app = Application.builder().token(config.telegram_bot_token).build()
        print("+ Telegram application created successfully")
        
        await app.shutdown()
        
    except Exception as e:
        print(f"- Telegram functionality test failed: {e}")
        return False
    
    return True

async def test_wallet_operations():
    """Test wallet creation and management"""
    print("\n7. Testing Wallet Operations...")
    try:
        from src.modules.wallet_manager import UserWalletManager
        
        config = get_config()
        db_manager = DatabaseManager(config.database_url)
        await db_manager.init_db()
        
        wallet_manager = UserWalletManager(db_manager, config)
        
        # Test wallet creation
        test_user_id = 999999999
        wallet_address = await wallet_manager.get_or_create_user_wallet(test_user_id)
        print(f"+ Wallet created: {wallet_address}")
        
        # Test wallet retrieval
        retrieved_wallet = await wallet_manager.get_user_wallet_address(test_user_id)
        print(f"+ Wallet retrieved: {retrieved_wallet}")
        
        await db_manager.dispose()
        
    except Exception as e:
        print(f"- Wallet operations test failed: {e}")
        return False
    
    return True

async def test_ai_analysis():
    """Test AI analysis functionality"""
    print("\n8. Testing AI Analysis...")
    try:
        from src.modules.ai_strategy_engine import MLPredictionEngine
        
        ai_engine = MLPredictionEngine()
        
        # Test basic analysis
        test_data = {
            'price_change_24h': 0.05,
            'volume_24h': 1000000,
            'market_cap': 5000000,
            'holders': 1000,
            'liquidity': 2000000
        }
        
        analysis = await ai_engine.predict_token_success(test_data)
        print(f"+ AI analysis completed: {analysis}")
        
    except Exception as e:
        print(f"- AI analysis test failed: {e}")
        return False
    
    return True

async def main():
    """Run all tests"""
    print("Starting comprehensive bot testing...")
    
    # Core functionality tests
    core_tests = await test_all_functions()
    
    # Telegram functionality tests
    telegram_tests = await test_telegram_functionality()
    
    # Wallet operations tests
    wallet_tests = await test_wallet_operations()
    
    # AI analysis tests
    ai_tests = await test_ai_analysis()
    
    # Summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    print(f"Core Functionality: {'+ PASS' if core_tests else '- FAIL'}")
    print(f"Telegram Functionality: {'+ PASS' if telegram_tests else '- FAIL'}")
    print(f"Wallet Operations: {'+ PASS' if wallet_tests else '- FAIL'}")
    print(f"AI Analysis: {'+ PASS' if ai_tests else '- FAIL'}")
    
    all_passed = core_tests and telegram_tests and wallet_tests and ai_tests
    
    if all_passed:
        print("\nALL TESTS PASSED! Bot is ready for production!")
    else:
        print("\n- Some tests failed. Please check the errors above.")
    
    return all_passed

if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)
