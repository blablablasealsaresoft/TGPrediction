# 🧪 VERIFY BOT IS WORKING
# Run this to test if @gonehuntingbot is responding

Write-Host "`n🧪 TESTING @gonehuntingbot...`n" -ForegroundColor Cyan

$BOT_TOKEN = "8490397863:AAGg9W6CJTdvfLCSA8Cm7J4NCSzcey1FnRc"

Write-Host "1. Testing bot connection..." -ForegroundColor Yellow
$response = Invoke-RestMethod -Uri "https://api.telegram.org/bot$BOT_TOKEN/getMe"

if ($response.ok) {
    Write-Host "   ✅ Bot connected: @$($response.result.username)" -ForegroundColor Green
} else {
    Write-Host "   ❌ Bot not connected" -ForegroundColor Red
    exit 1
}

Write-Host "`n2. Testing webhook status..." -ForegroundColor Yellow
$webhook = Invoke-RestMethod -Uri "https://api.telegram.org/bot$BOT_TOKEN/getWebhookInfo"

if ($webhook.result.url) {
    Write-Host "   ⚠️  Webhook active: $($webhook.result.url)" -ForegroundColor Yellow
    Write-Host "   Deleting webhook..." -ForegroundColor Yellow
    Invoke-RestMethod -Uri "https://api.telegram.org/bot$BOT_TOKEN/deleteWebhook?drop_pending_updates=true" | Out-Null
    Write-Host "   ✅ Webhook deleted" -ForegroundColor Green
} else {
    Write-Host "   ✅ No webhook (polling mode)" -ForegroundColor Green
}

Write-Host "`n3. Checking recent updates..." -ForegroundColor Yellow
$updates = Invoke-RestMethod -Uri "https://api.telegram.org/bot$BOT_TOKEN/getUpdates"

if ($updates.ok) {
    Write-Host "   ✅ Can receive messages" -ForegroundColor Green
    if ($updates.result.Count -gt 0) {
        Write-Host "   📬 $($updates.result.Count) pending messages" -ForegroundColor Cyan
    }
} else {
    Write-Host "   ❌ Cannot receive messages" -ForegroundColor Red
}

Write-Host "`n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "✅ BOT VERIFICATION COMPLETE!" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan

Write-Host "`n📱 Test on Telegram:" -ForegroundColor Yellow
Write-Host "   1. Open Telegram" -ForegroundColor White
Write-Host "   2. Search: @gonehuntingbot" -ForegroundColor White
Write-Host "   3. Send: /start" -ForegroundColor White
Write-Host "   4. Should get instant response!`n" -ForegroundColor White

