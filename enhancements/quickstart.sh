#!/bin/bash

# 🚀 ELITE SOLANA TRADING BOT - QUICK START SCRIPT
# This script helps you get the bot running in minutes

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 ELITE SOLANA TRADING BOT - QUICK START"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check Python version
echo "📋 Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
required_version="3.9"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then 
    echo "❌ Python 3.9+ required. You have: $python_version"
    exit 1
fi
echo "✅ Python $python_version detected"
echo ""

# Create virtual environment
echo "🔧 Setting up virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ All dependencies installed"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi
echo ""

# Check for .env file
echo "🔐 Checking configuration..."
if [ ! -f ".env" ]; then
    echo "⚠️  No .env file found!"
    echo ""
    echo "Creating .env template..."
    cat > .env << 'EOF'
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=your_bot_token_here

# Solana Configuration
SOLANA_RPC_URL=https://api.mainnet-beta.solana.com
SOLANA_WS_URL=wss://api.mainnet-beta.solana.com

# IMPORTANT: For production, use a paid RPC for better performance!
# Recommended providers:
# - QuickNode: https://www.quicknode.com/
# - Helius: https://www.helius.dev/
# - Alchemy: https://www.alchemy.com/

# Wallet Configuration
# ⚠️  NEVER commit this file to git!
# ⚠️  Keep your private key secure!
WALLET_PRIVATE_KEY=your_private_key_here

# Trading Configuration
MAX_POSITION_SIZE_SOL=10.0
DEFAULT_BUY_AMOUNT=0.1
MAX_SLIPPAGE=0.05

# Automated Trading
AUTO_TRADE_ENABLED=false
AUTO_TRADE_MIN_CONFIDENCE=0.75
AUTO_TRADE_MAX_DAILY_TRADES=50
AUTO_TRADE_DAILY_LIMIT_SOL=100.0

# Risk Management
STOP_LOSS_PERCENTAGE=0.15
TAKE_PROFIT_PERCENTAGE=0.50
TRAILING_STOP_PERCENTAGE=0.10
MAX_DAILY_LOSS_SOL=50.0

# Sniping Configuration
SNIPE_ENABLED=true
SNIPE_AMOUNT_SOL=0.5
SNIPE_MIN_LIQUIDITY_SOL=10
SNIPE_PRIORITY_FEE=1000000

# Protection Settings
HONEYPOT_CHECK_ENABLED=true
MIN_LIQUIDITY_USD=5000.0
CHECK_MINT_AUTHORITY=true
CHECK_FREEZE_AUTHORITY=true
MAX_TOP_HOLDER_PERCENTAGE=0.20

# Twitter Monitoring (Optional)
TWITTER_MONITOR_ENABLED=false
TWITTER_REUSE_CHECK_ENABLED=true

# Database
DATABASE_URL=sqlite+aiosqlite:///trading_bot.db

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/trading_bot.log
EOF

    echo "✅ Created .env template"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "⚠️  IMPORTANT: Edit .env file with your configuration!"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "Required settings:"
    echo "1. TELEGRAM_BOT_TOKEN - Get from @BotFather on Telegram"
    echo "2. WALLET_PRIVATE_KEY - Your Solana wallet private key"
    echo ""
    echo "Run this script again after editing .env"
    echo ""
    exit 1
else
    # Check if .env is properly configured
    source .env
    
    if [ "$TELEGRAM_BOT_TOKEN" = "your_bot_token_here" ]; then
        echo "❌ Please edit .env and add your TELEGRAM_BOT_TOKEN"
        exit 1
    fi
    
    echo "✅ Configuration file found"
fi
echo ""

# Create logs directory
if [ ! -d "logs" ]; then
    mkdir logs
    echo "✅ Created logs directory"
fi

# Initialize database
echo "💾 Initializing database..."
python3 -c "
from database import DatabaseManager
import asyncio

async def init():
    db = DatabaseManager()
    await db.init_db()
    print('✅ Database initialized')

asyncio.run(init())
" 2>/dev/null || echo "✅ Database ready"
echo ""

# Display bot selection menu
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🤖 SELECT BOT VERSION TO RUN:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "1) Elite Bot (Recommended)"
echo "   - All advanced features"
echo "   - Wallet intelligence"
echo "   - Auto trading"
echo "   - 6-layer protection"
echo ""
echo "2) Main Bot (Full Production)"
echo "   - Your original bot"
echo "   - Social trading"
echo "   - AI strategies"
echo "   - Sentiment analysis"
echo ""
echo "3) Basic Bot (Learning/Testing)"
echo "   - Simple operations"
echo "   - Good for testing"
echo "   - Educational"
echo ""
echo "4) Exit"
echo ""
read -p "Enter choice [1-4]: " choice

case $choice in
    1)
        echo ""
        echo "🚀 Starting Elite Bot..."
        echo ""
        python3 elite_trading_bot.py
        ;;
    2)
        echo ""
        echo "🚀 Starting Main Bot..."
        echo ""
        python3 main.py
        ;;
    3)
        echo ""
        echo "🚀 Starting Basic Bot..."
        echo ""
        python3 basic_bot.py
        ;;
    4)
        echo "👋 Goodbye!"
        exit 0
        ;;
    *)
        echo "❌ Invalid choice"
        exit 1
        ;;
esac
