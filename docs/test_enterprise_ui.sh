#!/bin/bash
# Quick test of enterprise UI updates
# Run on Ubuntu: bash test_enterprise_ui.sh

set -e

echo "🎨 ENTERPRISE UI UPDATE - DEPLOYMENT"
echo "=" * 60

# Check if on Ubuntu
if [[ "$OSTYPE" != "linux-gnu"* ]]; then
    echo "❌ Run this on Ubuntu server"
    exit 1
fi

cd ~/code/TGbot

echo "1. Killing existing bot..."
pkill -f run_bot || true
sleep 3

echo "2. Activating environment..."
source .venv/bin/activate

echo "3. Loading environment..."
set -a
source .env
set +a

echo "4. Starting bot with new enterprise UI..."
echo ""
echo "✅ NEW FEATURES:"
echo "   - Enterprise-grade UI formatting"
echo "   - Consistent HTML rendering"
echo "   - Professional visual hierarchy"
echo "   - Smart button layouts"
echo "   - Fixed datetime warning"
echo "   - Removed duplicate buttons"
echo ""
echo "🧪 TEST THESE COMMANDS:"
echo "   /start → New welcome screen"
echo "   /wallet → Enterprise wallet dashboard"
echo "   /help → Organized command reference"
echo "   /leaderboard → Beautiful rankings"
echo "   /stats → Performance dashboard"
echo ""
echo "Starting bot in 3 seconds..."
sleep 3

python scripts/run_bot.py --network mainnet

