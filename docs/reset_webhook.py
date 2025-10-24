#!/usr/bin/env python3
"""
Reset Telegram webhook to fix API conflicts
"""

import asyncio
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.config import get_config
from telegram import Bot

async def reset_webhook():
    """Reset Telegram webhook"""
    
    print("\nResetting Telegram Bot Webhook...")
    
    config = get_config()
    bot_token = config.telegram_bot_token
    
    try:
        bot = Bot(token=bot_token)
        
        # Delete webhook
        result = await bot.delete_webhook()
        print(f"+ Webhook deleted: {result}")
        
        # Get bot info
        bot_info = await bot.get_me()
        print(f"+ Bot info: @{bot_info.username}")
        
        print("+ Webhook reset successful!")
        print("+ Bot is ready for polling mode")
        
    except Exception as e:
        print(f"- Error resetting webhook: {e}")

if __name__ == "__main__":
    asyncio.run(reset_webhook())
