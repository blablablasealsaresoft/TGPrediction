# Production Deployment Checklist

## Pre-Deployment

### Environment Configuration

- [ ] Generate wallet encryption key
  ```bash
  python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
  ```
- [ ] Set `WALLET_ENCRYPTION_KEY` in secure storage (KMS, Vault, or encrypted .env)
- [ ] Configure `TELEGRAM_BOT_TOKEN` (obtain from @BotFather)
- [ ] Set `ADMIN_CHAT_ID` (your Telegram user ID)
- [ ] Configure `SOLANA_RPC_URL` (recommended: Helius, Triton, or QuickNode)
- [ ] Optional: Set `HELIUS_API_KEY` for faster transaction parsing
- [ ] Optional: Configure sentiment APIs (Twitter, Reddit, Discord)

### Infrastructure

- [ ] Provision server (min: 2 CPU, 4GB RAM, 20GB storage)
- [ ] Install Python 3.9+ and pip
- [ ] Install SQLite (or provision PostgreSQL for production)
- [ ] Set up log rotation (`logrotate`)
- [ ] Configure firewall (allow outbound HTTPS, block inbound except SSH)
- [ ] Set up monitoring (Grafana, Datadog, or CloudWatch)

### Security

- [ ] Secure wallet encryption key (never commit to git)
- [ ] Set up SSH key authentication (disable password auth)
- [ ] Configure fail2ban for SSH protection
- [ ] Enable automatic security updates
- [ ] Set up database encryption at rest
- [ ] Review and minimize server permissions

---

## Installation

### 1. Clone Repository

```bash
git clone <repository-url> /opt/trading-bot
cd /opt/trading-bot
```

### 2. Install Dependencies

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
cp .env.example .env
nano .env
# Fill in all required variables
```

### 4. Run Health Check

```bash
python scripts/health_check.py
```

Expected output:
```
✅ WALLET_ENCRYPTION_KEY
✅ TELEGRAM_BOT_TOKEN
✅ SOLANA_RPC_URL
✅ Database initialization
✅ Solana RPC connection
✅ All modules
```

### 5. Initialize Database

```bash
# Database is automatically created on first run
# But you can verify:
python -c "
import asyncio
from src.modules.database import DatabaseManager
async def init():
    db = DatabaseManager()
    await db.init_db()
    print('✅ Database initialized')
asyncio.run(init())
"
```

---

## Deployment Options

### Option A: Systemd Service (Recommended)

1. Create service file:

```bash
sudo nano /etc/systemd/system/trading-bot.service
```

2. Add configuration:

```ini
[Unit]
Description=Solana Revolutionary Trading Bot
After=network.target

[Service]
Type=simple
User=trading-bot
Group=trading-bot
WorkingDirectory=/opt/trading-bot
Environment="PATH=/opt/trading-bot/venv/bin"
EnvironmentFile=/opt/trading-bot/.env
ExecStart=/opt/trading-bot/venv/bin/python scripts/run_bot.py
Restart=on-failure
RestartSec=10s
StandardOutput=append:/opt/trading-bot/logs/bot.log
StandardError=append:/opt/trading-bot/logs/bot-error.log

[Install]
WantedBy=multi-user.target
```

3. Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable trading-bot
sudo systemctl start trading-bot
```

4. Check status:

```bash
sudo systemctl status trading-bot
sudo journalctl -u trading-bot -f
```

### Option B: Docker

1. Build image:

```bash
docker build -t trading-bot:latest .
```

2. Run container:

```bash
docker run -d \
  --name trading-bot \
  --restart unless-stopped \
  -v /opt/trading-bot/data:/app/data \
  -v /opt/trading-bot/logs:/app/logs \
  --env-file .env \
  trading-bot:latest
```

3. Check logs:

```bash
docker logs -f trading-bot
```

### Option C: Kubernetes

1. Create namespace:

```bash
kubectl create namespace trading-bot
```

2. Create secrets:

```bash
kubectl create secret generic trading-bot-secrets \
  --from-env-file=.env \
  -n trading-bot
```

3. Deploy:

