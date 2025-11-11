# Daily Operations Guide

**For:** Production Bot Operator
**Platform:** Elite AI Trading Bot
**Version:** 1.0.0

---

## 📅 Daily Routine (5-10 minutes)

### Morning Check (5 minutes)

**1. Health Check**
```powershell
# Windows
.\scripts\daily_health_check.ps1

# Or Python version
python scripts/monitor_bot_health.py
```

**Expected Output:**
- ✅ All containers running
- ✅ Database connected
- ✅ 441 tracked wallets
- ✅ Error count low (<10)

**2. Telegram Bot Check**
Open Telegram and send:
```
/metrics
```

**Expected:**
- Uptime > 0 hours
- Success rate > 90% (or 0 if no trades yet)
- Health status: Healthy
- Recent errors: 0

**3. Container Status**
```powershell
docker-compose -f docker-compose.prod.yml ps
```

**Expected:** All containers "Up" and "healthy"

---

## 📊 Weekly Routine (30 minutes)

### Database Review (10 minutes)

**Check growth:**
```powershell
docker exec -it trading-bot-db psql -U trader -d trading_bot -c "
SELECT 
    'Total Trades: ' || COUNT(*) AS stat FROM trades
UNION ALL
SELECT 
    'Successful Trades: ' || COUNT(*) FROM trades WHERE success = true
UNION ALL  
SELECT
    'Open Positions: ' || COUNT(*) FROM positions WHERE is_open = true
UNION ALL
SELECT
    'Total Users: ' || COUNT(*) FROM user_wallets;
"
```

**Create backup:**
```powershell
.\scripts\create_db_backup.ps1
```

### Performance Review (10 minutes)

**Top performing wallets:**
```powershell
docker exec -it trading-bot-db psql -U trader -d trading_bot -c "
SELECT 
    wallet_address,
    score,
    win_rate,
    total_pnl
FROM tracked_wallets 
WHERE copy_enabled = true
ORDER BY score DESC
LIMIT 10;
"
```

**Recent trade performance:**
```powershell
docker exec -it trading-bot-db psql -U trader -d trading_bot -c "
SELECT 
    DATE(timestamp) as trade_date,
    COUNT(*) as trades,
    SUM(CASE WHEN success THEN 1 ELSE 0 END) as successful,
    ROUND(AVG(CASE WHEN success THEN 1.0 ELSE 0.0 END) * 100, 2) as success_rate
FROM trades
WHERE timestamp > NOW() - INTERVAL '7 days'
GROUP BY DATE(timestamp)
ORDER BY trade_date DESC;
"
```

### Log Review (10 minutes)

**Check for patterns:**
```powershell
# Count errors by component
docker exec trading-bot-app grep '"level": "ERROR"' logs/trading_bot.jsonl | 
    Select-String -Pattern '"component": "([^"]+)"' | 
    Group-Object | 
    Sort-Object Count -Descending
```

**Recent warnings:**
```powershell
docker exec trading-bot-app grep '"level": "WARNING"' logs/trading_bot.jsonl | tail -10
```

---

## 🔧 Monthly Routine (1-2 hours)

### Database Maintenance

**Vacuum and analyze:**
```powershell
docker exec -it trading-bot-db psql -U trader -d trading_bot -c "VACUUM ANALYZE;"
```

**Check database size:**
```powershell
docker exec -it trading-bot-db psql -U trader -d trading_bot -c "
SELECT 
    pg_size_pretty(pg_database_size('trading_bot')) as db_size;
"
```

**Archive old trades (optional - after 90 days):**
```powershell
docker exec -it trading-bot-db psql -U trader -d trading_bot -c "
DELETE FROM trades 
WHERE timestamp < NOW() - INTERVAL '90 days' 
  AND success = true;
"
```

### Performance Optimization

**Update wallet scores:**
```powershell
# Wallets are scored automatically, but you can verify:
docker exec -it trading-bot-db psql -U trader -d trading_bot -c "
SELECT 
    COUNT(*) FILTER (WHERE score >= 80) as excellent,
    COUNT(*) FILTER (WHERE score >= 70) as good,
    COUNT(*) FILTER (WHERE score >= 60) as average,
    COUNT(*) FILTER (WHERE score < 60) as poor
FROM tracked_wallets;
"
```

