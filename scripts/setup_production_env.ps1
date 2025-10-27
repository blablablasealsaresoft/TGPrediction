# Production Environment Setup Script (PowerShell)
# Run this to copy your production .env file

Write-Host "================================" -ForegroundColor Cyan
Write-Host "Production Environment Setup" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Check if .env already exists
if (Test-Path ".env") {
    Write-Host "⚠️  WARNING: .env file already exists!" -ForegroundColor Yellow
    $response = Read-Host "Do you want to backup and replace it? (y/N)"
    if ($response -eq "y" -or $response -eq "Y") {
        $backupFile = ".env.backup.$(Get-Date -Format 'yyyyMMdd_HHmmss')"
        Write-Host "📦 Backing up existing .env to: $backupFile" -ForegroundColor Green
        Copy-Item .env $backupFile
    } else {
        Write-Host "❌ Aborted. Your existing .env was not modified." -ForegroundColor Red
        exit 1
    }
}

# Copy the template
Write-Host "📝 Copying production template to .env..." -ForegroundColor Green
Copy-Item ENV_PRODUCTION_READY.txt .env

Write-Host ""
Write-Host "✅ .env file created!" -ForegroundColor Green
Write-Host ""
Write-Host "================================" -ForegroundColor Yellow
Write-Host "🚨 REQUIRED ACTIONS:" -ForegroundColor Yellow
Write-Host "================================" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Edit .env and fill in:"
Write-Host "   - ADMIN_CHAT_ID (your Telegram ID from @userinfobot)"
Write-Host "   - WALLET_PRIVATE_KEY (your bot's wallet private key)"
Write-Host ""
Write-Host "2. Your tokens are already generated:" -ForegroundColor Green
Write-Host "   ✅ CONFIRM_TOKEN: lYBjdXRJLcMFCLKCcOmTCCUniHOdi31A" -ForegroundColor Green
Write-Host "   ✅ WALLET_ENCRYPTION_KEY: (generated securely)" -ForegroundColor Green
Write-Host ""
Write-Host "3. Fix Telegram conflicts:"
Write-Host "   python scripts/fix_telegram_conflict.py"
Write-Host ""
Write-Host "4. Test the bot in read-only mode:"
Write-Host "   python scripts/run_bot.py --network mainnet"
Write-Host ""
Write-Host "5. When ready for LIVE trading:"
Write-Host "   - Edit .env: ALLOW_BROADCAST=true"
Write-Host "   - Use confirm token in all commands:"
Write-Host "     /buy TOKEN 1.0 confirm=lYBjdXRJLcMFCLKCcOmTCCUniHOdi31A"
Write-Host ""
Write-Host "================================" -ForegroundColor Red
Write-Host "⚠️  SAFETY REMINDER" -ForegroundColor Red
Write-Host "================================" -ForegroundColor Red
Write-Host "- Test with SMALL amounts first" -ForegroundColor Yellow
Write-Host "- ALLOW_BROADCAST=false means read-only (safe)" -ForegroundColor Yellow
Write-Host "- ALLOW_BROADCAST=true requires confirm token" -ForegroundColor Yellow
Write-Host "- Change the tokens after testing!" -ForegroundColor Yellow
Write-Host ""

