# 🚀 APOLLO CyberSentinel - Dashboard Deployment Guide

## Overview

Your Telegram bot now has a beautiful web dashboard! This guide will help you deploy the complete system with both the Telegram bot and web interface working together.

## 🎯 What's Included

### Frontend Pages
1. **Landing Page** (`/`) - Main entry point with navigation
2. **Trading Dashboard** (`/dashboard`) - Real-time trading command center
3. **Prediction Market** (`/prediction-market`) - Strategy hub & community intelligence
4. **Documentation** (`/docs`) - Complete API & command reference

### API Endpoints
All your bot functionality is accessible via REST API at `/api/v1/`:
- `/api/v1/metrics` - Bot performance metrics
- `/api/v1/performance` - 7-day performance data
- `/api/v1/trades/recent` - Recent trades
- `/api/v1/trades/top-tokens` - Top performing tokens
- `/api/v1/phases/status` - 4-phase system status
- `/api/v1/predictions/*` - Prediction phase endpoints
- `/api/v1/flash/*` - Flash loan endpoints
- `/api/v1/launches/*` - Launch predictor endpoints
- `/api/v1/markets/*` - Prediction markets endpoints

## 🏃 Quick Start (Local Development)

### 1. Start the Bot with Web Dashboard

```bash
# The bot automatically starts the web API server on port 8080
python scripts/run_bot.py
```

### 2. Access the Dashboard

Open your browser and navigate to:
- **Landing Page**: http://localhost:8080/
- **Dashboard**: http://localhost:8080/dashboard
- **Prediction Market**: http://localhost:8080/prediction-market
- **Documentation**: http://localhost:8080/docs
- **API Docs**: http://localhost:8080/api/v1/metrics

### 3. Telegram Bot Works Simultaneously

Your Telegram bot continues to work exactly as before! All commands like `/start`, `/predict`, `/buy`, `/sell`, etc. work perfectly while the web dashboard provides a visual interface.

## 🐳 Docker Deployment

### Option 1: Using Docker Compose (Recommended)

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f apollo-bot

# Stop services
docker-compose down
```

### Option 2: Manual Docker Build

```bash
# Build the image
docker build -t apollo-cybersentinel .

# Run the container
docker run -d \
  --name apollo-bot \
  -p 8080:8080 \
  --env-file .env \
  apollo-cybersentinel
```

## 🌐 Production Deployment with Nginx

For production, use nginx as a reverse proxy:

### 1. Copy the nginx configuration

```bash
# The nginx.conf is already in .claude/nginx.conf
# Copy it to your nginx sites-available folder
sudo cp .claude/nginx.conf /etc/nginx/sites-available/apollo-dashboard

# Create symbolic link
sudo ln -s /etc/nginx/sites-available/apollo-dashboard /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Reload nginx
sudo systemctl reload nginx
```

### 2. Configure SSL (Let's Encrypt)

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d yourdomain.com

# Auto-renewal is configured automatically
```

### 3. Access Your Dashboard

- **Production URL**: https://yourdomain.com/
- **Dashboard**: https://yourdomain.com/dashboard
- **API**: https://yourdomain.com/api/v1/

## ⚙️ Configuration

### Environment Variables

Add these to your `.env` file:

```env
# Web Dashboard Settings
WEB_DASHBOARD_ENABLED=true
WEB_DASHBOARD_PORT=8080
WEB_DASHBOARD_HOST=0.0.0.0

# CORS Settings (for frontend)
CORS_ORIGINS=http://localhost:3000,http://localhost:8080,https://yourdomain.com
```

### Customization

#### Update Bot Username in Landing Page
Edit `public/index.html` line 329:
```html
<a href="https://t.me/YOUR_BOT_USERNAME" target="_blank" class="nav-button">
```

Replace `YOUR_BOT_USERNAME` with your actual bot username.

## 🔒 Security Considerations

### For Production Deployments:

1. **Enable Authentication** (Coming Soon)
   - The dashboard currently has no authentication
   - Recommended: Add API key authentication or OAuth