**Review RPC usage:**
Check Helius dashboard for API usage. If approaching limits:
- Reduce tracked wallet count
- Increase scan intervals
- Optimize query patterns

### Security Review

**Check for suspicious activity:**
```powershell
docker exec -it trading-bot-db psql -U trader -d trading_bot -c "
SELECT 
    user_id,
    COUNT(*) as trade_count,
    SUM(amount_sol) as total_volume
FROM trades
WHERE timestamp > NOW() - INTERVAL '24 hours'
GROUP BY user_id
HAVING COUNT(*) > 50 OR SUM(amount_sol) > 100
ORDER BY trade_count DESC;
"
```

---

## 🚨 Alert Thresholds

### Critical (Immediate Action)

| Metric | Threshold | Action |
|--------|-----------|--------|
| **Bot Down** | Container stopped | Restart immediately |
| **Database Down** | Connection failed | Check PostgreSQL logs |
| **Error Rate** | >20 errors/hour | Review logs, pause trading |
| **Failed Trades** | >50% failure rate | Pause trading, investigate |
| **Memory Usage** | >90% | Restart bot, check for leaks |

### Warning (Review Soon)

| Metric | Threshold | Action |
|--------|-----------|--------|
| **High Errors** | >10 errors/hour | Review error patterns |
| **Database Size** | >1 GB | Consider archiving old data |
| **Low Success Rate** | <70% | Review trade logic |
| **High RPC Usage** | >80% of quota | Optimize or upgrade plan |

---

## 📱 Telegram Monitoring

### Commands to Run Daily

```
/metrics          ← Bot health
/stats            ← Your performance
/autostatus       ← Automation status
/sniper_status    ← Sniper status (when enabled)
```

### What to Look For

**Good Signs:**
- ✅ Uptime increasing daily
- ✅ Success rate >70%
- ✅ Error count staying low
- ✅ Trades executing (when broadcast enabled)

**Warning Signs:**
- ⚠️ Success rate dropping
- ⚠️ Error count increasing
- ⚠️ No trades when automation enabled
- ⚠️ High failure rate

---

## 🔄 Restart Procedures

### Graceful Restart

```powershell
# Restart just the bot (preserves database)
docker-compose -f docker-compose.prod.yml restart trading-bot

# Monitor startup
docker-compose -f docker-compose.prod.yml logs -f trading-bot
```

**Wait for:** "Bot is now listening for commands..."

### Full Restart

```powershell
# Stop all
docker-compose -f docker-compose.prod.yml down

# Start all
docker-compose -f docker-compose.prod.yml up -d

# Monitor
docker-compose -f docker-compose.prod.yml logs -f trading-bot
```

### Emergency Stop

```powershell
# Stop trading immediately
docker-compose -f docker-compose.prod.yml stop trading-bot

# Check what caused issue
docker-compose -f docker-compose.prod.yml logs --tail=100 trading-bot
```

---

## 💾 Backup Procedures

### Daily Automated Backup

The docker-compose configuration includes a backup service (optional).

**To enable:**
```powershell
docker-compose -f docker-compose.prod.yml --profile backup up -d db-backup
```

**Manual backup:**
```powershell
.\scripts\create_db_backup.ps1
```

**Backups stored in:** `backups/trading_bot_backup_YYYYMMDD_HHMMSS.sql`

**Retention:** Last 7 days (automatic cleanup)

### Restore from Backup

```powershell
# Stop bot
docker-compose -f docker-compose.prod.yml stop trading-bot

# Restore
docker exec -i trading-bot-db psql -U trader trading_bot < backups/trading_bot_backup_20250111_120000.sql

# Restart
docker-compose -f docker-compose.prod.yml start trading-bot
```

---

## 📈 Performance Monitoring

### Key Metrics to Track

**Daily:**
- Bot uptime
- Total trades
- Success rate
- Error count
- Active users

**Weekly:**
- Trade volume (SOL)
- Win rate
- Average profit per trade
- Top performing wallets
- RPC request volume

**Monthly:**
- Monthly Recurring Revenue (MRR)
- User growth rate
- Database size
- API costs
- Infrastructure costs

### Dashboard Commands

