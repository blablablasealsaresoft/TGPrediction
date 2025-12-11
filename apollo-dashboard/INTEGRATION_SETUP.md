# APOLLO Dashboard - TGbot Integration Setup Guide

## Overview

This guide explains how to set up and use the APOLLO dashboard as the web frontend for your TGbot trading bot.

## Architecture

The integration consists of:
1. **Python Backend API** (aiohttp) - REST API + WebSocket server running on port 8080
2. **React Frontend** - Dashboard and Admin Panel served on port 3000  
3. **Nginx Reverse Proxy** - Routes requests on port 80 to backend/frontend
4. **PostgreSQL & Redis** - Shared data layer with the trading bot

## Quick Start (5 Minutes)

### 1. Configure Environment Variables

Add these to your `.env` file:

```bash
# Web API Configuration
WEB_API_ENABLED=true
WEB_API_HOST=0.0.0.0
WEB_API_PORT=8080
WEB_API_CORS_ORIGINS=http://localhost:3000,http://localhost
WEB_API_JWT_SECRET=your-jwt-secret-key-min-32-characters-long
WEB_API_ADMIN_API_KEY=your-admin-api-key-change-in-production
ADMIN_PASSWORD=your-admin-password
```

**Important:** Change the default values for production!

### 2. Deploy the Stack

Run the deployment script:

```bash
chmod +x deploy_dashboard.sh
./deploy_dashboard.sh
```

Or manually:

```bash
docker-compose -f docker-compose.prod.yml up -d
```

### 3. Access the Dashboard

- **Dashboard**: http://localhost
- **Admin Panel**: http://localhost/admin
- **API Health**: http://localhost:8080/health
- **API Docs**: See `docs/DASHBOARD_API.md`

## Detailed Setup

### Prerequisites

- Docker & Docker Compose installed
- TGbot already configured and running
- PostgreSQL database initialized
- At least 4GB RAM available

### Step-by-Step Installation

#### 1. Install Dependencies

The bot requires these Python packages:

```bash
pip install aiohttp aiohttp-cors python-jose passlib
```

Or add to your `requirements.txt`:

```txt
aiohttp>=3.9.0
aiohttp-cors>=0.7.0
python-jose>=3.3.0
passlib>=1.7.4
```

#### 2. Configure Frontend

Create `apollo-dashboard/frontend/.env`:

```bash
REACT_APP_API_URL=http://localhost:8080/api/v1
REACT_APP_WS_URL=ws://localhost:8080/ws
REACT_APP_API_KEY=your-admin-api-key
NODE_ENV=production
```

#### 3. Build Frontend (Optional - Docker Handles This)

If you want to build locally:

```bash
cd apollo-dashboard/frontend
npm install
npm run build
```

#### 4. Start Services

```bash
# Start all services
docker-compose -f docker-compose.prod.yml up -d

# Check status
docker-compose -f docker-compose.prod.yml ps

# View logs
docker-compose -f docker-compose.prod.yml logs -f
```

## Features

### Dashboard (`/`)

- **Real-time Metrics**: Total trades, win rate, P&L, active users
- **Performance Charts**: 7-day performance, real-time activity
- **Phase Status**: 4-phase system monitoring
- **Top Tokens**: Best performing trades
- **System Alerts**: Live notifications

### Admin Panel (`/admin`)

- **Service Management**: View and restart services
- **Configuration Editor**: Update bot settings
- **Live Logs**: Real-time log streaming
- **Quick Actions**: Backup, restart, emergency stop

## API Integration

The dashboard connects to your TGbot via:

### REST API Endpoints

See `docs/DASHBOARD_API.md` for complete documentation.

Key endpoints:
- `GET /api/v1/metrics` - Bot metrics
- `GET /api/v1/trades/recent` - Recent trades
- `GET /api/v1/admin/services` - Service status
- `PUT /api/v1/admin/config` - Update configuration

### WebSocket Connection

Real-time updates via WebSocket at `ws://localhost:8080/ws`:

```javascript
const ws = new WebSocket('ws://localhost:8080/ws');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Update:', data);
};
```

## Architecture Details

### Data Flow

```
User Browser
    ↓
Nginx (:80)
    ├─→ React Frontend (:3000) - Dashboard UI
    └─→ Python API (:8080) - REST + WebSocket
            ↓
      TGbot Modules
            ↓
    PostgreSQL + Redis
```

### Module Integration

The Web API integrates with these TGbot modules:

- **database.py** - Query trades, positions, users
- **monitoring.py** - Service health checks
- **ai_strategy_engine.py** - Prediction stats
- **flash_loan_engine.py** - Flash loan data
- **bundle_launch_predictor.py** - Launch predictions
- **prediction_markets.py** - Market data

## Troubleshooting

### Dashboard Not Loading

```bash
# Check if services are running
docker-compose -f docker-compose.prod.yml ps

# Check nginx logs
docker-compose -f docker-compose.prod.yml logs nginx-proxy

# Check frontend logs
docker-compose -f docker-compose.prod.yml logs apollo-dashboard
```

### API Not Responding

```bash
# Test API health
curl http://localhost:8080/health

# Check bot logs
docker-compose -f docker-compose.prod.yml logs trading-bot

# Verify Web API is enabled in .env
grep WEB_API_ENABLED .env
```

