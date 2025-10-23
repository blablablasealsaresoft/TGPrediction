"""
Reset Telegram webhook to fix 409 Conflict error
"""

import asyncio
import os
from dotenv import load_dotenv
import aiohttp

load_dotenv()

async def reset_webhook():
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    
    print("\n🔄 Resetting Telegram Bot Webhook...")
    print("="*60)
    
    async with aiohttp.ClientSession() as session:
        # Delete webhook
        url = f"https://api.telegram.org/bot{token}/deleteWebhook?drop_pending_updates=true"
        
        async with session.post(url) as response:
            result = await response.json()
            
            if result.get('ok'):
                print("✅ Webhook deleted successfully")
                print(f"   Description: {result.get('description', 'N/A')}")
            else:
                print(f"⚠️ Response: {result}")
        
        # Get current webhook info
        url = f"https://api.telegram.org/bot{token}/getWebhookInfo"
        
        async with session.get(url) as response:
            result = await response.json()
            
            if result.get('ok'):
                info = result.get('result', {})
                print(f"\n✅ Current webhook status:")
                print(f"   URL: {info.get('url', 'None (polling mode)')}")
                print(f"   Pending updates: {info.get('pending_update_count', 0)}")
            
    print("\n✅ Telegram webhook reset complete!")
    print("="*60)
    print("\nNow you can start the bot without conflicts:")
    print("  python scripts/run_bot.py")

if __name__ == "__main__":
    asyncio.run(reset_webhook())

