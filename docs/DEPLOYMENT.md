# 🚀 Deployment Guide

## Production Deployment Options

### Option 1: Docker (Recommended)

#### Prerequisites
- Docker & Docker Compose installed
- 2GB RAM minimum
- Stable internet connection

#### Steps

```bash
# 1. Clone repository
git clone <your-repo>
cd sol

# 2. Configure environment
cp config/.env.example .env
nano .env  # Edit with your credentials

# 3. Start services
docker-compose up -d

# 4. Check logs
docker-compose logs -f trading-bot

# 5. Monitor health
curl http://localhost:8080/health
```

---

### Option 2: VPS Deployment

#### Recommended VPS Specs
- **CPU:** 2+ cores
- **RAM:** 4GB minimum
- **Storage:** 20GB SSD
- **OS:** Ubuntu 20.04 LTS or newer

#### Setup on Ubuntu

```bash
# 1. Update system
sudo apt update && sudo apt upgrade -y

# 2. Install Python 3.9+
sudo apt install python3.9 python3.9-venv python3-pip -y

# 3. Clone repository
git clone <your-repo>
cd sol

# 4. Create virtual environment
python3.9 -m venv venv
source venv/bin/activate

# 5. Install dependencies
pip install -r requirements.txt

# 6. Setup configuration
cp config/.env.example .env
nano .env  # Add your credentials

# 7. Run setup
python scripts/setup_project.py

# 8. Test bot
python scripts/run_bot.py
```

#### Run as System Service

Create `/etc/systemd/system/trading-bot.service`:

```ini
[Unit]
Description=Solana Trading Bot
After=network.target

[Service]
Type=simple
User=youruser
WorkingDirectory=/path/to/sol
Environment="PATH=/path/to/sol/venv/bin"
ExecStart=/path/to/sol/venv/bin/python scripts/run_bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable trading-bot
sudo systemctl start trading-bot
sudo systemctl status trading-bot
```

---

### Option 3: Kubernetes

#### Deployment YAML

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: trading-bot
spec:
  replicas: 1
  selector:
    matchLabels:
      app: trading-bot
  template:
    metadata:
      labels:
        app: trading-bot
    spec:
      containers:
      - name: trading-bot
        image: yourdockerhub/trading-bot:latest
        env:
        - name: TELEGRAM_BOT_TOKEN
          valueFrom:
            secretKeyRef:
              name: trading-bot-secrets
              key: telegram-token
        - name: WALLET_PRIVATE_KEY
          valueFrom:
            secretKeyRef:
              name: trading-bot-secrets
              key: wallet-key
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "2000m"
```

---

## Environment Variables

### Required

```env
TELEGRAM_BOT_TOKEN=          # From @BotFather
WALLET_PRIVATE_KEY=          # Base58 encoded
SOLANA_RPC_URL=             # Solana RPC endpoint
```

### Optional but Recommended

```env
ADMIN_CHAT_ID=              # Your Telegram user ID
MAX_TRADE_SIZE_SOL=1.0      # Maximum per trade
DAILY_LOSS_LIMIT_SOL=5.0    # Stop if exceeded
```

### Optional (Enhanced Features)

```env
TWITTER_API_KEY=            # For sentiment analysis
REDDIT_CLIENT_ID=           # For community intel
DISCORD_TOKEN=              # For Discord monitoring
```

---

## Security Best Practices

### 1. Wallet Security
- ✅ Use dedicated wallet for bot
- ✅ Fund with limited amounts
- ✅ Never share private key
- ✅ Use hardware wallet for main funds

### 2. API Key Security
- ✅ Store in environment variables
- ✅ Never commit to git
- ✅ Rotate keys regularly
- ✅ Limit key permissions

### 3. Server Security
- ✅ Enable firewall (UFW)
- ✅ Use SSH keys only
- ✅ Disable root login
- ✅ Regular security updates
- ✅ Monitor system logs

### 4. Monitoring
- ✅ Set up alerts
- ✅ Monitor daily P&L
- ✅ Watch for errors
- ✅ Regular backups

---

## Monitoring & Alerts

### Health Checks

```bash
# Check bot health
curl http://localhost:8080/health

# Check metrics
curl http://localhost:8080/metrics
```

### Logs

```bash
# Docker
docker-compose logs -f trading-bot

# Systemd
sudo journalctl -u trading-bot -f

# Log files
tail -f logs/trading_bot.log
```

### Alerts Setup

Configure admin alerts in Telegram:
- Critical errors
- Large trades
- Daily P&L limits
- System health issues

---

## Backup & Recovery

### Database Backup

```bash
# Backup SQLite database
cp trading_bot.db backups/trading_bot_$(date +%Y%m%d).db

# Automated backup script
0 2 * * * /path/to/backup_script.sh
```

### Configuration Backup

```bash
# Backup .env (encrypted)
tar czf config_backup.tar.gz .env
gpg -c config_backup.tar.gz
```

---

## Scaling

### Horizontal Scaling
- Run multiple bots with different strategies
- Use load balancer for health checks
- Shared database for analytics

### Performance Optimization
- Use premium RPC endpoints
- Enable connection pooling
- Cache frequently accessed data
- Optimize database queries

---

## Troubleshooting

### Bot Won't Start

```bash
# Check logs
docker-compose logs trading-bot

# Verify configuration
python -c "from src.config import get_config; get_config().validate()"

# Check dependencies
pip install -r requirements.txt --upgrade
```

### High Memory Usage

```bash
# Monitor resources
docker stats

# Restart bot
docker-compose restart trading-bot
```

### Database Issues

```bash
# Reinitialize database
python -c "import asyncio; from src.modules.database import DatabaseManager; asyncio.run(DatabaseManager().init_db())"
```

---

## Cost Optimization

### RPC Endpoints
- Free: `https://api.mainnet-beta.solana.com` (rate limited)
- Paid: Alchemy, QuickNode, Helius (better reliability)

### VPS Hosting
- $5/month: DigitalOcean, Vultr, Linode
- $10/month: Better performance
- $20/month: Production ready

### Estimated Monthly Costs
- VPS: $5-20
- Premium RPC: $0-50 (depending on usage)
- Database: $0 (SQLite) or $10+ (managed)
- **Total: $5-80/month**

---

## Production Checklist

Before going live:

- [ ] Tested on devnet
- [ ] Small test trades on mainnet
- [ ] All safety limits configured
- [ ] Backups automated
- [ ] Monitoring set up
- [ ] Alerts configured
- [ ] Documentation reviewed
- [ ] Emergency shutdown plan
- [ ] Tested with small amounts (<$50)
- [ ] Understand all risks

---

## Support

For deployment help:
1. Check logs first
2. Review documentation
3. Search existing issues
4. Create new issue with details

---

**Remember: Start small, test thoroughly, never risk more than you can afford to lose!**

