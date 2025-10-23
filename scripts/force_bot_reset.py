"""
Force reset Telegram bot connection by dropping webhook and clearing updates
This will disconnect ALL bot instances and allow a fresh start
"""
import os
import sys
import requests
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

def force_reset_bot():
    """Force disconnect all bot instances"""
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    
    if not token:
        print("❌ No Telegram bot token found in .env")
        return
    
    base_url = f"https://api.telegram.org/bot{token}"
    
    print("🔧 Forcing bot reset...")
    print("=" * 60)
    
    # Step 1: Delete webhook (if any)
    print("\n1️⃣ Deleting webhook...")
    response = requests.post(f"{base_url}/deleteWebhook", json={"drop_pending_updates": True})
    if response.status_code == 200:
        print("   ✅ Webhook deleted")
    else:
        print(f"   ⚠️ Response: {response.status_code}")
    
    # Step 2: Get and clear pending updates (this forces disconnect)
    print("\n2️⃣ Clearing pending updates...")
    response = requests.post(f"{base_url}/getUpdates", json={"offset": -1, "timeout": 1})
    if response.status_code == 200:
        result = response.json()
        updates = result.get('result', [])
        
        if updates:
            # Get the highest update_id and offset past it
            highest_id = max(u['update_id'] for u in updates)
            
            print(f"   📊 Found {len(updates)} pending updates")
            print(f"   🔄 Clearing up to update ID {highest_id}...")
            
            # Offset past all pending updates
            response = requests.post(f"{base_url}/getUpdates", json={"offset": highest_id + 1, "timeout": 1})
            print("   ✅ Pending updates cleared")
        else:
            print("   ✅ No pending updates")
    else:
        print(f"   ⚠️ Response: {response.status_code}")
    
    # Step 3: Verify connection is clear
    print("\n3️⃣ Verifying reset...")
    response = requests.get(f"{base_url}/getMe")
    if response.status_code == 200:
        bot_info = response.json()['result']
        print(f"   ✅ Bot ready: @{bot_info['username']}")
        print(f"   🔓 Connection cleared - ready for new instance")
    else:
        print(f"   ❌ Failed to verify: {response.status_code}")
    
    print("\n" + "=" * 60)
    print("✅ RESET COMPLETE!")
    print("\nYou can now start the bot with:")
    print("   python scripts/run_bot.py")
    print("\nNote: Any other running instances will be disconnected!")

if __name__ == "__main__":
    force_reset_bot()

