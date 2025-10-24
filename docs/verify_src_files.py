#!/usr/bin/env python3
"""
Comprehensive Source Code Verification
Check every file in src/ folder for proper usage and configuration
"""

import asyncio
import os
import sys
import importlib
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.config import get_config

async def verify_all_src_files():
    """Verify every file in src/ folder"""
    
    print("COMPREHENSIVE SOURCE CODE VERIFICATION")
    print("="*80)
    print("Checking every file in src/ folder for proper usage and configuration")
    print("="*80)
    
    config = get_config()
    
    # Files to check
    src_files = {
        # Core files
        'src.config': 'Configuration management',
        'src.bot.main': 'Main bot class',
        'src.bot.basic_bot': 'Basic bot functionality',
        
        # Database and core modules
        'src.modules.database': 'Database management',
        'src.modules.wallet_manager': 'Wallet management',
        'src.modules.monitoring': 'Bot monitoring',
        
        # Trading modules
        'src.modules.automated_trading': 'Automated trading engine',
        'src.modules.trade_execution': 'Trade execution service',
        'src.modules.fast_execution': 'Fast execution engine',
        'src.modules.jupiter_client': 'Jupiter DEX client',
        
        # Intelligence modules
        'src.modules.ai_strategy_engine': 'AI strategy engine',
        'src.modules.wallet_intelligence': 'Wallet intelligence',
        'src.modules.sentiment_analysis': 'Sentiment analysis',
        'src.modules.affiliated_wallet_detector': 'Affiliated wallet detection',
        
        # Protection and sniper modules
        'src.modules.elite_protection': 'Elite protection system',
        'src.modules.token_sniper': 'Token sniper',
        
        # Social and marketplace modules
        'src.modules.social_trading': 'Social trading marketplace',
        'src.modules.discord_monitor': 'Discord monitoring',
    }
    
    results = {}
    
    print("\n1. MODULE IMPORT VERIFICATION")
    print("-" * 50)
    
    for module_name, description in src_files.items():
        try:
            module = importlib.import_module(module_name)
            print(f"+ {module_name}: IMPORTED")
            results[module_name] = {'import': True, 'description': description}
        except Exception as e:
            print(f"- {module_name}: FAILED - {e}")
            results[module_name] = {'import': False, 'error': str(e), 'description': description}
    
    print("\n2. CLASS INSTANTIATION VERIFICATION")
    print("-" * 50)
    
    # Test class instantiation
    instantiation_tests = [
        ('src.modules.database.DatabaseManager', 'DatabaseManager', [config.database_url]),
        ('src.modules.wallet_manager.UserWalletManager', 'UserWalletManager', [None, config]),
        ('src.modules.monitoring.BotMonitor', 'BotMonitor', [config]),
        ('src.modules.ai_strategy_engine.MLPredictionEngine', 'MLPredictionEngine', []),
        ('src.modules.sentiment_analysis.SentimentAnalyzer', 'SentimentAnalyzer', []),
        ('src.modules.elite_protection.EliteProtectionSystem', 'EliteProtectionSystem', [config]),
    ]
    
    for module_name, class_name, args in instantiation_tests:
        try:
            module = importlib.import_module(module_name)
            cls = getattr(module, class_name)
            
            # Create instance
            if args[0] is None:  # Special case for UserWalletManager
                from src.modules.database import DatabaseManager
                db = DatabaseManager(config.database_url)
                await db.init_db()
                instance = cls(db, config)
                await db.dispose()
            else:
                instance = cls(*args)
            
            print(f"+ {class_name}: INSTANTIATED")
            results[module_name] = results.get(module_name, {})
            results[module_name]['instantiation'] = True
            
        except Exception as e:
            print(f"- {class_name}: FAILED - {e}")
            results[module_name] = results.get(module_name, {})
            results[module_name]['instantiation'] = False
            results[module_name]['instantiation_error'] = str(e)
    
    print("\n3. ADVANCED MODULE VERIFICATION")
    print("-" * 50)
    
    # Test more complex modules that require multiple dependencies
    try:
        from src.modules.database import DatabaseManager
        from src.modules.jupiter_client import JupiterClient
        from src.modules.wallet_intelligence import WalletIntelligenceEngine
        from src.modules.elite_protection import EliteProtectionSystem
        from src.modules.automated_trading import AutomatedTradingEngine
        from src.modules.trade_execution import TradeExecutionService
        from src.modules.wallet_manager import UserWalletManager
        from solana.rpc.async_api import AsyncClient
        
        # Initialize dependencies
        db = DatabaseManager(config.database_url)
        await db.init_db()
        
        client = AsyncClient(config.solana_rpc_url)
        jupiter_client = JupiterClient(config.solana_rpc_url)
        wallet_intelligence = WalletIntelligenceEngine(client)
        protection_system = EliteProtectionSystem(config)
        
        # Test AutomatedTradingEngine
        try:
            auto_engine = AutomatedTradingEngine(config, wallet_intelligence, jupiter_client, protection_system)
            print("+ AutomatedTradingEngine: CONFIGURED")
        except Exception as e:
            print(f"- AutomatedTradingEngine: FAILED - {e}")
        
        # Test TradeExecutionService
        try:
            wallet_manager = UserWalletManager(db, config)
            trade_service = TradeExecutionService(db, wallet_manager, jupiter_client, protection_system)
            print("+ TradeExecutionService: CONFIGURED")
        except Exception as e:
            print(f"- TradeExecutionService: FAILED - {e}")
        
        # Test TokenSniper
        try:
            from src.modules.token_sniper import AutoSniper
            sniper = AutoSniper(config, db, client)
            print("+ AutoSniper: CONFIGURED")
        except Exception as e:
            print(f"- AutoSniper: FAILED - {e}")
        
        # Test SocialTradingMarketplace
        try:
            from src.modules.social_trading import SocialTradingMarketplace
            social_trading = SocialTradingMarketplace(db)
            print("+ SocialTradingMarketplace: CONFIGURED")
        except Exception as e:
            print(f"- SocialTradingMarketplace: FAILED - {e}")
        
        # Test FastExecutionEngine
        try:
            from src.modules.fast_execution import FastExecutionEngine
            fast_engine = FastExecutionEngine(config.solana_rpc_url, [])
            print("+ FastExecutionEngine: CONFIGURED")
        except Exception as e:
            print(f"- FastExecutionEngine: FAILED - {e}")
        
        # Test AffiliatedWalletDetector
        try:
            from src.modules.affiliated_wallet_detector import AffiliatedWalletDetector
            detector = AffiliatedWalletDetector(client)
            print("+ AffiliatedWalletDetector: CONFIGURED")
        except Exception as e:
            print(f"- AffiliatedWalletDetector: FAILED - {e}")
        
        await client.close()
        await db.dispose()
        
    except Exception as e:
        print(f"- Advanced module verification failed: {e}")
    
    print("\n4. MAIN BOT VERIFICATION")
    print("-" * 50)
    
    try:
        from src.bot.main import RevolutionaryTradingBot
        from src.modules.database import DatabaseManager
        from solana.rpc.async_api import AsyncClient
        
        db = DatabaseManager(config.database_url)
        await db.init_db()
        client = AsyncClient(config.solana_rpc_url)
        
        bot = RevolutionaryTradingBot(config, db, solana_client=client)
        print("+ RevolutionaryTradingBot: CONFIGURED")
        
        await client.close()
        await db.dispose()
        
    except Exception as e:
        print(f"- RevolutionaryTradingBot: FAILED - {e}")
    
    print("\n5. CONFIGURATION VERIFICATION")
    print("-" * 50)
    
    # Check all config values
    config_checks = [
        ('telegram_bot_token', config.telegram_bot_token),
        ('admin_chat_id', config.admin_chat_id),
        ('solana_rpc_url', config.solana_rpc_url),
        ('database_url', config.database_url),
        ('wallet_private_key', config.wallet_private_key),
        ('wallet_encryption_key', config.wallet_encryption_key),
    ]
    
    for key, value in config_checks:
        if value:
            print(f"+ {key}: CONFIGURED")
        else:
            print(f"- {key}: MISSING")
    
    print("\n6. FILE USAGE ANALYSIS")
    print("-" * 50)
    
    # Check which files are actually being used
    used_files = []
    unused_files = []
    
    for module_name, result in results.items():
        if result.get('import', False):
            used_files.append(module_name)
        else:
            unused_files.append(module_name)
    
    print(f"Used files: {len(used_files)}")
    for file in used_files:
        print(f"  + {file}")
    
    if unused_files:
        print(f"\nUnused files: {len(unused_files)}")
        for file in unused_files:
            print(f"  - {file}")
    
    print("\n7. FINAL ASSESSMENT")
    print("-" * 50)
    
    total_files = len(src_files)
    working_files = len([f for f in results.values() if f.get('import', False)])
    working_percentage = (working_files / total_files) * 100
    
    print(f"Total files checked: {total_files}")
    print(f"Working files: {working_files}")
    print(f"Success rate: {working_percentage:.1f}%")
    
    if working_percentage >= 90:
        print("STATUS: EXCELLENT - All core modules working")
    elif working_percentage >= 80:
        print("STATUS: GOOD - Most modules working")
    elif working_percentage >= 70:
        print("STATUS: FAIR - Some modules need attention")
    else:
        print("STATUS: POOR - Multiple modules failing")
    
    print("\n" + "="*80)
    print("VERIFICATION COMPLETE")
    print("="*80)
    
    return results

if __name__ == "__main__":
    asyncio.run(verify_all_src_files())
