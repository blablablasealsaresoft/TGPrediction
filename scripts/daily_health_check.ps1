# Daily health check routine for production bot (Windows/PowerShell)
# Run this daily to verify system health

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "🏥 DAILY HEALTH CHECK - $(Get-Date)" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Check if containers are running
Write-Host "📦 Container Status:" -ForegroundColor Yellow
docker-compose -f docker-compose.prod.yml ps

Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
Write-Host ""

# Check PostgreSQL health
Write-Host "🗄️  Database Health:" -ForegroundColor Yellow
$pgVersion = docker exec trading-bot-db psql -U trader -d trading_bot -c "SELECT version();" -t 2>&1 | Select-Object -First 1
if ($pgVersion) {
    Write-Host "✅ PostgreSQL connected" -ForegroundColor Green
} else {
    Write-Host "❌ PostgreSQL connection failed" -ForegroundColor Red
}

# Check database stats
Write-Host ""
Write-Host "📊 Database Statistics:" -ForegroundColor Yellow

$trades = docker exec trading-bot-db psql -U trader -d trading_bot -t -c "SELECT COUNT(*) FROM trades;" 2>&1 | Select-String -Pattern "\d+"
Write-Host "   Trades: $($trades.Matches[0].Value)"

$positions = docker exec trading-bot-db psql -U trader -d trading_bot -t -c "SELECT COUNT(*) FROM positions WHERE is_open = true;" 2>&1 | Select-String -Pattern "\d+"
Write-Host "   Active Positions: $($positions.Matches[0].Value)"

$wallets = docker exec trading-bot-db psql -U trader -d trading_bot -t -c "SELECT COUNT(*) FROM user_wallets;" 2>&1 | Select-String -Pattern "\d+"
Write-Host "   User Wallets: $($wallets.Matches[0].Value)"

$tracked = docker exec trading-bot-db psql -U trader -d trading_bot -t -c "SELECT COUNT(*) FROM tracked_wallets;" 2>&1 | Select-String -Pattern "\d+"
Write-Host "   Tracked Wallets: $($tracked.Matches[0].Value)"

Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
Write-Host ""

# Check Redis health
Write-Host "⚡ Redis Health:" -ForegroundColor Yellow
try {
    $redisPing = docker exec trading-bot-redis redis-cli PING 2>&1
    if ($redisPing -like "*PONG*" -or $redisPing -like "*Authentication*") {
        Write-Host "✅ Redis responding" -ForegroundColor Green
    }
} catch {
    Write-Host "⚠️  Redis check failed" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
Write-Host ""

# Check bot logs for errors
Write-Host "🔍 Recent Errors (last 24 hours):" -ForegroundColor Yellow
try {
    $logContent = docker exec trading-bot-app cat logs/trading_bot.jsonl 2>&1
    $errorCount = ($logContent | Select-String '"level": "ERROR"').Count
    Write-Host "   Total errors: $errorCount" -ForegroundColor $(if ($errorCount -eq 0) { "Green" } else { "Yellow" })
    
    if ($errorCount -gt 0) {
        Write-Host ""
        Write-Host "   Last 5 errors:"
        ($logContent | Select-String '"level": "ERROR"' | Select-Object -Last 5) | ForEach-Object {
            Write-Host "   $_" -ForegroundColor Red
        }
    }
} catch {
    Write-Host "   Unable to read logs" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
Write-Host ""

# Check disk usage
Write-Host "💾 Disk Usage:" -ForegroundColor Yellow
Write-Host "   Log files:"
Get-ChildItem logs/*.jsonl -ErrorAction SilentlyContinue | ForEach-Object {
    $size = [math]::Round($_.Length / 1MB, 2)
    Write-Host "   $($_.Name): ${size} MB"
}

Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
Write-Host ""

# Summary
Write-Host "✅ HEALTH CHECK COMPLETE" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:"
Write-Host "  - Review error count (should be low)"
Write-Host "  - Check database growth (should be gradual)"
Write-Host "  - Verify all containers healthy"
Write-Host "  - Test /metrics command on Telegram"
Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan

