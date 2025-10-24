#!/usr/bin/env python3
"""
Complete Trading Bot Command Guide and Monitoring
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.config import get_config

def print_command_guide():
    """Print complete command guide"""
    print("\n" + "="*80)
    print("🚀 SOLANA TRADING BOT - COMPLETE COMMAND GUIDE")
    print("="*80)
    
    print("\n📱 TELEGRAM BOT COMMANDS:")
    print("-" * 50)
    
    print("\n🔐 WALLET COMMANDS:")
    print("  /wallet          - View your trading wallet")
    print("  /deposit         - Get deposit address and instructions")
    print("  /balance         - Check your SOL balance")
    print("  /export_wallet   - Export your wallet private key")
    
    print("\n🤖 AUTOMATED TRADING:")
    print("  /autostart       - Start automated trading (MAIN COMMAND)")
    print("  /autostop        - Stop automated trading")
    print("  /autostatus      - Check automated trading status")
    
    print("\n🎯 SNIPING COMMANDS:")
    print("  /snipe           - View auto-sniper status")
    print("  /snipe_enable    - Enable auto-sniper")
    print("  /snipe_disable    - Disable auto-sniper")
    print("  /snipe_settings  - Configure sniper settings")
    
    print("\n🧠 AI ANALYSIS:")
    print("  /ai_analyze <token> - Analyze any token with AI")
    print("  /analyze <token>    - Same as above (shortcut)")
    print("  /ai <token>         - Same as above (shortcut)")
    
    print("\n👥 SOCIAL TRADING:")
    print("  /leaderboard     - View top traders")
    print("  /trending        - View trending tokens")
    print("  /community <token> - Community sentiment analysis")
    print("  /copy_trader <id>  - Copy a specific trader")
    print("  /stop_copy       - Stop copying traders")
    
    print("\n📊 TRADING COMMANDS:")
    print("  /buy <token> <amount> - Buy tokens manually")
    print("  /sell <token> <amount> - Sell tokens manually")
    print("  /positions       - View open positions")
    print("  /portfolio       - View your portfolio")
    
    print("\n📈 STATS & REWARDS:")
    print("  /my_stats        - Your trading statistics")
    print("  /stats           - Same as above (shortcut)")
    print("  /rewards         - View your rewards and points")
    
    print("\n🎮 STRATEGY MARKETPLACE:")
    print("  /strategies      - Browse trading strategies")
    print("  /publish_strategy - Publish your strategy")
    print("  /buy_strategy <id> - Buy a strategy")
    
    print("\n🔧 UTILITY COMMANDS:")
    print("  /help            - Show this help")
    print("  /start           - Welcome message")
    print("  /settings        - Configure bot settings")
    
    print("\n" + "="*80)
    print("🎯 RECOMMENDED COMMAND ORDER:")
    print("="*80)
    
    print("\n1️⃣ FIRST TIME SETUP:")
    print("  1. /wallet        - Check your wallet")
    print("  2. /balance       - Verify 0.2 SOL balance")
    print("  3. /autostart     - Start automated trading")
    
    print("\n2️⃣ DAILY MONITORING:")
    print("  1. /autostatus    - Check if auto-trading is running")
    print("  2. /my_stats      - View your performance")
    print("  3. /positions     - Check open positions")
    print("  4. /leaderboard   - See top performers")
    
    print("\n3️⃣ ADVANCED FEATURES:")
    print("  1. /snipe_enable  - Enable auto-sniper")
    print("  2. /ai_analyze <token> - Analyze specific tokens")
    print("  3. /copy_trader <id> - Copy specific traders")
    print("  4. /strategies    - Browse strategies")
    
    print("\n4️⃣ EMERGENCY COMMANDS:")
    print("  1. /autostop      - Stop all automated trading")
    print("  2. /sell <token> <amount> - Manual sell")
    print("  3. /positions     - Check what you own")
    
    print("\n" + "="*80)
    print("📊 MONITORING COMMANDS:")
    print("="*80)
    
    print("\n🖥️ TERMINAL MONITORING:")
    print("  python scripts/monitor_wallet_scanning_24hr.py")
    print("  python scripts/view_logs.py")
    print("  python scripts/bot_status.py")
    print("  python scripts/check_trading_activity.py")
    
    print("\n📱 TELEGRAM MONITORING:")
    print("  /autostatus      - Check bot status")
    print("  /my_stats        - View performance")
    print("  /positions       - Check positions")
    
    print("\n" + "="*80)
    print("⚠️ IMPORTANT NOTES:")
    print("="*80)
    
    print("\n• Start with /autostart to begin automated trading")
    print("• Monitor with /autostatus regularly")
    print("• Use /my_stats to track performance")
    print("• Emergency stop with /autostop if needed")
    print("• Your bot monitors 443 wallets 24/7")
    print("• AI analyzes every trade before copying")
    print("• Elite protection prevents scams")
    
    print("\n" + "="*80)
    print("🚀 READY TO START TRADING!")
    print("="*80)

async def monitor_bot_status():
    """Monitor bot status"""
    print("\n🤖 BOT STATUS MONITORING")
    print("="*50)
    
    try:
        config = get_config()
        
        # Check if bot is running
        import subprocess
        result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq python.exe'], 
                              capture_output=True, text=True)
        
        if 'python.exe' in result.stdout:
            print("✅ Bot is running (Python processes detected)")
        else:
            print("❌ Bot is not running")
        
        # Check database
        from src.modules.database import DatabaseManager
        db = DatabaseManager(config.database_url)
        await db.init_db()
        
        # Check tracked wallets
        tracked_wallets = await db.get_tracked_wallets(user_id=1)
        print(f"✅ Tracked wallets: {len(tracked_wallets)}")
        
        # Check user wallet
        from sqlalchemy import select
        from src.modules.database import UserWallet
        
        async with db.async_session() as session:
            result = await session.execute(select(UserWallet).where(UserWallet.user_id == config.admin_chat_id))
            user_wallet = result.scalar_one_or_none()
            
            if user_wallet:
                print(f"✅ User wallet: {user_wallet.public_key}")
                
                # Check balance
                from solana.rpc.async_api import AsyncClient
                from solders.pubkey import Pubkey
                
                client = AsyncClient(config.solana_rpc_url)
                pubkey = Pubkey.from_string(user_wallet.public_key)
                balance_response = await client.get_balance(pubkey)
                balance_sol = balance_response.value / 1_000_000_000
                
                print(f"✅ Wallet balance: {balance_sol:.6f} SOL")
                
                await client.close()
            else:
                print("❌ No user wallet found")
        
        await db.dispose()
        
    except Exception as e:
        print(f"❌ Error checking bot status: {e}")

async def main():
    print_command_guide()
    await monitor_bot_status()
    
    print("\n" + "="*80)
    print("🎯 NEXT STEPS:")
    print("="*80)
    print("1. Open Telegram and find @Krypkal_bot")
    print("2. Send /wallet to check your wallet")
    print("3. Send /autostart to begin automated trading")
    print("4. Monitor with /autostatus")
    print("5. Check performance with /my_stats")
    print("\n🚀 Your bot is ready to make money!")

if __name__ == "__main__":
    asyncio.run(main())