```sql
-- Trading summary (last 30 days)
SELECT 
    COUNT(*) as total_trades,
    SUM(CASE WHEN success THEN 1 ELSE 0 END) as successful,
    ROUND(AVG(CASE WHEN success THEN 1.0 ELSE 0.0 END) * 100, 2) as success_rate,
    SUM(amount_sol) as total_volume_sol,
    COUNT(DISTINCT user_id) as unique_users
FROM trades
WHERE timestamp > NOW() - INTERVAL '30 days';

-- Top traders (by PnL)
SELECT 
    wallet_address,
    score,
    total_pnl,
    win_rate,
    followers
FROM tracked_wallets
WHERE is_trader = true
ORDER BY total_pnl DESC
LIMIT 20;

-- User growth
SELECT 
    DATE(created_at) as signup_date,
    COUNT(*) as new_users
FROM user_wallets
WHERE created_at > NOW() - INTERVAL '30 days'
GROUP BY DATE(created_at)
ORDER BY signup_date DESC;
```

---

## 🛠️ Troubleshooting Guide

### Issue: Bot Not Responding

**Symptoms:**
- Telegram commands timeout
- No response from bot

**Check:**
```powershell
# Container running?
docker ps | findstr trading-bot-app

# Telegram connection?
docker logs trading-bot-app | findstr "Application started"

# Errors in logs?
docker logs trading-bot-app | findstr ERROR
```

**Fix:**
```powershell
docker-compose -f docker-compose.prod.yml restart trading-bot
```

### Issue: High Error Rate

**Symptoms:**
- Many ERROR logs
- Failed trades increasing

**Check:**
```powershell
# Recent errors
docker exec trading-bot-app grep '"level": "ERROR"' logs/trading_bot.jsonl | tail -20
```

**Common Causes:**
- RPC rate limiting (upgrade plan)
- Invalid token addresses (user error)
- Network issues (check RPC endpoints)
- Database connection issues (check PostgreSQL)

**Fix:** Review specific errors and address root cause

### Issue: Database Growing Too Large

**Symptoms:**
- Database >1 GB
- Slow queries

**Check:**
```powershell
docker exec -it trading-bot-db psql -U trader -d trading_bot -c "
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
"
```

**Fix:** Archive old trades (see Monthly Routine above)

---

## 🔐 Security Checklist

### Daily
- [ ] Review failed login attempts (if any)
- [ ] Check for unusual trade patterns
- [ ] Verify API key usage (Helius dashboard)

### Weekly
- [ ] Review user activity for suspicious behavior
- [ ] Check for database injection attempts
- [ ] Verify wallet encryption keys secure

### Monthly
- [ ] Rotate API keys (optional but recommended)
- [ ] Update dependencies if security patches available
- [ ] Review access logs
- [ ] Test backup restoration

---

## 📞 Support Contacts

### Health Check Issues
- **Script:** `scripts/monitor_bot_health.py`
- **Manual:** Check container logs

### Database Issues
- **Check:** `docker logs trading-bot-db`
- **Access:** `docker exec -it trading-bot-db psql -U trader -d trading_bot`

### Bot Issues
- **Logs:** `docker logs trading-bot-app`
- **Restart:** `docker-compose restart trading-bot`

---

## ✅ Daily Checklist Template

```
[ ] Run health check script
[ ] Check /metrics on Telegram
[ ] Review error count (<10)
[ ] Verify containers healthy
[ ] Check disk usage (<80%)
[ ] Review any alerts
[ ] Test one command on Telegram
[ ] Check database backup exists (if enabled)
```

---

## 📊 Weekly Report Template

```
Week of: [DATE]

**Uptime:** [X]% 
**Total Trades:** [X]
**Success Rate:** [X]%
**Active Users:** [X]
**Top Wallet Score:** [X]/100
**Errors:** [X]
**Revenue:** $[X] (if tracking)

**Issues:** [List any issues]
**Actions Taken:** [List fixes]
**Next Week:** [Plans]
```

---

## 🚀 Optimization Tips

### If Bot is Slow
- Check RPC response times
- Consider upgrading Helius plan
- Reduce tracked wallet count
- Increase scan intervals

### If Database is Growing Fast
- Archive old successful trades
- Consider PostgreSQL partitioning
- Enable automatic cleanup scripts

### If Errors are High
- Review error patterns in logs
- Check API rate limits
- Verify network connectivity
- Update RPC endpoints

---

**Keep this guide handy for daily operations!** 📚

**Questions?** Check logs or run health check script.

---

**Last Updated:** 2025-01-11
**Version:** 1.0.0

