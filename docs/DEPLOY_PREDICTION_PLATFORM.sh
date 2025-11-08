#!/bin/bash
# 🎯 DEPLOY PREDICTION PLATFORM - Complete Integration
# Run on Ubuntu: bash DEPLOY_PREDICTION_PLATFORM.sh

set -e

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎯 PREDICTION PLATFORM DEPLOYMENT"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

cd ~/code/TGbot

echo "Step 1: Stopping bot..."
pkill -f run_bot || true
sleep 3

echo "Step 2: Pulling latest from GitHub..."
git pull origin main || echo "⚠️ Git pull failed - will use existing files"

echo "Step 3: Verifying prediction platform files..."

# Check enhanced neural engine
if [ -f "src/modules/enhanced_neural_engine.py" ]; then
    echo "   ✅ enhanced_neural_engine.py present"
else
    echo "   ❌ enhanced_neural_engine.py MISSING!"
    echo "   Need to transfer from Windows"
    exit 1
fi

# Check unified neural engine
if [ -f "src/modules/unified_neural_engine.py" ]; then
    echo "   ✅ unified_neural_engine.py present"
else
    echo "   ❌ unified_neural_engine.py MISSING!"
    exit 1
fi

# Check active scanner
if [ -f "src/modules/active_sentiment_scanner.py" ]; then
    echo "   ✅ active_sentiment_scanner.py present"
else
    echo "   ❌ active_sentiment_scanner.py MISSING!"
    exit 1
fi

# Check UI formatter
if [ -f "src/modules/ui_formatter.py" ]; then
    echo "   ✅ ui_formatter.py present"
else
    echo "   ⚠️ ui_formatter.py missing (optional)"
fi

echo ""
echo "Step 4: Checking main.py integration..."
if grep -q "PredictionLayer" src/bot/main.py; then
    echo "   ✅ PredictionLayer integrated"
else
    echo "   ❌ main.py not updated!"
    echo "   Need to transfer updated main.py from Windows"
    exit 1
fi

if grep -q "predict_command" src/bot/main.py; then
    echo "   ✅ Prediction commands present"
else
    echo "   ❌ Prediction commands missing!"
    exit 1
fi

echo ""
echo "Step 5: Updating environment config..."
if [ -f "ENV_ULTIMATE_ENHANCED.txt" ]; then
    cp ENV_ULTIMATE_ENHANCED.txt .env.enhanced
    echo "   ✅ Enhanced config ready (.env.enhanced)"
    echo "   Run: cp .env.enhanced .env (to activate)"
else
    echo "   ⚠️ ENV_ULTIMATE_ENHANCED.txt not found (optional)"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ PREDICTION PLATFORM VERIFIED!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🎯 NEW FEATURES AVAILABLE:"
echo "   ✅ /predict - Probability predictions"
echo "   ✅ /autopredictions - Auto-trade on predictions"
echo "   ✅ /prediction_stats - Track accuracy"
echo "   ✅ Enhanced neural intelligence"
echo "   ✅ Kelly Criterion position sizing"
echo "   ✅ Dynamic TP/SL targets"
echo "   ✅ Tier-based recommendations"
echo ""
echo "🧠 INTELLIGENCE STACK:"
echo "   ✅ UnifiedNeuralEngine (learns weights)"
echo "   ✅ PredictionLayer (probabilities)"
echo "   ✅ ActiveSentimentScanner (Twitter/Reddit)"
echo "   ✅ 441 Elite Wallets (smart money)"
echo "   ✅ Community Intelligence"
echo "   ✅ 6-Layer Protection"
echo ""
echo "🚀 STARTING PREDICTION PLATFORM..."
sleep 2

source .venv/bin/activate
set -a
source .env
set +a

python scripts/run_bot.py --network mainnet

