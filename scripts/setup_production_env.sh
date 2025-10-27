#!/bin/bash
# Production Environment Setup Script
# Run this to copy your production .env file

set -e

echo "================================"
echo "Production Environment Setup"
echo "================================"
echo ""

# Check if .env already exists
if [ -f ".env" ]; then
    echo "⚠️  WARNING: .env file already exists!"
    read -p "Do you want to backup and replace it? (y/N): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        BACKUP_FILE=".env.backup.$(date +%Y%m%d_%H%M%S)"
        echo "📦 Backing up existing .env to: $BACKUP_FILE"
        cp .env "$BACKUP_FILE"
    else
        echo "❌ Aborted. Your existing .env was not modified."
        exit 1
    fi
fi

# Copy the template
echo "📝 Copying production template to .env..."
cp ENV_PRODUCTION_READY.txt .env

echo ""
echo "✅ .env file created!"
echo ""
echo "================================"
echo "🚨 REQUIRED ACTIONS:"
echo "================================"
echo ""
echo "1. Edit .env and fill in:"
echo "   - ADMIN_CHAT_ID (your Telegram ID from @userinfobot)"
echo "   - WALLET_PRIVATE_KEY (your bot's wallet private key)"
echo ""
echo "2. Your tokens are already generated:"
echo "   ✅ CONFIRM_TOKEN: lYBjdXRJLcMFCLKCcOmTCCUniHOdi31A"
echo "   ✅ WALLET_ENCRYPTION_KEY: (generated securely)"
echo ""
echo "3. Fix Telegram conflicts:"
echo "   python scripts/fix_telegram_conflict.py"
echo ""
echo "4. Test the bot in read-only mode:"
echo "   python scripts/run_bot.py --network mainnet"
echo ""
echo "5. When ready for LIVE trading:"
echo "   - Edit .env: ALLOW_BROADCAST=true"
echo "   - Use confirm token in all commands:"
echo "     /buy TOKEN 1.0 confirm=lYBjdXRJLcMFCLKCcOmTCCUniHOdi31A"
echo ""
echo "================================"
echo "⚠️  SAFETY REMINDER"
echo "================================"
echo "- Test with SMALL amounts first"
echo "- ALLOW_BROADCAST=false means read-only (safe)"
echo "- ALLOW_BROADCAST=true requires confirm token"
echo "- Change the tokens after testing!"
echo ""

