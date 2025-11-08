# 🚀 START BOT - SIMPLE & CLEAN
# Run this to start your complete platform

Write-Host "`n🚀 STARTING ELITE TRADING BOT...`n" -ForegroundColor Cyan

cd C:\Users\ckthe\sol\TGbot

# Activate virtual environment
Write-Host "Activating environment..." -ForegroundColor Yellow
.\.venv\Scripts\Activate.ps1

# Show what will start
Write-Host "`n✅ Ready to start with:" -ForegroundColor Green
Write-Host "   • Bot: @gonehuntingbot" -ForegroundColor White
Write-Host "   • Network: mainnet" -ForegroundColor White
Write-Host "   • All 4 Phases: Active" -ForegroundColor White
Write-Host "   • 45 Commands: Ready`n" -ForegroundColor White

Write-Host "Starting in 3 seconds..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

# Start the bot
python scripts\run_bot.py --network mainnet