```bash
kubectl apply -f k8s/deployment.yaml -n trading-bot
```

---

## Post-Deployment

### Verification

- [ ] Bot starts without errors
- [ ] Telegram bot responds to `/start`
- [ ] Database tables created
- [ ] User can create wallet with `/start`
- [ ] `/balance` command works
- [ ] AI analysis works (`/ai <token>`)
- [ ] Sniper system operational (check logs for token detection)

### Initial Configuration

- [ ] Create admin user wallet (`/start` from admin account)
- [ ] Fund admin wallet for testing
- [ ] Test manual buy/sell commands
- [ ] Configure default user settings in database
- [ ] Set up tracked wallets for automated trading
- [ ] Register initial traders for copy trading

### Monitoring Setup

- [ ] Configure alerting thresholds
  - Trade failure rate > 10%
  - Daily loss > 2x limit
  - RPC errors > 50/minute
  - Database errors
  - Bot downtime > 5 minutes

- [ ] Set up dashboards
  - Active users
  - Daily trade volume (SOL)
  - PnL distribution
  - Sniper hit rate
  - Copy trading followers
  - RPC request rate

- [ ] Test alert delivery
  - Telegram admin notifications
  - Email alerts (if configured)
  - PagerDuty integration (if configured)

### Backup Configuration

- [ ] Database backup schedule (daily at minimum)
  ```bash
  # Cron job
  0 2 * * * /opt/trading-bot/scripts/backup_database.sh
  ```

- [ ] Backup retention policy (7 days daily, 4 weeks weekly, 12 months monthly)

- [ ] Test backup restoration
  ```bash
  # Stop bot
  systemctl stop trading-bot
  
  # Restore backup
  cp trading_bot.db.backup_20250124 trading_bot.db
  
  # Start bot
  systemctl start trading-bot
  ```

- [ ] Off-site backup storage (S3, Google Cloud Storage, etc.)

---

## Operations

### Daily Checks

- [ ] Review logs for errors
  ```bash
  grep "ERROR" logs/trading_bot.log | tail -20
  ```

- [ ] Check database size
  ```bash
  ls -lh trading_bot.db
  ```

- [ ] Verify bot is running
  ```bash
  systemctl status trading-bot
  ```

- [ ] Monitor active users and trade volume

### Weekly Checks

- [ ] Review trade performance (win rate, PnL)
- [ ] Check sniper effectiveness
- [ ] Review RPC usage and costs
- [ ] Update tracked wallets based on performance
- [ ] Prune old data (optional)
  ```bash
  sqlite3 trading_bot.db "DELETE FROM trades WHERE timestamp < datetime('now', '-90 days');"
  ```

### Monthly Checks

- [ ] Review and update risk parameters
- [ ] Analyze copy trading effectiveness
- [ ] Update AI model with new data (if applicable)
- [ ] Review and update trader tiers
- [ ] Security audit (check logs for suspicious activity)
- [ ] Backup verification (test restore)

### Quarterly Checks

- [ ] Rotate wallet encryption key
  ```bash
  python scripts/rotate_wallet_key.py
  ```

- [ ] Update dependencies
  ```bash
  pip list --outdated
  pip install --upgrade <package>
  ```

- [ ] Performance optimization review
- [ ] Infrastructure cost analysis
- [ ] Disaster recovery test

---

## Troubleshooting

### Bot Won't Start

1. Check logs:
   ```bash
   tail -100 logs/trading_bot.log
   journalctl -u trading-bot -n 100
   ```

2. Verify environment:
   ```bash
   python scripts/health_check.py
   ```

3. Check configuration:
   ```bash
   source .env
   echo $WALLET_ENCRYPTION_KEY  # Should not be empty
   echo $TELEGRAM_BOT_TOKEN     # Should not be empty
   ```

### High RPC Costs

1. Check request volume:
   ```bash
   grep "RPC" logs/trading_bot.log | wc -l
   ```

2. Optimize:
   - Reduce tracked wallet count
   - Increase scan interval (automated_trading.py)
   - Enable transaction caching
   - Use Helius enhanced API

### Database Growing Too Large

