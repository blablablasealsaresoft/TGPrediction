#!/usr/bin/env python3
"""
Fix Telegram bot conflict by ensuring webhooks are deleted and no other instances are polling
"""
import os
import sys
import time
import asyncio
import httpx
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.config import get_config


async def check_webhook_info(token: str):
    """Check current webhook configuration"""
    url = f"https://api.telegram.org/bot{token}/getWebhookInfo"
    async with httpx.AsyncClient() as client:
        response = await client.get(url, timeout=30.0)
        data = response.json()
        return data


async def delete_webhook(token: str, drop_pending: bool = True):
    """Delete webhook with option to drop pending updates"""
    url = f"https://api.telegram.org/bot{token}/deleteWebhook"
    params = {"drop_pending_updates": str(drop_pending).lower()}
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, params=params, timeout=30.0)
        data = response.json()
        return data


async def get_me(token: str):
    """Get bot information"""
    url = f"https://api.telegram.org/bot{token}/getMe"
    async with httpx.AsyncClient() as client:
        response = await client.get(url, timeout=30.0)
        data = response.json()
        return data


async def main():
    print("=" * 60)
    print("Telegram Bot Conflict Resolver")
    print("=" * 60)
    
    config = get_config()
    token = config.telegram_bot_token
    
    if not token:
        print("❌ ERROR: TELEGRAM_BOT_TOKEN not found in environment")
        return 1
    
    # Step 1: Verify bot token
    print("\n1. Verifying bot token...")
    try:
        bot_info = await get_me(token)
        if bot_info.get("ok"):
            bot_data = bot_info["result"]
            print(f"   ✅ Bot verified: @{bot_data['username']} (ID: {bot_data['id']})")
        else:
            print(f"   ❌ Invalid token: {bot_info.get('description')}")
            return 1
    except Exception as e:
        print(f"   ❌ Error verifying token: {e}")
        return 1
    
    # Step 2: Check current webhook status
    print("\n2. Checking webhook status...")
    try:
        webhook_info = await check_webhook_info(token)
        if webhook_info.get("ok"):
            result = webhook_info["result"]
            if result.get("url"):
                print(f"   ⚠️  WEBHOOK ACTIVE: {result['url']}")
                print(f"      Pending updates: {result.get('pending_update_count', 0)}")
                print(f"      Last error: {result.get('last_error_message', 'None')}")
            else:
                print("   ✅ No webhook configured")
                pending = result.get('pending_update_count', 0)
                if pending > 0:
                    print(f"      ⚠️  Pending updates: {pending}")
        else:
            print(f"   ❌ Error: {webhook_info.get('description')}")
    except Exception as e:
        print(f"   ❌ Error checking webhook: {e}")
    
    # Step 3: Delete webhook and drop pending updates
    print("\n3. Deleting webhook and clearing pending updates...")
    try:
        delete_result = await delete_webhook(token, drop_pending=True)
        if delete_result.get("ok"):
            print("   ✅ Webhook deleted and pending updates cleared")
        else:
            print(f"   ❌ Failed to delete webhook: {delete_result.get('description')}")
    except Exception as e:
        print(f"   ❌ Error deleting webhook: {e}")
    
    # Step 4: Wait and verify
    print("\n4. Waiting 3 seconds for Telegram to process...")
    await asyncio.sleep(3)
    
    print("\n5. Verifying webhook is gone...")
    try:
        webhook_info = await check_webhook_info(token)
        if webhook_info.get("ok"):
            result = webhook_info["result"]
            if result.get("url"):
                print(f"   ❌ WEBHOOK STILL ACTIVE: {result['url']}")
                print("      Manual intervention required!")
                return 1
            else:
                print("   ✅ Webhook successfully removed")
                pending = result.get('pending_update_count', 0)
                print(f"      Pending updates: {pending}")
        else:
            print(f"   ❌ Error: {webhook_info.get('description')}")
    except Exception as e:
        print(f"   ❌ Error checking webhook: {e}")
    
    print("\n" + "=" * 60)
    print("✅ RESOLUTION COMPLETE")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Make sure no other bot instances are running")
    print("2. Check if this bot is running on another server/location")
    print("3. Wait 5-10 seconds before starting your bot")
    print("4. Run: python scripts/run_bot.py --network mainnet")
    print("\nIf you still get conflicts:")
    print("- Check @BotFather for any webhook settings")
    print("- Verify no other scripts are using this bot token")
    print("- Consider regenerating your bot token via @BotFather")
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

