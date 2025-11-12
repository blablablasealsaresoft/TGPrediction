@echo off
REM APOLLO CyberSentinel - Quick Start Script (Windows)
REM Starts the Telegram bot with web dashboard

echo.
echo 🚀 Starting APOLLO CyberSentinel with Web Dashboard...
echo.

REM Check if .env file exists
if not exist .env (
    echo ⚠️  .env file not found!
    echo Creating .env from .env.example...
    if exist .env.example (
        copy .env.example .env
        echo ✓ .env file created. Please edit it with your API keys.
        echo.
        echo Required variables:
        echo   - TELEGRAM_BOT_TOKEN
        echo   - SOLANA_PRIVATE_KEY
        echo   - DATABASE_URL
        echo.
        pause
        exit /b 1
    ) else (
        echo ⚠️  .env.example not found!
        pause
        exit /b 1
    )
)

echo 📋 Loading environment variables...

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Python not found! Please install Python 3.9 or higher.
    pause
    exit /b 1
)

echo 🐍 Using Python:
python --version
echo.

REM Create virtual environment if needed
if not exist venv (
    echo 📦 Creating virtual environment...
    python -m venv venv
    
    echo 📦 Installing dependencies...
    call venv\Scripts\activate.bat
    pip install -r requirements.txt
) else (
    call venv\Scripts\activate.bat
)

REM Check public directory
if not exist public (
    echo ⚠️  public directory not found!
    echo The web dashboard files may be missing.
    echo Please ensure you have:
    echo   - public\index.html
    echo   - public\dashboard.html
    echo   - public\prediction-market.html
    echo   - public\docs.html
    echo   - public\static\
    pause
    exit /b 1
)

echo ✓ All checks passed!
echo.
echo 🎯 Starting services...
echo.

REM Start the bot
echo ▶️  Launching APOLLO CyberSentinel...
echo.
echo 📡 Services will be available at:
echo    Landing Page:       http://localhost:8080/
echo    Trading Dashboard:  http://localhost:8080/dashboard
echo    Prediction Market:  http://localhost:8080/prediction-market
echo    Documentation:      http://localhost:8080/docs
echo    API Endpoint:       http://localhost:8080/api/v1/
echo    Health Check:       http://localhost:8080/health
echo.
echo 💬 Telegram bot will also be active!
echo.
echo Press CTRL+C to stop
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

REM Run the bot
python scripts\run_bot.py

pause

