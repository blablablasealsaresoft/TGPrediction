#!/bin/bash
# Emergency Telegram conflict fixer
# Run this on Ubuntu: bash FIX_TELEGRAM_NOW.sh

echo "🔧 Fixing Telegram conflicts..."

# Get bot token from environment
TOKEN="${TELEGRAM_BOT_TOKEN}"

if [ -z "$TOKEN" ]; then
    echo "❌ TELEGRAM_BOT_TOKEN not set"
    echo "Run: export TELEGRAM_BOT_TOKEN=8455438652:AAFvrxM6GFZ91BwoohvMCezhsj7N16YFju0"
    exit 1
fi

echo "1. Deleting webhook..."
curl -s -X POST "https://api.telegram.org/bot${TOKEN}/deleteWebhook?drop_pending_updates=true"
echo ""

echo "2. Waiting 10 seconds..."
sleep 10

echo "3. Checking webhook status..."
curl -s -X GET "https://api.telegram.org/bot${TOKEN}/getWebhookInfo"
echo ""

echo "✅ Done! Wait 20 more seconds before starting bot."
sleep 20
echo "✅ Ready to start bot now!"

