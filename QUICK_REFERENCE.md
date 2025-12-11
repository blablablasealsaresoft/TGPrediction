# 🚀 APOLLO Dashboard - Quick Reference Card

## Start Commands

```bash
# Windows
start_dashboard.bat

# Linux/Mac
./start_dashboard.sh

# Docker
docker-compose up -d

# Manual
python scripts/run_bot.py
```

## URLs

| Service | URL |
|---------|-----|
| Landing | http://localhost:8080/ |
| Dashboard | http://localhost:8080/dashboard |
| Market | http://localhost:8080/prediction-market |
| Docs | http://localhost:8080/docs |
| API | http://localhost:8080/api/v1/ |
| Health | http://localhost:8080/health |
| WebSocket | ws://localhost:8080/ws |

## API Endpoints

```bash
# Metrics
GET /api/v1/metrics
GET /api/v1/performance
GET /api/v1/trades/recent
GET /api/v1/trades/top-tokens

# Phases
GET /api/v1/phases/status
GET /api/v1/predictions/stats
GET /api/v1/flash/stats
GET /api/v1/launches/predictions
GET /api/v1/markets

# Admin
GET /api/v1/admin/services
GET /api/v1/admin/config
GET /api/v1/admin/logs
```

## Docker Commands

```bash
# Start
docker-compose up -d

# Stop
docker-compose down

# Logs
docker-compose logs -f apollo-bot

# Restart
docker-compose restart apollo-bot

# Update
docker-compose pull
docker-compose up -d
```

## File Structure

```
TGbot/
├── public/                    # Frontend files
│   ├── index.html            # Landing page
│   ├── dashboard.html        # Dashboard
│   ├── prediction-market.html
│   ├── docs.html
│   └── static/
│       ├── css/              # Styles
│       └── js/               # Effects
├── src/modules/
│   ├── web_api.py            # REST API server
│   └── web_auth.py           # Authentication
├── docker-compose.yml        # Docker config
├── start_dashboard.sh        # Start script (Unix)
└── start_dashboard.bat       # Start script (Windows)
```

## Environment Variables

```env
# Required
TELEGRAM_BOT_TOKEN=your_token
SOLANA_PRIVATE_KEY=your_key
DATABASE_URL=postgresql://...

# Web Dashboard
WEB_DASHBOARD_ENABLED=true
WEB_DASHBOARD_PORT=8080
WEB_DASHBOARD_HOST=0.0.0.0

# Optional Security
DASHBOARD_API_KEY=your_secret_key
```

## Test Commands

```bash
# Health check
curl http://localhost:8080/health

# Get metrics
curl http://localhost:8080/api/v1/metrics | jq

# With auth
curl -H "X-API-Key: your-key" http://localhost:8080/api/v1/metrics
```

## Troubleshooting

```bash
# Check status
curl http://localhost:8080/health

# View logs
tail -f logs/bot.log

# Check port
netstat -an | grep 8080

# Verify files
ls -la public/

# Docker logs
docker logs apollo-bot
```

## Customization

```css
/* Colors - public/static/css/apollo-enhanced-style.css */
:root {
    --neon-cyan: #00f5ff;
    --neon-purple: #bd00ff;
    --neon-green: #00ff88;
}
```

## Production Nginx

```bash
# Copy config
sudo cp .claude/nginx.conf /etc/nginx/sites-available/apollo

# Enable
sudo ln -s /etc/nginx/sites-available/apollo /etc/nginx/sites-enabled/

# SSL
sudo certbot --nginx -d yourdomain.com

# Reload
sudo systemctl reload nginx
```

## Quick Tests

```bash
# 1. Start bot
python scripts/run_bot.py

# 2. Test in browser
http://localhost:8080/

# 3. Test Telegram
/start command in bot

# 4. Test API
curl http://localhost:8080/api/v1/metrics

# 5. Check health
curl http://localhost:8080/health
```

## Documentation Links

- **Complete Guide**: `WEB_DASHBOARD_README.md`
- **Deployment**: `DASHBOARD_DEPLOYMENT_GUIDE.md`
- **Integration**: `INTEGRATION_COMPLETE.md`
- **This Card**: `QUICK_REFERENCE.md`

---

**That's it! Start with `start_dashboard.bat` or `start_dashboard.sh`** 🚀

