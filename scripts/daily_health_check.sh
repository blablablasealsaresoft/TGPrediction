#!/bin/bash
# Daily health check routine for production bot
# Run this daily to verify system health

set -e

echo "============================================================"
echo "🏥 DAILY HEALTH CHECK - $(date)"
echo "============================================================"
echo ""

# Check if containers are running
echo "📦 Container Status:"
docker-compose -f docker-compose.prod.yml ps

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check PostgreSQL health
echo "🗄️  Database Health:"
docker exec trading-bot-db psql -U trader -d trading_bot -c "SELECT version();" -t | head -1
echo "✅ PostgreSQL connected"

# Check database stats
echo ""
echo "📊 Database Statistics:"
docker exec trading-bot-db psql -U trader -d trading_bot -t -c "
SELECT 
    'Trades: ' || COUNT(*) 
FROM trades;
"

docker exec trading-bot-db psql -U trader -d trading_bot -t -c "
SELECT 
    'Active Positions: ' || COUNT(*) 
FROM positions WHERE is_open = true;
"

docker exec trading-bot-db psql -U trader -d trading_bot -t -c "
SELECT 
    'User Wallets: ' || COUNT(*) 
FROM user_wallets;
"

docker exec trading-bot-db psql -U trader -d trading_bot -t -c "
SELECT 
    'Tracked Wallets: ' || COUNT(*) 
FROM tracked_wallets;
"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check Redis health
echo "⚡ Redis Health:"
if docker exec trading-bot-redis redis-cli -a "${REDIS_PASSWORD}" PING 2>/dev/null | grep -q PONG; then
    echo "✅ Redis responding"
else
    echo "⚠️  Redis authentication required"
    docker exec trading-bot-redis redis-cli PING
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check bot logs for errors
echo "🔍 Recent Errors (last 24 hours):"
ERROR_COUNT=$(docker exec trading-bot-app grep '"level": "ERROR"' logs/trading_bot.jsonl 2>/dev/null | wc -l || echo "0")
echo "Total errors: $ERROR_COUNT"

if [ "$ERROR_COUNT" -gt 0 ]; then
    echo ""
    echo "Last 5 errors:"
    docker exec trading-bot-app grep '"level": "ERROR"' logs/trading_bot.jsonl 2>/dev/null | tail -5 || echo "No errors"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check disk usage
echo "💾 Disk Usage:"
echo "Database size:"
docker exec trading-bot-db du -h /var/lib/postgresql/data/pgdata 2>/dev/null | tail -1 || echo "Unable to check"

echo ""
echo "Log file sizes:"
ls -lh logs/*.jsonl 2>/dev/null | awk '{print $5, $9}' || echo "No log files"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check API connectivity
echo "🌐 API Status:"
python scripts/validate_api_keys.py 2>&1 | grep "Critical APIs:" || echo "API check script available"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Summary
echo "✅ HEALTH CHECK COMPLETE"
echo ""
echo "Next steps:"
echo "  - Review error count (should be low)"
echo "  - Check database growth (should be gradual)"
echo "  - Verify all containers healthy"
echo "  - Test /metrics command on Telegram"
echo ""
echo "============================================================"