2. **Rate Limiting**
   - Nginx configuration includes rate limiting
   - API limit: 100 requests/second
   - Dashboard limit: 50 requests/second

3. **Firewall Rules**
   ```bash
   # Allow only necessary ports
   sudo ufw allow 80/tcp   # HTTP
   sudo ufw allow 443/tcp  # HTTPS
   sudo ufw enable
   ```

4. **Environment Secrets**
   - Never commit `.env` file
   - Use Docker secrets or AWS Secrets Manager in production

## 🎨 Customization Guide

### Branding

All colors and styles are defined in:
- `public/static/css/apollo-enhanced-style.css`

CSS variables you can customize:
```css
:root {
    --neon-cyan: #00f5ff;
    --neon-purple: #bd00ff;
    --neon-green: #00ff88;
    --neon-gold: #ffd700;
    --neon-pink: #ff006e;
    --bg-deep: #0a0014;
    --bg-dark: #150028;
}
```

### Effects

The visual effects are powered by:
- `public/static/js/apollo-enhanced-effects.js`

To disable effects, remove the script include from HTML files.

## 📊 Dashboard Features

### Real-Time Updates
- Metrics update every 10 seconds
- WebSocket support at `/ws` for live data streaming
- Performance charts with 7-day history

### Trading Dashboard Shows:
- ✅ Total P&L and win rate
- ✅ Recent trades
- ✅ Top performing tokens
- ✅ 4-phase system status
- ✅ Real-time alerts
- ✅ AI confidence levels

### Prediction Market Shows:
- ✅ Active prediction markets
- ✅ Strategy marketplace
- ✅ Community token ratings
- ✅ Elite wallet leaderboard
- ✅ User achievements

## 🐛 Troubleshooting

### Dashboard Not Loading

1. **Check if web server is running:**
   ```bash
   curl http://localhost:8080/health
   # Should return: {"status":"healthy"}
   ```

2. **Check logs:**
   ```bash
   # Docker
   docker logs apollo-bot

   # Direct run
   tail -f logs/bot.log
   ```

3. **Verify static files exist:**
   ```bash
   ls -la public/
   ls -la public/static/
   ```

### API Returning Empty Data

The API returns real data from your database. If you see empty metrics:
- Bot needs to make some trades first
- Check database connection in logs
- Verify DATABASE_URL in `.env`

### Cannot Connect from External Network

1. **Check firewall:**
   ```bash
   sudo ufw status
   ```

2. **Verify port binding:**
   ```bash
   netstat -tulpn | grep 8080
   ```

3. **Check Docker port mapping:**
   ```bash
   docker ps
   # Should show: 0.0.0.0:8080->8080/tcp
   ```

## 🚀 Performance Optimization

### For High Traffic:

1. **Enable Redis Caching:**
   ```env
   REDIS_URL=redis://localhost:6379
   CACHE_TTL=60  # seconds
   ```

2. **Use CDN for Static Files:**
   - Upload `/public/static/` to CloudFlare or AWS CloudFront
   - Update URLs in HTML files

3. **Scale with Load Balancer:**
   ```bash
   # Run multiple instances
   docker-compose up --scale apollo-bot=3
   ```

## 📚 Next Steps

1. **Customize the dashboard** to match your brand
2. **Add authentication** for sensitive endpoints
3. **Set up monitoring** with Prometheus/Grafana
4. **Configure alerts** for system health
5. **Add your Telegram bot link** to the landing page

## 💡 Tips

- **Test locally first** before deploying to production
- **Use environment variables** for all configuration
- **Monitor your logs** regularly
- **Keep dependencies updated** for security patches
- **Backup your database** regularly

## 🆘 Support

If you encounter issues:
1. Check the logs first
2. Verify all environment variables are set
3. Ensure ports are not blocked
4. Test with `curl` before browser

## 📖 API Documentation

Full API documentation is available at `/docs` in your deployed dashboard.

You can also access it programmatically:
```bash
curl http://localhost:8080/api/v1/metrics | jq
```

---

**Congratulations!** 🎉 Your Telegram bot now has a professional web dashboard while maintaining all its original functionality!

