#!/bin/bash
# 🎨 COMPLETE ENTERPRISE UI + NEURAL AI DEPLOYMENT
# This deploys the FULL elite version with all enhancements

set -e

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎨 DEPLOYING COMPLETE ENTERPRISE UI"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

cd ~/code/TGbot

echo "Step 1: Stopping bot..."
pkill -f run_bot || true
sleep 3

echo "Step 2: Backing up current files..."
cp src/bot/main.py src/bot/main.py.backup.$(date +%Y%m%d_%H%M%S)
cp src/modules/ui_formatter.py src/modules/ui_formatter.py.backup.$(date +%Y%m%d_%H%M%S) 2>/dev/null || true

echo "Step 3: Checking deployment package..."
if [ ! -f "MANUAL_DEPLOY_PACKAGE/main.py" ]; then
    echo "❌ ERROR: MANUAL_DEPLOY_PACKAGE/main.py not found!"
    echo ""
    echo "You need to transfer these files from Windows to Ubuntu:"
    echo "  1. MANUAL_DEPLOY_PACKAGE/main.py"
    echo "  2. MANUAL_DEPLOY_PACKAGE/ui_formatter.py"
    echo "  3. MANUAL_DEPLOY_PACKAGE/unified_neural_engine.py"
    echo "  4. MANUAL_DEPLOY_PACKAGE/active_sentiment_scanner.py"
    echo ""
    echo "Use SCP, git, or manual copy-paste."
    echo ""
    exit 1
fi

echo "Step 4: Deploying files..."

# Deploy UI formatter (if exists in package)
if [ -f "MANUAL_DEPLOY_PACKAGE/ui_formatter.py" ]; then
    cp MANUAL_DEPLOY_PACKAGE/ui_formatter.py src/modules/
    echo "   ✅ Deployed ui_formatter.py"
else
    echo "   ℹ️ ui_formatter.py not in package (will use existing)"
fi

# Deploy complete main.py with all enhancements
cp MANUAL_DEPLOY_PACKAGE/main.py src/bot/
echo "   ✅ Deployed main.py (complete with neural AI + enterprise UI)"

# Verify neural modules exist
if [ -f "src/modules/unified_neural_engine.py" ]; then
    echo "   ✅ unified_neural_engine.py present"
else
    if [ -f "MANUAL_DEPLOY_PACKAGE/unified_neural_engine.py" ]; then
        cp MANUAL_DEPLOY_PACKAGE/unified_neural_engine.py src/modules/
        echo "   ✅ Deployed unified_neural_engine.py"
    fi
fi

if [ -f "src/modules/active_sentiment_scanner.py" ]; then
    echo "   ✅ active_sentiment_scanner.py present"
else
    if [ -f "MANUAL_DEPLOY_PACKAGE/active_sentiment_scanner.py" ]; then
        cp MANUAL_DEPLOY_PACKAGE/active_sentiment_scanner.py src/modules/
        echo "   ✅ Deployed active_sentiment_scanner.py"
    fi
fi

echo ""
echo "Step 5: Verifying installation..."
echo ""
echo "Files deployed:"
ls -lh src/bot/main.py
ls -lh src/modules/ui_formatter.py 2>/dev/null || echo "   ui_formatter.py: Will be created"
ls -lh src/modules/unified_neural_engine.py
ls -lh src/modules/active_sentiment_scanner.py

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ COMPLETE ELITE VERSION DEPLOYED!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🎨 NEW FEATURES:"
echo "   ✅ Enterprise UI (professional Telegram interface)"
echo "   ✅ Unified Neural Engine (learns from trades)"
echo "   ✅ Active Sentiment Scanner (scans Twitter/Reddit)"
echo "   ✅ Enhanced /start command"
echo "   ✅ Enhanced /wallet command"
echo "   ✅ Enhanced /leaderboard command"
echo "   ✅ Enhanced /help command"
echo "   ✅ Enhanced /stats command"
echo "   ✅ Enhanced /trending command"
echo "   ✅ Enhanced /ai command"
echo ""
echo "🚀 STARTING ELITE BOT..."
echo ""
sleep 2

source .venv/bin/activate
set -a
source .env
set +a

python scripts/run_bot.py --network mainnet