### WebSocket Disconnecting

Check nginx configuration supports WebSocket:

```bash
# Verify WebSocket proxy settings
docker exec nginx-proxy cat /etc/nginx/nginx.conf | grep -A 5 "location /ws"
```

### Database Connection Errors

```bash
# Check if PostgreSQL is running
docker-compose -f docker-compose.prod.yml ps postgres

# Test database connection
docker exec trading-bot-db psql -U trader -d trading_bot -c "SELECT 1"
```

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `WEB_API_ENABLED` | `true` | Enable/disable Web API |
| `WEB_API_HOST` | `0.0.0.0` | API bind address |
| `WEB_API_PORT` | `8080` | API port |
| `WEB_API_CORS_ORIGINS` | `localhost:3000,localhost` | Allowed CORS origins |
| `WEB_API_JWT_SECRET` | - | JWT signing secret |
| `WEB_API_ADMIN_API_KEY` | - | Admin API key |
| `ADMIN_PASSWORD` | - | Admin login password |

### Nginx Configuration

Edit `nginx/nginx.conf` to:
- Change ports
- Add SSL certificates
- Modify rate limiting
- Add custom routes

### Frontend Configuration

Edit `apollo-dashboard/frontend/.env` to:
- Change API URL
- Update WebSocket URL
- Set API key

## Security

### Production Checklist

- [ ] Change default passwords and API keys
- [ ] Enable HTTPS with SSL certificates
- [ ] Restrict admin panel access by IP
- [ ] Set secure JWT secret (32+ characters)
- [ ] Enable rate limiting
- [ ] Review CORS origins
- [ ] Enable firewall rules
- [ ] Regular security updates

### SSL Setup (Production)

1. Obtain SSL certificates (e.g., Let's Encrypt)
2. Place certificates in `nginx/ssl/`
3. Uncomment HTTPS server block in `nginx/nginx.conf`
4. Update frontend `.env` to use HTTPS URLs
5. Restart nginx: `docker-compose restart nginx-proxy`

## Performance

### Resource Usage

- **Bot + API**: ~2GB RAM, 2 CPU cores
- **Frontend**: ~256MB RAM
- **Nginx**: ~128MB RAM
- **PostgreSQL**: ~512MB RAM
- **Redis**: ~256MB RAM

**Total**: ~3-4GB RAM recommended

### Optimization

- Enable Redis caching for API responses
- Use Nginx caching for static assets
- Compress API responses with gzip
- Limit WebSocket broadcast frequency
- Add database indexes for queries

## Monitoring

### Health Checks

```bash
# API health
curl http://localhost:8080/health

# Services status
curl -H "X-API-Key: your_key" http://localhost:8080/api/v1/admin/services

# Database
docker exec trading-bot-db pg_isready
```

### Logs

```bash
# All services
docker-compose -f docker-compose.prod.yml logs -f

# Specific service
docker-compose -f docker-compose.prod.yml logs -f trading-bot
docker-compose -f docker-compose.prod.yml logs -f apollo-dashboard
docker-compose -f docker-compose.prod.yml logs -f nginx-proxy
```

### Metrics

The API provides metrics at:
- `/api/v1/metrics` - Bot performance
- `/api/v1/admin/services` - Service health
- `/health` - API health
- `/ready` - Readiness probe

## Backup & Recovery

### Database Backup

```bash
# Manual backup
docker exec trading-bot-db pg_dump -U trader trading_bot > backup.sql

# Restore
docker exec -i trading-bot-db psql -U trader trading_bot < backup.sql
```

### Configuration Backup

```bash
# Backup .env and configs
tar -czf config-backup.tar.gz .env apollo-dashboard/frontend/.env nginx/nginx.conf

# Restore
tar -xzf config-backup.tar.gz
```

## Updating

### Update Bot Code

```bash
# Pull latest changes
git pull

# Rebuild containers
docker-compose -f docker-compose.prod.yml build

# Restart services
docker-compose -f docker-compose.prod.yml up -d
```

### Update Dashboard

```bash
# Rebuild frontend
docker-compose -f docker-compose.prod.yml build apollo-dashboard

# Restart
docker-compose -f docker-compose.prod.yml restart apollo-dashboard
```

## Development

### Local Development

```bash
# Start backend (bot + API)
python -m src.bot.main

# Start frontend (separate terminal)
cd apollo-dashboard/frontend
npm start
```

Access at:
- Frontend: http://localhost:3000
- API: http://localhost:8080

### Making Changes

1. Edit source files
2. Test locally
3. Rebuild containers
4. Deploy to production

### Testing

See `tests/test_web_api.py` for API tests.

```bash
# Run tests
pytest tests/test_web_api.py -v
```

## Support

### Documentation

- **API Docs**: `docs/DASHBOARD_API.md`
- **Environment Variables**: `WEB_API_ENV_VARS.md`
- **Deployment**: `deploy_dashboard.sh`
- **TGbot Docs**: `README.md`, `docs/`

### Getting Help

1. Check logs for errors
2. Verify configuration
3. Test API health endpoints
4. Review this guide
5. Check GitHub issues

## License

Same as TGbot - see main README.md

## Credits

Built as an integrated dashboard for APOLLO CyberSentinel TGbot.

