#!/bin/bash
# Quick deployment script for Ubuntu
# Run this on your Ubuntu server after uploading the code

set -e

echo "🚀 Solana Trading Bot - Ubuntu Deployment"
echo "=========================================="
echo ""

# Check if running on Linux
if [[ "$OSTYPE" != "linux-gnu"* ]]; then
    echo "❌ This script is for Ubuntu/Linux only"
    echo "   Run this on your Ubuntu server, not Windows"
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | grep -oP '\d+\.\d+' | head -1)
MAJOR_VERSION=$(echo $PYTHON_VERSION | cut -d. -f1)
MINOR_VERSION=$(echo $PYTHON_VERSION | cut -d. -f2)

if [ "$MAJOR_VERSION" -lt 3 ] || ([ "$MAJOR_VERSION" -eq 3 ] && [ "$MINOR_VERSION" -lt 10 ]); then
    echo "❌ Python 3.10+ required. Found: $PYTHON_VERSION"
    echo "   Install with: sudo apt install python3.12 python3.12-venv -y"
    exit 1
fi

echo "✅ Python version: $PYTHON_VERSION"

# Create virtual environment if needed
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate venv
echo "🔧 Activating virtual environment..."
source .venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip -q

# Install requirements
echo "📚 Installing dependencies..."
pip install -r requirements.txt -q

# Setup .env if not exists
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file from template..."
    cp ENV_PRODUCTION_READY.txt .env
    echo "⚠️  IMPORTANT: Edit .env and fill in:"
    echo "   - ADMIN_CHAT_ID"
    echo "   - WALLET_PRIVATE_KEY"
else
    echo "✅ .env file already exists"
fi

# Fix .env formatting
echo "🔧 Fixing .env formatting..."
perl -0pi -e 's/\r//g' .env 2>/dev/null || true
perl -0pi -e 's/^\h+//mg' .env 2>/dev/null || true

# Secure .env
chmod 600 .env

# Create logs directory
mkdir -p logs
chmod 755 logs

# Fix Telegram conflicts
echo "📡 Fixing Telegram conflicts..."
python scripts/fix_telegram_conflict.py

echo ""
echo "=========================================="
echo "✅ DEPLOYMENT COMPLETE!"
echo "=========================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Edit .env file:"
echo "   nano .env"
echo ""
echo "2. Fill in required values:"
echo "   - ADMIN_CHAT_ID (from @userinfobot)"
echo "   - WALLET_PRIVATE_KEY (your bot wallet)"
echo ""
echo "3. Test run (read-only mode):"
echo "   source .venv/bin/activate"
echo "   set -a; source .env; set +a"
echo "   python scripts/run_bot.py --network mainnet"
echo ""
echo "4. Setup as service (optional):"
echo "   See UBUNTU_DEPLOYMENT.md for systemd setup"
echo ""
echo "5. Go live:"
echo "   Edit .env: ALLOW_BROADCAST=true"
echo "   Use confirm token in commands"
echo ""
echo "Your tokens:"
echo "  CONFIRM_TOKEN=lYBjdXRJLcMFCLKCcOmTCCUniHOdi31A"
echo ""

