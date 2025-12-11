# 🔧 APOLLO CyberSentinel - Administrator Guide

**Enterprise System Administration & Operations Manual**

---

## 📋 Table of Contents

1. [System Architecture](#system-architecture)
2. [Installation & Deployment](#installation--deployment)
3. [Configuration Management](#configuration-management)
4. [Monitoring & Observability](#monitoring--observability)
5. [Database Administration](#database-administration)
6. [Security Operations](#security-operations)
7. [Performance Tuning](#performance-tuning)
8. [Backup & Recovery](#backup--recovery)
9. [Troubleshooting Guide](#troubleshooting-guide)
10. [Incident Response](#incident-response)
11. [Scaling & Capacity Planning](#scaling--capacity-planning)
12. [Maintenance Procedures](#maintenance-procedures)

---

## 🏗️ System Architecture

### High-Level Overview

```
┌─────────────────────────────────────────────────────────────┐
│                         USERS                                │
│                     (Telegram Interface)                     │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                   TRADING BOT CORE                           │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Telegram Bot Handler (webhooks + polling)          │   │
│  └──────────────┬──────────────────────────────────────┘   │
│                 │                                            │
│  ┌──────────────▼───────────────┐  ┌────────────────────┐  │
│  │  Command Router & Parser     │  │  Authentication    │  │
│  └──────────────┬───────────────┘  └────────────────────┘  │
│                 │                                            │
│  ┌──────────────▼──────────────────────────────────────┐   │
│  │              INTELLIGENCE LAYER                      │   │
│  │  ┌──────────┐ ┌──────────┐ ┌───────────┐           │   │
│  │  │ Predict  │ │  Flash   │ │  Launch   │           │   │
│  │  │  Engine  │ │  Arb     │ │ Predictor │           │   │
│  │  └──────────┘ └──────────┘ └───────────┘           │   │
│  │  ┌──────────┐ ┌──────────┐ ┌───────────┐           │   │
│  │  │  Wallet  │ │ Sentiment│ │ Security  │           │   │
│  │  │ Tracker  │ │  Scanner │ │  Shield   │           │   │
│  │  └──────────┘ └──────────┘ └───────────┘           │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌───────────────────────────────────────────────────────┐ │
│  │              EXECUTION LAYER                           │ │
│  │  ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐     │ │
│  │  │Jupiter │  │Raydium │  │  Orca  │  │Marginfi│     │ │
│  │  │  API   │  │  API   │  │  API   │  │  Flash │     │ │
│  │  └────────┘  └────────┘  └────────┘  └────────┘     │ │
│  └───────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                   DATA LAYER                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │ PostgreSQL  │  │   Redis     │  │  File Store │         │
│  │  (Primary)  │  │  (Cache)    │  │   (Logs)    │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
└──────────────────────────────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│              EXTERNAL INTEGRATIONS                           │
│  ┌────────────────────────────────────────────────────┐     │
│  │ Solana RPC (Helius + 5 fallbacks)                 │     │
│  │ DexScreener, Birdeye, Jupiter, Twitter, Reddit    │     │
│  │ RugCheck, GoPlus, TokenSniffer, RugDoc, etc.      │     │
│  └────────────────────────────────────────────────────┘     │
└──────────────────────────────────────────────────────────────┘
```

### Component Breakdown

**1. Trading Bot Core** (Node.js)
- Telegram bot handler
- Command routing and parsing
- Business logic orchestration
- Error handling and retries

**2. Intelligence Layer** (Python + Node.js)
- Phase 1: Prediction engine (ML models)
- Phase 2: Flash arbitrage scanner
- Phase 3: Launch predictor (social + on-chain)
- Phase 4: Prediction markets
- Wallet intelligence (441 wallets)
- Sentiment analysis
- 8-layer security system

**3. Execution Layer**
- DEX integrations (Jupiter, Raydium, Orca)
- Flash loan protocol (Marginfi)
- Transaction builders
- MEV protection (Jito)

**4. Data Layer**
- PostgreSQL: Transactional data
- Redis: Caching + pub/sub
- File system: Logs + backups

**5. External APIs**
- 26+ integrations
- Multi-source redundancy
- Intelligent failover

---

## 🚀 Installation & Deployment

### Prerequisites

**System Requirements:**
- OS: Ubuntu 22.04 LTS (recommended)
- CPU: 4 cores minimum (8 cores recommended)
- RAM: 8GB minimum (16GB recommended)
- Storage: 50GB NVMe SSD
- Network: 100 Mbps (1 Gbps recommended)

**Software Requirements:**
```bash
Docker >= 24.0.0
Docker Compose >= 2.20.0
Git >= 2.30.0
```

### Installation Steps

**1. Clone Repository**
```bash
git clone https://github.com/apollosentinel/trading-bot.git
cd trading-bot
```

**2. Environment Configuration**
```bash
# Copy example environment file
cp .env.example .env

# Edit configuration
nano .env
```

**Critical Environment Variables:**

```bash
# Core Settings
NODE_ENV=production
PORT=8080
LOG_LEVEL=info

# Telegram
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_WEBHOOK_URL=https://yourdomain.com/webhook

# Database
DATABASE_URL=postgresql://trader:password@trading-bot-db:5432/trading_bot
REDIS_URL=redis://trading-bot-redis:6379

# Solana
SOLANA_RPC_URL=https://your-helius-rpc.com
SOLANA_PRIVATE_KEY=your_encrypted_master_key
SOLANA_NETWORK=mainnet-beta

# API Keys (26+ integrations)
DEXSCREENER_API_KEY=your_key
BIRDEYE_API_KEY=your_key
JUPITER_API_KEY=your_key
TWITTER_BEARER_TOKEN=your_key
REDDIT_CLIENT_ID=your_key
# ... (see envconfig.txt for complete list)

# Security
JWT_SECRET=your_256bit_secret
ENCRYPTION_KEY=your_256bit_encryption_key
ALLOW_BROADCAST=false  # SET TO true FOR PRODUCTION!

# Trading Limits
MAX_TRADE_AMOUNT_SOL=100
MAX_DAILY_VOLUME_SOL=1000
CIRCUIT_BREAKER_THRESHOLD=5

# Flash Loans
MARGINFI_PROGRAM_ID=your_program_id
FLASH_LOAN_FEE_PERCENT=0.001

# Monitoring
SENTRY_DSN=your_sentry_dsn
PROMETHEUS_PORT=9090
```

**3. Build & Deploy**

**Development:**
```bash
docker-compose up --build
```

**Production:**
```bash
docker-compose -f docker-compose.prod.yml up -d --build
```

**4. Verify Deployment**
```bash
# Check container status
docker-compose -f docker-compose.prod.yml ps

# Check logs
docker-compose -f docker-compose.prod.yml logs -f trading-bot

# Health check
curl http://localhost:8080/ready

# Test Telegram bot
# Message @gonehuntingbot on Telegram: /start
```

**5. Database Initialization**
```bash
# Run migrations
docker exec trading-bot-app npm run migrate

# Seed elite wallets (441 pre-loaded)
docker exec trading-bot-app npm run seed:wallets

# Seed base tokens (7 Solana pairs)
docker exec trading-bot-app npm run seed:tokens
```

---

## ⚙️ Configuration Management

### Environment Files

**Structure:**
```
/app
├── .env                 # Main configuration
├── .env.example         # Template
├── envconfig.txt        # Detailed documentation
└── config/
    ├── database.js
    ├── redis.js
    ├── telegram.js
    ├── trading.js
    └── security.js
```

### Critical Configuration Sections

**1. Twitter Configuration (Consolidated)**
```bash
# Twitter API Settings
TWITTER_ENABLED=true
TWITTER_API_METHOD=twikit  # Primary: unlimited, no rate limits
TWITTER_API_FALLBACK=official  # Fallback only

# Quality Filters (Unified - NO DUPLICATES)
MIN_TWITTER_FOLLOWERS=1000  # Higher quality
MIN_TWITTER_ACCOUNT_AGE_DAYS=60  # Stricter

# Scanning
TWITTER_SCAN_INTERVAL_MS=180000  # 3 minutes
TWITTER_KEYWORDS=Solana gem,$$SOL new token,moon,100x
```

**2. Security Configuration**
```bash
# 8-Layer Security System
RUGCHECK_API_KEY=your_key
GOPLUS_API_KEY=your_key
TOKENSNIFFER_API_KEY=your_key
RUGDOC_API_URL=https://api.rugdoc.io
BIRDEYE_SECURITY_ENDPOINT=enabled
SOLANA_BEACH_API=your_key

# Internal Security
HONEYPOT_DETECTION_ENABLED=true
AUTHORITY_CHECK_ENABLED=true
MIN_LIQUIDITY_SOL=5
MIN_HOLDERS=100
SECURITY_LAYERS_REQUIRED=6  # Out of 8 must pass
```

**3. Trading Configuration**
```bash
# Limits by Tier
BRONZE_MAX_TRADE_SOL=10
BRONZE_MAX_DAILY_SOL=50
SILVER_MAX_TRADE_SOL=25
SILVER_MAX_DAILY_SOL=100
GOLD_MAX_TRADE_SOL=50
GOLD_MAX_DAILY_SOL=250
PLATINUM_MAX_TRADE_SOL=150
PLATINUM_MAX_DAILY_SOL=750
ELITE_MAX_TRADE_SOL=500
ELITE_MAX_DAILY_SOL=unlimited

# Auto-Trading
AUTO_PREDICTIONS_ENABLED=true
AUTO_PREDICTIONS_MIN_CONFIDENCE=90
AUTO_PREDICTIONS_MAX_DAILY_TRADES=25
AUTO_PREDICTIONS_MAX_DAILY_AMOUNT=10

# Circuit Breaker
CIRCUIT_BREAKER_ENABLED=true
CIRCUIT_BREAKER_THRESHOLD=5  # Consecutive losses
CIRCUIT_BREAKER_COOLDOWN_MIN=60
```

**4. Performance Configuration**
```bash
# RPC Redundancy (5 fallbacks)
SOLANA_RPC_PRIMARY=https://helius.rpc
SOLANA_RPC_FALLBACK_1=https://alchemy.rpc
SOLANA_RPC_FALLBACK_2=https://quicknode.rpc
SOLANA_RPC_FALLBACK_3=https://getblock.rpc
SOLANA_RPC_FALLBACK_4=https://chainstack.rpc
RPC_TIMEOUT_MS=5000
RPC_MAX_RETRIES=3

# Database Pooling
DB_POOL_MIN=2
DB_POOL_MAX=20
DB_IDLE_TIMEOUT_MS=30000

# Redis
REDIS_MAX_RETRIES=10
REDIS_RETRY_DELAY_MS=500
```

### Configuration Validation

```bash
# Run configuration validator
docker exec trading-bot-app npm run validate:config

# Expected output:
✅ Environment variables: 110/110 present
✅ API keys: 26/26 valid
✅ Database connection: OK
✅ Redis connection: OK
✅ RPC endpoints: 6/6 reachable
✅ Twitter config: NO DUPLICATES
✅ Security layers: 8/8 configured
✅ Trading limits: Properly set
🎉 Configuration is VALID
```

---

## 📊 Monitoring & Observability

### Health Check Endpoints

**1. `/health` - Basic Liveness**
```bash
curl http://localhost:8080/health

# Response (200 OK):
{
  "status": "ok",
  "timestamp": "2025-11-11T17:30:00Z"
}
```

**2. `/ready` - Readiness Check**
```bash
curl http://localhost:8080/ready

# Response (200 OK or 503 Service Unavailable):
{
  "status": "ready",  # or "not_ready"
  "services": {
    "database": "connected",
    "redis": "connected",
    "rpc": "connected",
    "apis": {
      "dexscreener": "operational",
      "birdeye": "operational",
      "jupiter": "operational"
    }
  },
  "version": "4.5.0",
  "uptime": "99.97%"
}
```

**3. `/status` - Detailed Metrics**
```bash
curl http://localhost:8080/status

# Returns comprehensive system status
```

### Logging

**Log Levels:**
```
ERROR - Critical issues requiring immediate attention
WARN  - Potential issues to monitor
INFO  - General operational messages
DEBUG - Detailed debugging information
```

**Log Locations:**
```bash
# Application logs
/app/logs/trading_bot.jsonl
/app/logs/error.jsonl

# System logs
docker-compose logs -f trading-bot

# Filter by level
docker exec trading-bot-app grep '"level":"ERROR"' logs/trading_bot.jsonl | tail -20

# Filter by feature
docker-compose logs trading-bot | Select-String "prediction|flash|launch"
```

**Log Rotation:**
```bash
# Logs rotate daily, retain 30 days
# Location: /app/logs/
# Format: trading_bot.YYYY-MM-DD.jsonl
```

### Prometheus Metrics

**Exposed on:** `http://localhost:9090/metrics`

**Key Metrics:**
```
# Trading Metrics
trading_bot_trades_total{phase="predictions",outcome="win"}
trading_bot_trades_total{phase="flash_loans",outcome="win"}
trading_bot_pnl_sol{user_tier="gold"}
trading_bot_win_rate{phase="predictions"}

# Performance Metrics
trading_bot_request_duration_seconds{endpoint="/api/predict"}
trading_bot_database_query_duration_seconds{query_type="insert"}
trading_bot_rpc_latency_seconds{rpc="helius"}

# System Metrics
trading_bot_active_users
trading_bot_tokens_monitored
trading_bot_elite_wallets_tracked
trading_bot_security_alerts_total

# API Health
trading_bot_api_health{service="dexscreener",status="up"}
trading_bot_api_latency_seconds{service="birdeye"}
```

### Grafana Dashboards

**Pre-configured dashboards:**
1. **Overview Dashboard** - High-level metrics
2. **Trading Performance** - Win rates, P&L, phases
3. **System Health** - Infrastructure metrics
4. **Security Dashboard** - 8-layer monitoring
5. **API Health** - External service status

**Access:** `http://localhost:3000` (default credentials: admin/admin)

### Alerting

**Alert Manager Rules:**

```yaml
# Critical Alerts (PagerDuty)
- name: critical
  rules:
  - alert: DatabaseDown
    expr: trading_bot_database_status == 0
    for: 1m
    
  - alert: HighErrorRate
    expr: rate(trading_bot_errors_total[5m]) > 10
    for: 5m
    
  - alert: CircuitBreakerActive
    expr: trading_bot_circuit_breaker_active == 1
    for: 1m

# Warning Alerts (Slack)
- name: warnings
  rules:
  - alert: LowRPCPerformance
    expr: trading_bot_rpc_latency_seconds > 2
    for: 10m
    
  - alert: HighMemoryUsage
    expr: process_resident_memory_bytes > 7e9
    for: 15m
    
  - alert: APISlowdown
    expr: trading_bot_api_latency_seconds{service="birdeye"} > 1
    for: 10m
```

---

## 🗄️ Database Administration

### Schema Overview

**Core Tables:**
```sql
-- User Management
users (user_id, telegram_id, created_at, tier, points)
user_wallets (id, user_id, address, encrypted_private_key, balance)
user_settings (user_id, auto_trade, risk_level, notifications)

-- Trading
trades (id, user_id, token, type, amount, price, timestamp, success, pnl)
positions (id, user_id, token, entry_price, current_price, quantity)

-- Copy Trading
tracked_wallets (id, address, score, tier, win_rate, total_pnl, followers)
copy_relationships (id, user_id, wallet_address, copy_amount, active)

-- Predictions
predictions (id, token, direction, confidence, outcome, accuracy)
prediction_stats (user_id, total, wins, losses, accuracy_rate)

-- Flash Loans
flash_loan_history (id, user_id, borrow_amount, profit, fee, timestamp)
arbitrage_opportunities (id, token, price_diff, potential_profit)

-- Launch Predictor
launch_predictions (id, token, confidence, social_score, launch_time)
launch_outcomes (id, prediction_id, actual_launch, price_change_6h)

-- Prediction Markets
prediction_markets (id, question, pool_up, pool_down, deadline, resolved)
market_stakes (id, market_id, user_id, outcome, amount, staked_at)
```

### Common Database Operations

**1. Connect to Database**
```bash
docker exec -it trading-bot-db psql -U trader -d trading_bot
```

**2. Check Database Status**
```sql
-- Connection count
SELECT count(*) FROM pg_stat_activity;

-- Database size
SELECT pg_size_pretty(pg_database_size('trading_bot'));

-- Table sizes
SELECT 
  schemaname, tablename,
  pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
LIMIT 10;

-- Long-running queries
SELECT pid, now() - query_start AS duration, query
FROM pg_stat_activity
WHERE state = 'active'
  AND now() - query_start > interval '1 minute';
```

**3. Performance Tuning**
```sql
-- Missing indexes (run weekly)
SELECT 
  schemaname, tablename, attname, correlation
FROM pg_stats
WHERE schemaname = 'public'
  AND correlation < 0.5;

-- Index usage
SELECT 
  schemaname, tablename, indexname, idx_scan, idx_tup_read, idx_tup_fetch
FROM pg_stat_user_indexes
ORDER BY idx_scan ASC
LIMIT 20;

-- Vacuum status
SELECT 
  schemaname, tablename, last_vacuum, last_autovacuum,
  n_tup_ins, n_tup_upd, n_tup_del
FROM pg_stat_user_tables;
```

**4. Data Cleanup**
```sql
-- Delete old trades (retain 90 days)
DELETE FROM trades WHERE timestamp < NOW() - INTERVAL '90 days';

-- Archive old logs
INSERT INTO trades_archive SELECT * FROM trades 
WHERE timestamp < NOW() - INTERVAL '90 days';

-- Vacuum after large deletions
VACUUM ANALYZE trades;
```

### Backup Procedures

**Automated Daily Backups:**
```bash
# Backup script (runs at 2 AM daily via cron)
#!/bin/bash
DATE=$(date +%Y-%m-%d)
BACKUP_DIR="/backups"
DB_NAME="trading_bot"

# Backup database
docker exec trading-bot-db pg_dump -U trader $DB_NAME | gzip > $BACKUP_DIR/db_$DATE.sql.gz

# Backup Redis (if persistence enabled)
docker exec trading-bot-redis redis-cli BGSAVE

# Backup logs
tar -czf $BACKUP_DIR/logs_$DATE.tar.gz /app/logs/

# Backup .env (encrypted)
gpg --encrypt --recipient admin@apollosentinel.com .env > $BACKUP_DIR/env_$DATE.gpg

# Retention: 30 daily, 12 monthly
find $BACKUP_DIR -name "db_*.sql.gz" -mtime +30 -delete

echo "✅ Backup completed: $DATE"
```

**Manual Backup:**
```bash
# Database
docker exec trading-bot-db pg_dump -U trader trading_bot > backup_$(date +%Y%m%d).sql

# Redis
docker exec trading-bot-redis redis-cli SAVE
docker cp trading-bot-redis:/data/dump.rdb ./backup_redis_$(date +%Y%m%d).rdb
```

**Restore from Backup:**
```bash
# Database
docker exec -i trading-bot-db psql -U trader trading_bot < backup_20251111.sql

# Redis
docker cp backup_redis_20251111.rdb trading-bot-redis:/data/dump.rdb
docker restart trading-bot-redis
```

---

## 🔒 Security Operations

### Encryption

**Private Keys:**
```javascript
// Encryption at rest (AES-256-GCM)
const crypto = require('crypto');
const algorithm = 'aes-256-gcm';
const key = Buffer.from(process.env.ENCRYPTION_KEY, 'hex');

function encrypt(text) {
  const iv = crypto.randomBytes(16);
  const cipher = crypto.createCipheriv(algorithm, key, iv);
  let encrypted = cipher.update(text, 'utf8', 'hex');
  encrypted += cipher.final('hex');
  const authTag = cipher.getAuthTag();
  return {
    encrypted,
    iv: iv.toString('hex'),
    authTag: authTag.toString('hex')
  };
}

function decrypt(encrypted, iv, authTag) {
  const decipher = crypto.createDecipheriv(
    algorithm,
    key,
    Buffer.from(iv, 'hex')
  );
  decipher.setAuthTag(Buffer.from(authTag, 'hex'));
  let decrypted = decipher.update(encrypted, 'hex', 'utf8');
  decrypted += decipher.final('utf8');
  return decrypted;
}
```

**API Keys:**
- Stored in environment variables
- Never logged or exposed
- Rotated every 90 days
- Separate keys per environment

### Access Control

**Role-Based Access:**
```
SUPER_ADMIN:
  - Full system access
  - Configuration changes
  - User management
  - Emergency stop

ADMIN:
  - System monitoring
  - Log access
  - Database read-only
  - Alert management

SUPPORT:
  - User lookup
  - Transaction history
  - Basic troubleshooting
  - No financial operations

USER:
  - Own wallet only
  - Trading operations
  - Statistics viewing
  - Settings management
```

**IP Whitelisting (Production):**
```bash
# In .env
ALLOWED_IPS=1.2.3.4,5.6.7.8,9.10.11.12

# In nginx.conf
allow 1.2.3.4;
allow 5.6.7.8;
allow 9.10.11.12;
deny all;
```

### Security Monitoring

**Real-time Alerts:**
```bash
# Suspicious activity patterns
- Multiple failed login attempts (5+ in 5 min)
- Unusual withdrawal amounts (>50 SOL)
- API key usage from new IP
- Admin action from non-admin IP
- Database queries taking >10 seconds
```

**Security Audit Log:**
```sql
-- Security events table
CREATE TABLE security_events (
  id SERIAL PRIMARY KEY,
  event_type VARCHAR(50),
  severity VARCHAR(20),
  user_id BIGINT,
  ip_address INET,
  details JSONB,
  timestamp TIMESTAMPTZ DEFAULT NOW()
);

-- Query security events
SELECT * FROM security_events 
WHERE severity = 'CRITICAL' 
  AND timestamp > NOW() - INTERVAL '24 hours'
ORDER BY timestamp DESC;
```

---

## ⚡ Performance Tuning

### Database Optimization

**Connection Pooling:**
```javascript
// config/database.js
const pool = new Pool({
  host: process.env.DB_HOST,
  port: 5432,
  database: process.env.DB_NAME,
  user: process.env.DB_USER,
  password: process.env.DB_PASSWORD,
  min: 2,
  max: 20,
  idleTimeoutMillis: 30000,
  connectionTimeoutMillis: 2000
});
```

**Query Optimization:**
```sql
-- Add indexes for frequent queries
CREATE INDEX idx_trades_user_timestamp ON trades(user_id, timestamp DESC);
CREATE INDEX idx_trades_token_timestamp ON trades(token, timestamp DESC);
CREATE INDEX idx_positions_user_active ON positions(user_id) WHERE active = true;
CREATE INDEX idx_wallets_score ON tracked_wallets(score DESC);

-- Partial indexes for active data
CREATE INDEX idx_active_markets ON prediction_markets(deadline) WHERE resolved = false;
CREATE INDEX idx_pending_stakes ON market_stakes(market_id) WHERE status = 'pending';
```

### Redis Optimization

**Memory Management:**
```bash
# redis.conf
maxmemory 4gb
maxmemory-policy allkeys-lru  # Evict least recently used

# Key patterns
prediction:<token>:<timestamp>  # TTL: 6 hours
arbitrage:<dex_pair>            # TTL: 30 seconds
wallet:<address>:trades         # TTL: 1 hour
cache:<endpoint>:<params>       # TTL: 5 minutes
```

**Pub/Sub for Real-time:**
```javascript
// Publish trade execution
redis.publish('trades', JSON.stringify({
  user_id: 12345,
  token: 'EPjF...',
  type: 'BUY',
  amount: 1.5,
  success: true
}));

// Subscribe to updates
redis.subscribe('trades', 'predictions', 'security_alerts');
```

### RPC Optimization

**Connection Pooling:**
```javascript
const { Connection } = require('@solana/web3.js');

// Primary + fallbacks
const rpcEndpoints = [
  process.env.SOLANA_RPC_PRIMARY,
  process.env.SOLANA_RPC_FALLBACK_1,
  process.env.SOLANA_RPC_FALLBACK_2,
  process.env.SOLANA_RPC_FALLBACK_3,
  process.env.SOLANA_RPC_FALLBACK_4
];

let currentRPCIndex = 0;

async function getRPCConnection() {
  try {
    const connection = new Connection(
      rpcEndpoints[currentRPCIndex],
      'confirmed'
    );
    await connection.getLatestBlockhash();  // Health check
    return connection;
  } catch (error) {
    currentRPCIndex = (currentRPCIndex + 1) % rpcEndpoints.length;
    return getRPCConnection();  // Try next RPC
  }
}
```

### API Rate Limiting

**Per-User Rate Limits:**
```javascript
const rateLimit = require('express-rate-limit');

const limiter = rateLimit({
  store: new RedisStore({ client: redis }),
  keyGenerator: (req) => req.user.tier,  // Rate limit by tier
  max: (req) => {
    const limits = {
      bronze: 100,
      silver: 200,
      gold: 500,
      platinum: 1000,
      elite: Infinity
    };
    return limits[req.user.tier];
  },
  windowMs: 60 * 1000,  // 1 minute
  message: 'Too many requests, please upgrade your tier.'
});

app.use('/api/', limiter);
```

---

## 💾 Backup & Recovery

### Backup Strategy

**3-2-1 Rule:**
- 3 copies of data
- 2 different storage types (disk + S3)
- 1 offsite location

**Backup Schedule:**
```
Daily: Full database + Redis + logs
Weekly: Configuration files
Monthly: Complete system snapshot
```

**Automated Script:**
```bash
#!/bin/bash
# /scripts/backup.sh

set -e

DATE=$(date +%Y-%m-%d_%H-%M)
BACKUP_DIR="/backups/$DATE"
S3_BUCKET="s3://apollosentinel-backups"

mkdir -p $BACKUP_DIR

# 1. Database
echo "Backing up database..."
docker exec trading-bot-db pg_dump -U trader trading_bot | gzip > $BACKUP_DIR/database.sql.gz

# 2. Redis
echo "Backing up Redis..."
docker exec trading-bot-redis redis-cli SAVE
docker cp trading-bot-redis:/data/dump.rdb $BACKUP_DIR/redis.rdb

# 3. Logs
echo "Backing up logs..."
tar -czf $BACKUP_DIR/logs.tar.gz /app/logs/

# 4. Configuration
echo "Backing up configuration..."
tar -czf $BACKUP_DIR/config.tar.gz /app/.env /app/docker-compose.prod.yml

# 5. Upload to S3
echo "Uploading to S3..."
aws s3 sync $BACKUP_DIR $S3_BUCKET/$DATE

# 6. Verify backup
echo "Verifying backup integrity..."
gzip -t $BACKUP_DIR/database.sql.gz
aws s3 ls $S3_BUCKET/$DATE/

# 7. Cleanup old backups (retain 30 days local, 90 days S3)
find /backups -type d -mtime +30 -exec rm -rf {} +
aws s3 ls $S3_BUCKET/ | awk '{print $4}' | while read date; do
  if [[ $(date -d "$date" +%s) -lt $(date -d "90 days ago" +%s) ]]; then
    aws s3 rm --recursive $S3_BUCKET/$date
  fi
done

echo "✅ Backup completed successfully: $DATE"
```

### Disaster Recovery

**Recovery Time Objective (RTO):** 30 minutes  
**Recovery Point Objective (RPO):** 24 hours (daily backups)

**Full System Recovery:**
```bash
#!/bin/bash
# /scripts/restore.sh

BACKUP_DATE=$1  # e.g., 2025-11-11_02-00

if [ -z "$BACKUP_DATE" ]; then
  echo "Usage: ./restore.sh YYYY-MM-DD_HH-MM"
  exit 1
fi

S3_BUCKET="s3://apollosentinel-backups"
RESTORE_DIR="/restore/$BACKUP_DATE"

echo "🚨 DISASTER RECOVERY MODE"
echo "Restoring from backup: $BACKUP_DATE"
read -p "Continue? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
  echo "Aborted."
  exit 1
fi

# 1. Stop all services
echo "Stopping services..."
docker-compose -f docker-compose.prod.yml down

# 2. Download backup from S3
echo "Downloading backup..."
mkdir -p $RESTORE_DIR
aws s3 sync $S3_BUCKET/$BACKUP_DATE $RESTORE_DIR

# 3. Restore database
echo "Restoring database..."
gunzip < $RESTORE_DIR/database.sql.gz | docker exec -i trading-bot-db psql -U trader trading_bot

# 4. Restore Redis
echo "Restoring Redis..."
docker cp $RESTORE_DIR/redis.rdb trading-bot-redis:/data/dump.rdb
docker start trading-bot-redis

# 5. Restore logs
echo "Restoring logs..."
tar -xzf $RESTORE_DIR/logs.tar.gz -C /

# 6. Restore configuration
echo "Restoring configuration..."
tar -xzf $RESTORE_DIR/config.tar.gz -C /app

# 7. Start services
echo "Starting services..."
docker-compose -f docker-compose.prod.yml up -d

# 8. Verify health
echo "Verifying system health..."
sleep 30
curl http://localhost:8080/ready

echo "✅ System restored successfully"
echo "⚠️ Verify all services manually"
```

---

## 🔧 Troubleshooting Guide

### Common Issues

**1. Bot Not Responding**

**Symptoms:** Telegram messages not answered

**Diagnosis:**
```bash
# Check container status
docker ps | grep trading-bot

# Check logs
docker-compose logs -f trading-bot | tail -50

# Check Telegram webhook
curl -X GET "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/getWebhookInfo"
```

**Solutions:**
```bash
# Restart bot
docker-compose -f docker-compose.prod.yml restart trading-bot

# Clear webhook and use polling (fallback)
curl -X POST "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/deleteWebhook"
docker-compose -f docker-compose.prod.yml restart trading-bot

# Check .env
grep TELEGRAM_BOT_TOKEN .env  # Ensure valid token
```

---

**2. Database Connection Failed**

**Symptoms:** "ECONNREFUSED" or "database is unavailable"

**Diagnosis:**
```bash
# Check database container
docker ps | grep trading-bot-db

# Check database logs
docker logs trading-bot-db

# Try manual connection
docker exec -it trading-bot-db psql -U trader -d trading_bot
```

**Solutions:**
```bash
# Restart database
docker-compose restart trading-bot-db

# Check connection string
grep DATABASE_URL .env

# Check network
docker network inspect trading-bot_default
```

---

**3. High Memory Usage**

**Symptoms:** Container using >7GB RAM, slowdowns

**Diagnosis:**
```bash
# Check memory usage
docker stats trading-bot-app

# Check Node.js heap
docker exec trading-bot-app node -e "console.log(process.memoryUsage())"

# Check for memory leaks
docker exec trading-bot-app npm run heap-snapshot
```

**Solutions:**
```bash
# Increase Node.js heap limit
# In docker-compose.prod.yml:
environment:
  - NODE_OPTIONS=--max-old-space-size=8192

# Restart with garbage collection
docker-compose restart trading-bot-app

# Check for memory leaks in code
docker exec trading-bot-app npm run leak-check
```

---

**4. RPC Connection Timeout**

**Symptoms:** "RPC connection failed", slow transactions

**Diagnosis:**
```bash
# Test RPC endpoints
for rpc in $SOLANA_RPC_PRIMARY $SOLANA_RPC_FALLBACK_1; do
  curl -X POST $rpc -H "Content-Type: application/json" -d '{"jsonrpc":"2.0","id":1,"method":"getHealth"}'
done

# Check logs for RPC errors
docker-compose logs trading-bot | grep "RPC"
```

**Solutions:**
```bash
# Force RPC rotation
docker exec trading-bot-app npm run force-rpc-rotation

# Update RPC URLs in .env
nano .env  # Update SOLANA_RPC_PRIMARY

# Restart bot
docker-compose restart trading-bot-app
```

---

**5. API Rate Limit (429 Errors)**

**Symptoms:** "Too Many Requests" errors

**Diagnosis:**
```bash
# Check for 429 errors
docker-compose logs trading-bot | grep "429"

# Identify which API
docker-compose logs trading-bot | grep "rate limit"
```

**Solutions:**
```bash
# Twitter: Already using Twikit (unlimited)
grep TWITTER_API_METHOD .env  # Should be "twikit"

# Other APIs: Check rate limits
# DexScreener: 300 req/min
# Birdeye: 100 req/min
# Jupiter: 600 req/min

# Reduce scan frequency if needed
# In .env:
TWITTER_SCAN_INTERVAL_MS=300000  # 5 minutes instead of 3
```

---

## 🚨 Incident Response

### Severity Levels

**P0 - Critical (Response: Immediate)**
- System completely down
- Database corruption
- Security breach
- Financial loss

**P1 - High (Response: <15 min)**
- Degraded performance (>50% slower)
- One major feature broken
- RPC connection lost
- High error rate (>5%)

**P2 - Medium (Response: <1 hour)**
- Minor feature broken
- Slow response times
- Non-critical API down

**P3 - Low (Response: <4 hours)**
- Cosmetic issues
- Minor bugs
- Enhancement requests

### Incident Response Runbook

**P0 - System Down:**
```bash
1. Notify team immediately (PagerDuty + Slack)
2. Check infrastructure:
   - docker ps | grep trading-bot
   - curl http://localhost:8080/health
3. Check external dependencies:
   - RPC endpoints
   - Database
   - Redis
4. Emergency restart:
   - docker-compose -f docker-compose.prod.yml restart
5. If still down:
   - Check logs: docker logs trading-bot-app --tail=100
   - Restore from backup if necessary
6. Post-incident:
   - Write incident report
   - Update runbooks
   - Implement preventive measures
```

**P1 - Database Connection Lost:**
```bash
1. Check database status:
   - docker ps | grep trading-bot-db
   - docker logs trading-bot-db
2. Verify connection string in .env
3. Check network:
   - docker network ls
   - docker network inspect trading-bot_default
4. Restart database:
   - docker-compose restart trading-bot-db
5. Restart bot:
   - docker-compose restart trading-bot-app
6. Monitor for 15 minutes
```

### On-Call Procedures

**On-Call Checklist:**
```
✅ Laptop with VPN access
✅ Phone with PagerDuty app
✅ Admin credentials saved
✅ SSH keys configured
✅ Backup restore script tested
✅ Emergency contact list
```

**Escalation Path:**
```
Level 1: On-call engineer (15 min response)
Level 2: Senior engineer (30 min response)
Level 3: CTO (immediate response)
```

---

## 📈 Scaling & Capacity Planning

### Current Capacity

**Tested Limits:**
- Concurrent users: 10,000+
- Commands/second: 100+
- Database connections: 20 pool
- RPC requests: 600/min (Jupiter)
- Memory: 2-4GB typical usage

### Horizontal Scaling

**Load Balancer Setup:**
```yaml
# docker-compose.scale.yml
version: '3.8'
services:
  trading-bot-1:
    <<: *trading-bot-base
    container_name: trading-bot-1
  
  trading-bot-2:
    <<: *trading-bot-base
    container_name: trading-bot-2
  
  trading-bot-3:
    <<: *trading-bot-base
    container_name: trading-bot-3
  
  nginx:
    image: nginx:alpine
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    ports:
      - "80:80"
    depends_on:
      - trading-bot-1
      - trading-bot-2
      - trading-bot-3
```

**nginx.conf:**
```nginx
upstream trading_bot {
  least_conn;
  server trading-bot-1:8080;
  server trading-bot-2:8080;
  server trading-bot-3:8080;
}

server {
  listen 80;
  location / {
    proxy_pass http://trading_bot;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
  }
}
```

### Database Scaling

**Read Replicas:**
```yaml
services:
  postgres-primary:
    image: postgres:15
    environment:
      POSTGRES_REPLICATION_MODE: master
  
  postgres-replica-1:
    image: postgres:15
    environment:
      POSTGRES_REPLICATION_MODE: slave
      POSTGRES_MASTER_HOST: postgres-primary
```

**Query Routing:**
```javascript
// Read from replica
const replica = new Pool({ host: 'postgres-replica-1', ... });
const reads = await replica.query('SELECT * FROM trades WHERE...');

// Write to primary
const primary = new Pool({ host: 'postgres-primary', ... });
const writes = await primary.query('INSERT INTO trades VALUES...');
```

### Capacity Planning

**Growth Projections:**
```
Current: 156 active users
Year 1: 5,000 users (32x growth)
Year 2: 50,000 users (320x growth)
Year 3: 500,000 users (3,200x growth)
```

**Infrastructure Needs:**

| Users | Servers | DB Cores | RAM | Storage |
|-------|---------|----------|-----|---------|
| 156 | 1 | 4 | 8GB | 50GB |
| 5,000 | 3 | 8 | 16GB | 200GB |
| 50,000 | 10 | 16 | 64GB | 1TB |
| 500,000 | 50 | 32 | 256GB | 10TB |

---

## 🔄 Maintenance Procedures

### Routine Maintenance

**Daily:**
```bash
# Automated tasks
- Health check monitoring
- Error log review
- Backup verification
- API rate limit check
```

**Weekly:**
```bash
# Manual tasks
- Review security logs
- Check database performance
- Update API keys if needed
- Review and respond to user feedback
```

**Monthly:**
```bash
# Planned maintenance
- Software updates (dependencies)
- Database optimization (VACUUM, REINDEX)
- Security patches
- Capacity review
```

**Quarterly:**
```bash
# Major updates
- OS updates (Ubuntu)
- Major version upgrades (Node.js, PostgreSQL)
- Security audit
- Disaster recovery drill
```

### Software Updates

**Zero-Downtime Deployment:**
```bash
#!/bin/bash
# deploy.sh

# 1. Pull latest code
git pull origin main

# 2. Build new image
docker build -t trading-bot:new .

# 3. Tag as latest
docker tag trading-bot:new trading-bot:latest

# 4. Rolling restart (one container at a time)
for container in trading-bot-1 trading-bot-2 trading-bot-3; do
  echo "Updating $container..."
  docker stop $container
  docker rm $container
  docker-compose -f docker-compose.scale.yml up -d $container
  sleep 30  # Wait for health check
done

# 5. Verify deployment
curl http://localhost/health

echo "✅ Deployment complete"
```

### Database Maintenance

**Weekly Vacuum:**
```sql
-- Run during low-traffic hours (2 AM)
VACUUM (ANALYZE, VERBOSE) trades;
VACUUM (ANALYZE, VERBOSE) positions;
VACUUM (ANALYZE, VERBOSE) tracked_wallets;

-- Check bloat
SELECT 
  schemaname, tablename,
  pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size,
  (pgstattuple(schemaname||'.'||tablename)).dead_tuple_percent AS bloat_pct
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

**Monthly Reindex:**
```sql
-- Reindex critical tables
REINDEX TABLE CONCURRENTLY trades;
REINDEX TABLE CONCURRENTLY positions;
REINDEX TABLE CONCURRENTLY tracked_wallets;
```

---

## 📞 Support & Escalation

**Support Channels:**
- **Tier 1 (Users):** Telegram @gonehuntingbot
- **Tier 2 (Admins):** Slack #ops-support
- **Tier 3 (Critical):** PagerDuty

**Contact Information:**
- **DevOps Lead:** devops@apollosentinel.com
- **CTO:** cto@apollosentinel.com
- **On-Call:** +1-555-APOLLO-1

**Documentation:**
- **Internal Wiki:** wiki.apollosentinel.com
- **Runbooks:** runbooks.apollosentinel.com
- **API Docs:** docs.apollosentinel.com

---

**Last Updated:** November 11, 2025  
**Version:** 4.5.0  
**Maintainer:** APOLLO CyberSentinel DevOps Team  
**Made with 💎 by APOLLO CyberSentinel**
