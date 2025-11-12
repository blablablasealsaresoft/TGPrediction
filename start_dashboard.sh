#!/bin/bash

# APOLLO CyberSentinel - Quick Start Script
# Starts the Telegram bot with web dashboard

set -e  # Exit on error

echo "🚀 Starting APOLLO CyberSentinel with Web Dashboard..."
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if .env file exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  .env file not found!${NC}"
    echo "Creating .env from .env.example..."
    if [ -f .env.example ]; then
        cp .env.example .env
        echo -e "${GREEN}✓${NC} .env file created. Please edit it with your API keys."
        echo ""
        echo "Required variables:"
        echo "  - TELEGRAM_BOT_TOKEN"
        echo "  - SOLANA_PRIVATE_KEY"
        echo "  - DATABASE_URL"
        echo ""
        exit 1
    else
        echo -e "${YELLOW}⚠️  .env.example not found!${NC}"
        exit 1
    fi
fi

# Load environment variables
echo "📋 Loading environment variables..."
export $(cat .env | grep -v '^#' | xargs)

# Check Python version
PYTHON_CMD="python3"
if ! command -v python3 &> /dev/null; then
    PYTHON_CMD="python"
fi

echo "🐍 Using Python: $($PYTHON_CMD --version)"
echo ""

# Install dependencies if needed
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    $PYTHON_CMD -m venv venv
    
    echo "📦 Installing dependencies..."
    source venv/bin/activate || . venv/Scripts/activate
    pip install -r requirements.txt
else
    source venv/bin/activate || . venv/Scripts/activate
fi

# Ensure public directory exists
if [ ! -d "public" ]; then
    echo -e "${YELLOW}⚠️  public directory not found!${NC}"
    echo "The web dashboard files may be missing."
    echo "Please ensure you have:"
    echo "  - public/index.html"
    echo "  - public/dashboard.html"
    echo "  - public/prediction-market.html"
    echo "  - public/docs.html"
    echo "  - public/static/"
    exit 1
fi

echo -e "${GREEN}✓${NC} All checks passed!"
echo ""
echo "🎯 Starting services..."
echo ""

# Start the bot
echo "▶️  Launching APOLLO CyberSentinel..."
echo ""
echo "📡 Services will be available at:"
echo -e "   ${BLUE}Landing Page:${NC}       http://localhost:8080/"
echo -e "   ${BLUE}Trading Dashboard:${NC}  http://localhost:8080/dashboard"
echo -e "   ${BLUE}Prediction Market:${NC}  http://localhost:8080/prediction-market"
echo -e "   ${BLUE}Documentation:${NC}      http://localhost:8080/docs"
echo -e "   ${BLUE}API Endpoint:${NC}       http://localhost:8080/api/v1/"
echo -e "   ${BLUE}Health Check:${NC}       http://localhost:8080/health"
echo ""
echo "💬 Telegram bot will also be active!"
echo ""
echo "Press CTRL+C to stop"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Run the bot
$PYTHON_CMD scripts/run_bot.py

# Cleanup on exit
trap "echo ''; echo '👋 Stopping APOLLO CyberSentinel...'; exit 0" INT TERM

