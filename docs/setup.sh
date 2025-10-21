#!/bin/bash

# Solana Trading Bot Setup Script
# This script automates the installation process

set -e  # Exit on error

echo "🚀 Solana Trading Bot Setup"
echo "================================"
echo ""

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python version
echo "📋 Checking prerequisites..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is not installed${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 10 ]); then
    echo -e "${RED}❌ Python 3.10 or higher is required (found $PYTHON_VERSION)${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Python $PYTHON_VERSION${NC}"

# Create virtual environment
echo ""
echo "📦 Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}✅ Virtual environment created${NC}"
else
    echo -e "${YELLOW}⚠️  Virtual environment already exists${NC}"
fi

# Activate virtual environment
echo ""
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo ""
echo "📦 Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo ""
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo ""
    echo "⚙️  Creating .env configuration file..."
    cp .env.template .env
    echo -e "${GREEN}✅ .env file created${NC}"
    echo -e "${YELLOW}⚠️  IMPORTANT: Edit .env file with your configuration!${NC}"
else
    echo -e "${YELLOW}⚠️  .env file already exists, skipping${NC}"
fi

# Initialize database
echo ""
echo "🗄️  Initializing database..."
python3 -c "import asyncio; from database import DatabaseManager; asyncio.run(DatabaseManager().init_db())"
echo -e "${GREEN}✅ Database initialized${NC}"

# Create necessary directories
echo ""
echo "📁 Creating directories..."
mkdir -p logs
mkdir -p backups
echo -e "${GREEN}✅ Directories created${NC}"

# Print next steps
echo ""
echo "================================"
echo -e "${GREEN}✅ Setup complete!${NC}"
echo ""
echo "📝 Next steps:"
echo "1. Edit .env file with your configuration:"
echo "   - TELEGRAM_BOT_TOKEN (from @BotFather)"
echo "   - SOLANA_RPC_URL (get premium RPC)"
echo "   - WALLET_PRIVATE_KEY (create new wallet!)"
echo ""
echo "2. Test on devnet first:"
echo "   - Set USE_DEVNET=true in .env"
echo "   - Get devnet SOL: solana airdrop 1 YOUR_WALLET --url devnet"
echo ""
echo "3. Run the bot:"
echo "   source venv/bin/activate"
echo "   python3 solana_trading_bot.py"
echo ""
echo -e "${RED}⚠️  WARNINGS:${NC}"
echo "• Start with small amounts (0.1-0.5 SOL)"
echo "• Test thoroughly on devnet first"
echo "• Never share your private keys"
echo "• You can lose all your money - trade responsibly"
echo ""
echo -e "${YELLOW}📖 Read README.md for detailed instructions${NC}"
echo "================================"
