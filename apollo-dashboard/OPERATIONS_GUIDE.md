# 🛠️ Operations & Maintenance Guide
## APOLLO CyberSentinel Enterprise Platform

**For**: System Administrators, DevOps Engineers, Site Reliability Engineers  
**Version**: 2.0 Enterprise  
**Last Updated**: November 11, 2025

---

## 📋 Table of Contents

1. [Daily Operations](#daily-operations)
2. [Monitoring & Alerts](#monitoring--alerts)
3. [Performance Tuning](#performance-tuning)
4. [Backup & Recovery](#backup--recovery)
5. [Security Operations](#security-operations)
6. [Incident Response](#incident-response)
7. [Scaling Procedures](#scaling-procedures)
8. [Maintenance Windows](#maintenance-windows)

---

## 📅 Daily Operations

### Morning Checklist (5 minutes)

```bash
#!/bin/bash
# Run every morning at 08:00

echo "=== APOLLO CyberSentinel Health Check ==="
echo "Time: $(date)"
echo ""

# 1. Check system health
echo "1. System Health:"
curl -s http://localhost:8080/ready | jq '.'

# 2. Check Docker containers
echo -e "\n2. Docker Containers:"
docker-compose ps | grep -E "trading-bot|redis|postgres"

# 3. Check logs for errors
echo -e "\n3. Recent Errors (last 100 lines):"
docker-compose logs --tail=100 trading-bot | grep -i error | wc -l

# 4. Check API connections
echo -e "\n4. API Status:"
docker-compose exec trading-bot npm run check-apis 2>/dev/null || echo "API check script not found"

# 5. Check resource usage
echo -e "\n5. Resource Usage:"
docker stats --no-stream trading-bot-app trading-bot-db trading-bot-redis

# 6. Check disk space
echo -e "\n6. Disk Space:"
df -h | grep -E "/$|/mnt"

# 7. Check active users
echo -e "\n7. Active Trading Sessions:"
docker-compose exec -T trading-bot-db psql -U trader -d trading_bot -t -c \
  "SELECT COUNT(DISTINCT user_id) FROM user_sessions WHERE last_active > NOW() - INTERVAL '24 hours';"

echo -e "\n=== Health Check Complete ==="
```

Save as: `/usr/local/bin/apollo-health-check.sh`  
Schedule: `crontab -e` → `0 8 * * * /usr/local/bin/apollo-health-check.sh | mail -s "APOLLO Health Report" admin@company.com`

### Evening Checklist (5 minutes)

```bash
#!/bin/bash
# Run every evening at 20:00

echo "=== APOLLO CyberSentinel Daily Summary ==="
echo "Date: $(date +%Y-%m-%d)"
echo ""

# 1. Trading statistics
echo "1. Trading Statistics:"
docker-compose exec -T trading-bot-db psql -U trader -d trading_bot -t << EOF
SELECT 
  COUNT(*) as total_trades,
  SUM(CASE WHEN success = true THEN 1 ELSE 0 END) as successful_trades,
  ROUND(AVG(CASE WHEN success = true THEN 100.0 ELSE 0 END), 2) as win_rate,
  SUM(pnl) as total_pnl
FROM trades
WHERE timestamp > CURRENT_DATE;
EOF

# 2. AI Predictions
echo -e "\n2. AI Predictions Today:"
docker-compose exec -T trading-bot-db psql -U trader -d trading_bot -t << EOF
SELECT 
  COUNT(*) as total_predictions,
  SUM(CASE WHEN confidence >= 90 THEN 1 ELSE 0 END) as ultra_confidence,
  ROUND(AVG(confidence), 2) as avg_confidence
FROM predictions
WHERE timestamp > CURRENT_DATE;
EOF

# 3. System errors
echo -e "\n3. System Errors Today:"
docker-compose logs --since=24h trading-bot | grep -c ERROR

# 4. Backup verification
echo -e "\n4. Last Backup:"
ls -lh backups/daily/ | tail -1

echo -e "\n=== Daily Summary Complete ==="
```

Save as: `/usr/local/bin/apollo-daily-summary.sh`  
Schedule: `0 20 * * * /usr/local/bin/apollo-daily-summary.sh > /var/log/apollo/daily-summary-$(date +\%Y\%m\%d).log`

---

## 📊 Monitoring & Alerts

### Key Metrics to Monitor

#### System Health Metrics

```yaml
Metrics:
  - CPU Usage: 
      Warning: > 70%
      Critical: > 90%
  - Memory Usage:
      Warning: > 75%
      Critical: > 90%
  - Disk Usage:
      Warning: > 80%
      Critical: > 95%
  - Network I/O:
      Warning: > 100 Mbps sustained
      Critical: > 500 Mbps sustained
```

#### Application Metrics

```yaml
Metrics:
  - Response Time:
      Target: < 100ms
      Warning: > 200ms
      Critical: > 500ms
  - Error Rate:
      Target: < 0.1%
      Warning: > 0.5%
      Critical: > 1.0%
  - Database Connections:
      Target: < 50% pool
      Warning: > 80% pool
      Critical: > 95% pool
  - API Rate Limits:
      Warning: > 80% of limit
      Critical: > 95% of limit
```

### Setting Up Prometheus + Grafana

```bash
# 1. Add monitoring stack to docker-compose
cat >> docker-compose.monitoring.yml << EOF
version: '3.8'

services:
  prometheus:
    image: prom/prometheus:latest
    container_name: apollo-prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus-data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
    restart: unless-stopped

  grafana:
    image: grafana/grafana:latest
    container_name: apollo-grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
      - GF_USERS_ALLOW_SIGN_UP=false
    volumes:
      - grafana-data:/var/lib/grafana
      - ./monitoring/grafana-dashboards:/etc/grafana/provisioning/dashboards
    restart: unless-stopped

  node-exporter:
    image: prom/node-exporter:latest
    container_name: apollo-node-exporter
    ports:
      - "9100:9100"
    restart: unless-stopped

volumes:
  prometheus-data:
  grafana-data:

networks:
  default:
    name: apollo-network
    external: true
EOF

# 2. Create Prometheus config
mkdir -p monitoring
cat > monitoring/prometheus.yml << EOF
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'apollo-bot'
    static_configs:
      - targets: ['trading-bot-app:8080']
  
  - job_name: 'node-exporter'
    static_configs:
      - targets: ['node-exporter:9100']
  
  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres-exporter:9187']
EOF

# 3. Start monitoring stack
docker-compose -f docker-compose.monitoring.yml up -d

# 4. Access Grafana
# URL: http://localhost:3000
# Username: admin
# Password: admin (change immediately!)
```

### Alert Configuration

```yaml
# monitoring/alert-rules.yml
groups:
  - name: apollo_alerts
    interval: 30s
    rules:
      # High error rate
      - alert: HighErrorRate
        expr: rate(http_requests_total{status="500"}[5m]) > 0.05
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value }} errors per second"
      
      # High response time
      - alert: HighResponseTime
        expr: http_request_duration_seconds > 0.5
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High response time detected"
          description: "Average response time is {{ $value }}s"
      
      # Database connection pool exhausted
      - alert: DatabasePoolExhausted
        expr: pg_pool_connections_in_use / pg_pool_connections_max > 0.9
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "Database connection pool nearly exhausted"
          description: "{{ $value | humanizePercentage }} of connections in use"
      
      # Redis memory high
      - alert: RedisMemoryHigh
        expr: redis_memory_used_bytes / redis_memory_max_bytes > 0.8
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Redis memory usage is high"
          description: "{{ $value | humanizePercentage }} of Redis memory in use"
```

### Notification Channels

**Slack Integration**:
```bash
# Add to Grafana notification channels
curl -X POST http://localhost:3000/api/alert-notifications \
  -H "Content-Type: application/json" \
  -u admin:admin \
  -d '{
    "name": "Slack Alerts",
    "type": "slack",
    "isDefault": true,
    "settings": {
      "url": "https://hooks.slack.com/services/YOUR/WEBHOOK/URL",
      "username": "APOLLO CyberSentinel",
      "icon_emoji": ":rocket:"
    }
  }'
```

**Email Alerts**:
```bash
# Configure in Grafana settings
GF_SMTP_ENABLED=true
GF_SMTP_HOST=smtp.gmail.com:587
GF_SMTP_USER=alerts@company.com
GF_SMTP_PASSWORD=your-password
GF_SMTP_FROM_ADDRESS=alerts@company.com
GF_SMTP_FROM_NAME="APOLLO Alerts"
```

---

## ⚡ Performance Tuning

### Database Optimization

```sql
-- 1. Analyze database performance
SELECT schemaname, tablename, 
       pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- 2. Identify slow queries
SELECT query, mean_exec_time, calls
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;

-- 3. Add indexes for frequently queried columns
CREATE INDEX CONCURRENTLY idx_trades_timestamp ON trades(timestamp DESC);
CREATE INDEX CONCURRENTLY idx_trades_user_id ON trades(user_id);
CREATE INDEX CONCURRENTLY idx_predictions_token ON predictions(token);
CREATE INDEX CONCURRENTLY idx_predictions_confidence ON predictions(confidence DESC);

-- 4. Vacuum and analyze
VACUUM ANALYZE trades;
VACUUM ANALYZE predictions;
VACUUM ANALYZE user_wallets;

-- 5. Update statistics
ANALYZE;
```

### PostgreSQL Configuration

```ini
# /etc/postgresql/postgresql.conf
# Optimized for 8GB RAM system

# Memory Settings
shared_buffers = 2GB
effective_cache_size = 6GB
maintenance_work_mem = 512MB
work_mem = 64MB

# Checkpoint Settings
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100

# Query Planner
random_page_cost = 1.1
effective_io_concurrency = 200

# Connection Settings
max_connections = 200
```

### Redis Optimization

```conf
# /etc/redis/redis.conf

# Memory Management
maxmemory 2gb
maxmemory-policy allkeys-lru

# Persistence (for production)
save 900 1
save 300 10
save 60 10000

# Performance
tcp-keepalive 60
timeout 300
```

### Application-Level Optimization

```javascript
// Connection pooling configuration
const pool = new Pool({
  host: 'trading-bot-db',
  database: 'trading_bot',
  max: 20,                    // Maximum connections
  idleTimeoutMillis: 30000,   // Close idle clients after 30s
  connectionTimeoutMillis: 2000,
});

// Redis connection pooling
const redisOptions = {
  maxRetriesPerRequest: 3,
  enableReadyCheck: true,
  lazyConnect: true,
  maxReconnectionTime: 10000,
};

// Query optimization
// Use prepared statements
const result = await pool.query(
  'SELECT * FROM trades WHERE user_id = $1 AND timestamp > $2',
  [userId, timestamp]
);

// Batch operations
await pool.query('BEGIN');
for (const trade of trades) {
  await pool.query('INSERT INTO trades VALUES ($1, $2, $3)', [trade.id, trade.amount, trade.price]);
}
await pool.query('COMMIT');
```

---

## 💾 Backup & Recovery

### Automated Backup Script

```bash
#!/bin/bash
# /usr/local/bin/apollo-backup.sh

BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=30

echo "Starting backup at $(date)"

# 1. Database backup
echo "Backing up PostgreSQL database..."
docker exec trading-bot-db pg_dump -U trader trading_bot | gzip > \
  "$BACKUP_DIR/daily/db_backup_$DATE.sql.gz"

# 2. Configuration backup
echo "Backing up configuration..."
tar -czf "$BACKUP_DIR/daily/config_backup_$DATE.tar.gz" \
  .env envconfig.txt docker-compose*.yml

# 3. Redis backup (if persistent)
echo "Backing up Redis data..."
docker exec trading-bot-redis redis-cli BGSAVE
sleep 5
docker cp trading-bot-redis:/data/dump.rdb \
  "$BACKUP_DIR/daily/redis_backup_$DATE.rdb"

# 4. Logs backup
echo "Backing up logs..."
tar -czf "$BACKUP_DIR/daily/logs_backup_$DATE.tar.gz" logs/

# 5. Weekly full backup (Sundays)
if [ $(date +%u) -eq 7 ]; then
  echo "Creating weekly backup..."
  tar -czf "$BACKUP_DIR/weekly/full_backup_$DATE.tar.gz" \
    "$BACKUP_DIR/daily/"
fi

# 6. Monthly backup (1st of month)
if [ $(date +%d) -eq 01 ]; then
  echo "Creating monthly backup..."
  tar -czf "$BACKUP_DIR/monthly/full_backup_$DATE.tar.gz" \
    "$BACKUP_DIR/daily/" "$BACKUP_DIR/weekly/"
fi

# 7. Cleanup old backups
echo "Cleaning up old backups..."
find "$BACKUP_DIR/daily" -type f -mtime +$RETENTION_DAYS -delete
find "$BACKUP_DIR/weekly" -type f -mtime +90 -delete
find "$BACKUP_DIR/monthly" -type f -mtime +365 -delete

# 8. Verify backup integrity
echo "Verifying database backup..."
gunzip -c "$BACKUP_DIR/daily/db_backup_$DATE.sql.gz" | head -1

echo "Backup completed at $(date)"
```

Schedule: `0 2 * * * /usr/local/bin/apollo-backup.sh >> /var/log/apollo/backup.log 2>&1`

### Recovery Procedures

**Complete System Recovery**:
```bash
#!/bin/bash
# /usr/local/bin/apollo-restore.sh

BACKUP_FILE=$1

if [ -z "$BACKUP_FILE" ]; then
  echo "Usage: $0 <backup_file.sql.gz>"
  exit 1
fi

echo "WARNING: This will overwrite all current data!"
read -p "Continue? (yes/NO): " confirm

if [ "$confirm" != "yes" ]; then
  echo "Aborted."
  exit 0
fi

# 1. Stop services
echo "Stopping services..."
docker-compose down

# 2. Start only database
echo "Starting database..."
docker-compose up -d trading-bot-db
sleep 10

# 3. Drop and recreate database
echo "Recreating database..."
docker exec trading-bot-db psql -U trader -c "DROP DATABASE IF EXISTS trading_bot;"
docker exec trading-bot-db psql -U trader -c "CREATE DATABASE trading_bot;"

# 4. Restore database
echo "Restoring database from $BACKUP_FILE..."
gunzip -c "$BACKUP_FILE" | docker exec -i trading-bot-db psql -U trader trading_bot

# 5. Verify restoration
echo "Verifying restoration..."
docker exec trading-bot-db psql -U trader trading_bot -c "\dt"

# 6. Restart all services
echo "Restarting all services..."
docker-compose up -d

echo "Recovery complete!"
```

**Point-in-Time Recovery**:
```bash
# Enable WAL archiving in PostgreSQL
# In postgresql.conf:
wal_level = replica
archive_mode = on
archive_command = 'test ! -f /backups/wal/%f && cp %p /backups/wal/%f'

# Restore to specific point in time
docker exec trading-bot-db pg_basebackup -U trader -D /var/lib/postgresql/data_new -Fp -Xs -P
# Then configure recovery.conf with target time
```

---

## 🔒 Security Operations

### Security Audit Checklist

**Weekly Security Checks**:
```bash
#!/bin/bash
# /usr/local/bin/apollo-security-audit.sh

echo "=== APOLLO CyberSentinel Security Audit ==="
echo "Date: $(date)"
echo ""

# 1. Check for exposed ports
echo "1. Exposed Ports:"
docker ps --format "table {{.Names}}\t{{.Ports}}"

# 2. Check for running containers as root
echo -e "\n2. Root Processes:"
docker top trading-bot-app | grep "root" | wc -l

# 3. Check SSL/TLS certificates
echo -e "\n3. SSL Certificate Status:"
if [ -f "/etc/letsencrypt/live/yourdomain.com/cert.pem" ]; then
  openssl x509 -in /etc/letsencrypt/live/yourdomain.com/cert.pem -noout -dates
else
  echo "No SSL certificate found"
fi

# 4. Check for failed login attempts
echo -e "\n4. Failed Login Attempts (last 24h):"
docker-compose logs --since=24h trading-bot | grep -i "failed login" | wc -l

# 5. Check API key rotation
echo -e "\n5. API Keys Older Than 90 Days:"
docker-compose exec -T trading-bot-db psql -U trader -d trading_bot -t << EOF
SELECT COUNT(*) 
FROM api_keys 
WHERE created_at < NOW() - INTERVAL '90 days' 
AND revoked_at IS NULL;
EOF

# 6. Check for outdated dependencies
echo -e "\n6. Outdated Dependencies:"
docker exec trading-bot-app npm outdated 2>/dev/null | grep -v "^Package" | wc -l

echo -e "\n=== Security Audit Complete ==="
```

### Hardening Checklist

- [ ] Change all default passwords
- [ ] Enable firewall (UFW or iptables)
- [ ] Configure fail2ban for SSH
- [ ] Enable HTTPS with Let's Encrypt
- [ ] Disable root SSH login
- [ ] Enable 2FA for admin accounts
- [ ] Regular security updates
- [ ] API rate limiting configured
- [ ] Database encrypted at rest
- [ ] Secrets not in plaintext
- [ ] Regular security audits
- [ ] Intrusion detection system

---

## 🚨 Incident Response

### Incident Response Plan

**Level 1 - Low Severity** (Response: 4 hours)
- Single API endpoint slow
- Minor UI glitch
- Non-critical log errors

**Level 2 - Medium Severity** (Response: 1 hour)
- Multiple API endpoints degraded
- Database connection issues
- Elevated error rates

**Level 3 - High Severity** (Response: 15 minutes)
- System unavailable
- Data corruption
- Security breach
- Complete service outage

### Emergency Procedures

**System Down**:
```bash
# 1. Quick diagnostic
docker-compose ps
docker-compose logs --tail=100

# 2. Immediate restart
docker-compose restart

# 3. If still down, rebuild
docker-compose down
docker-compose up -d

# 4. Check logs for root cause
docker-compose logs -f | grep ERROR
```

**Database Corruption**:
```bash
# 1. Stop application
docker-compose stop trading-bot-app

# 2. Run database recovery
docker exec trading-bot-db pg_resetwal /var/lib/postgresql/data

# 3. Restore from latest backup
gunzip -c /backups/daily/db_backup_latest.sql.gz | \
  docker exec -i trading-bot-db psql -U trader trading_bot

# 4. Restart services
docker-compose up -d
```

**Security Breach**:
```bash
# 1. Isolate system
docker-compose down
iptables -A INPUT -j DROP

# 2. Preserve evidence
tar -czf /tmp/evidence-$(date +%s).tar.gz logs/ .env

# 3. Rotate all credentials
# - Database passwords
# - API keys
# - SSH keys
# - Telegram bot token

# 4. Audit and patch
# - Review all logs
# - Identify vulnerability
# - Apply security patches

# 5. Resume operations
docker-compose up -d
iptables -D INPUT -j DROP
```

---

## 📈 Scaling Procedures

### Vertical Scaling (Single Server)

**Upgrade Resources**:
```bash
# 1. Current resource usage
docker stats --no-stream

# 2. Update docker-compose resource limits
# docker-compose.prod.yml
services:
  trading-bot-app:
    deploy:
      resources:
        limits:
          cpus: '4.0'      # Increase from 2.0
          memory: 8G       # Increase from 4G
        reservations:
          cpus: '2.0'
          memory: 4G

# 3. Apply changes
docker-compose up -d --force-recreate
```

### Horizontal Scaling (Multiple Servers)

**Load Balancer Configuration**:
```nginx
# nginx-lb.conf
upstream apollo_backend {
    least_conn;
    server apollo-node1:8080 max_fails=3 fail_timeout=30s;
    server apollo-node2:8080 max_fails=3 fail_timeout=30s;
    server apollo-node3:8080 max_fails=3 fail_timeout=30s;
}

server {
    listen 80;
    
    location / {
        proxy_pass http://apollo_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

**Database Replication**:
```sql
-- Primary server
ALTER SYSTEM SET wal_level = replica;
ALTER SYSTEM SET max_wal_senders = 3;
ALTER SYSTEM SET wal_keep_segments = 64;

-- Replica server
CREATE SUBSCRIPTION apollo_subscription
CONNECTION 'host=primary-db port=5432 dbname=trading_bot user=replicator'
PUBLICATION apollo_publication;
```

---

## 🔧 Maintenance Windows

### Planned Maintenance Schedule

**Monthly Maintenance** (First Sunday, 02:00-04:00 UTC):
1. System updates
2. Security patches
3. Database optimization
4. Full backup verification
5. Performance review

**Quarterly Maintenance** (First Sunday of quarter, 02:00-06:00 UTC):
1. Major version upgrades
2. Infrastructure changes
3. Capacity planning
4. Disaster recovery test
5. Security audit

### Maintenance Checklist

```bash
#!/bin/bash
# /usr/local/bin/apollo-maintenance.sh

echo "=== Starting Maintenance Window ==="

# 1. Notify users
curl -X POST https://api.telegram.org/bot$BOT_TOKEN/sendMessage \
  -d chat_id=@YourChannel \
  -d text="🔧 Maintenance starting in 15 minutes"

sleep 900  # 15 minutes

# 2. Enable maintenance mode
echo "maintenance_mode=true" >> .env
docker-compose restart

# 3. Perform updates
docker-compose pull
docker-compose down
docker-compose up -d

# 4. Run database maintenance
docker exec trading-bot-db vacuumdb -U trader -d trading_bot --analyze

# 5. Verify health
sleep 30
curl http://localhost:8080/ready

# 6. Disable maintenance mode
sed -i '/maintenance_mode/d' .env
docker-compose restart

# 7. Notify completion
curl -X POST https://api.telegram.org/bot$BOT_TOKEN/sendMessage \
  -d chat_id=@YourChannel \
  -d text="✅ Maintenance complete. All systems operational."

echo "=== Maintenance Complete ==="
```

---

## 📞 Support & Escalation

**Tier 1 Support**: Common issues, user questions  
**Tier 2 Support**: Technical issues, performance problems  
**Tier 3 Support**: Critical failures, security incidents

**Escalation Path**:
1. On-call engineer (immediate)
2. Lead DevOps (15 minutes)
3. CTO (30 minutes)
4. CEO (1 hour - only for critical incidents)

**Contact Information**:
- On-Call: +1-XXX-XXX-XXXX (24/7)
- DevOps Team: devops@apollo-sentinel.com
- Security Team: security@apollo-sentinel.com
- Emergency Hotline: +1-XXX-XXX-XXXX

---

**Document Version**: 2.0  
**Last Reviewed**: November 11, 2025  
**Next Review**: December 11, 2025  
**Maintained by**: APOLLO CyberSentinel DevOps Team