1. Check size:
   ```bash
   sqlite3 trading_bot.db "SELECT COUNT(*) FROM trades;"
   sqlite3 trading_bot.db "SELECT COUNT(*) FROM snipe_runs;"
   ```

2. Archive old data:
   ```bash
   # Export to CSV
   sqlite3 trading_bot.db ".mode csv" ".output trades_archive.csv" "SELECT * FROM trades WHERE timestamp < datetime('now', '-90 days');"
   
   # Delete old records
   sqlite3 trading_bot.db "DELETE FROM trades WHERE timestamp < datetime('now', '-90 days');"
   
   # Vacuum to reclaim space
   sqlite3 trading_bot.db "VACUUM;"
   ```

### Memory Leaks

1. Monitor memory:
   ```bash
   ps aux | grep python
   ```

2. Restart service:
   ```bash
   systemctl restart trading-bot
   ```

3. If persistent, investigate:
   - Transaction cache size
   - Wallet cache size
   - Event loop tasks

---

## Rollback Plan

### If Deployment Fails

1. Stop new service:
   ```bash
   systemctl stop trading-bot
   ```

2. Restore previous version:
   ```bash
   cd /opt/trading-bot
   git checkout <previous-commit>
   ```

3. Restore database backup:
   ```bash
   cp trading_bot.db.backup_<timestamp> trading_bot.db
   ```

4. Restart service:
   ```bash
   systemctl start trading-bot
   ```

5. Verify:
   ```bash
   systemctl status trading-bot
   tail -f logs/trading_bot.log
   ```

### If Data Corruption

1. Stop bot immediately:
   ```bash
   systemctl stop trading-bot
   ```

2. Backup corrupted database:
   ```bash
   cp trading_bot.db trading_bot.db.corrupted_$(date +%Y%m%d_%H%M%S)
   ```

3. Restore from backup:
   ```bash
   cp trading_bot.db.backup_latest trading_bot.db
   ```

4. Verify integrity:
   ```bash
   sqlite3 trading_bot.db "PRAGMA integrity_check;"
   ```

5. Restart bot:
   ```bash
   systemctl start trading-bot
   ```

---

## Migration to PostgreSQL (Optional, for High-Volume Production)

### Benefits

- Better concurrent access
- Advanced indexing
- Replication and high availability
- Better performance at scale

### Steps

1. Provision PostgreSQL:
   ```bash
   # Install PostgreSQL
   sudo apt install postgresql postgresql-contrib
   
   # Create database
   sudo -u postgres createdb trading_bot
   sudo -u postgres createuser trading_bot
   sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE trading_bot TO trading_bot;"
   ```

2. Update connection string:
   ```bash
   export DATABASE_URL="postgresql://trading_bot:password@localhost:5432/trading_bot"
   ```

3. Migrate data:
   ```bash
   # Export from SQLite
   sqlite3 trading_bot.db .dump > dump.sql
   
   # Import to PostgreSQL (after converting syntax)
   psql trading_bot < dump.sql
   ```

4. Test:
   ```bash
   python scripts/health_check.py
   ```

5. Deploy with new configuration

---

## Success Criteria

Deployment is successful when:

- ✅ Bot runs continuously without crashes for 24 hours
- ✅ Users can create wallets and execute trades
- ✅ Sniper detects and analyzes new tokens
- ✅ Copy trading propagates trades correctly
- ✅ Database grows at expected rate
- ✅ RPC costs within budget
- ✅ No critical errors in logs
- ✅ Monitoring alerts are working
- ✅ Backups are running successfully
- ✅ Admin can access and manage system

---

## Contact & Support

**Emergency Contacts:**
- Bot admin: [contact info]
- Infrastructure: [contact info]
- On-call: [PagerDuty/rotation]

**Documentation:**
- Full docs: See `IMPLEMENTATION_GUIDE.md`
- API reference: See `README.md`
- Health check: `python scripts/health_check.py`

**Monitoring:**
- Dashboard: [link]
- Logs: `logs/trading_bot.log`
- Metrics: [link]

---

**Last Updated:** 2025-10-24  
**Version:** 1.0.0

