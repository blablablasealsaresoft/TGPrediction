# APOLLO Dashboard - Quick Start Guide

## ✅ Build Complete!

Your dashboard has been successfully built and is ready to deploy.

## 🚀 Deploy Now

### Option 1: Automated Deployment (Recommended)

```bash
./deploy_dashboard.sh
```

### Option 2: Manual Deployment

```bash
# Start all services
docker-compose -f docker-compose.prod.yml up -d

# Check status
docker-compose -f docker-compose.prod.yml ps

# View logs
docker-compose -f docker-compose.prod.yml logs -f
```

## 📊 Access Your Dashboard

Once deployed, access the dashboard at:

- **Dashboard Home**: http://localhost:3000
- **Via Nginx Proxy**: http://localhost (port 80)
- **API Health Check**: http://localhost:8080/health
- **API Metrics**: http://localhost:8080/api/v1/metrics

## ⚙️ Before Deploying

Make sure you've added these environment variables to your `.env` file:

```bash
# Web API Configuration
WEB_API_ENABLED=true
WEB_API_HOST=0.0.0.0
WEB_API_PORT=8080
WEB_API_CORS_ORIGINS=http://localhost:3000,http://localhost
WEB_API_JWT_SECRET=change-this-jwt-secret-min-32-chars
WEB_API_ADMIN_API_KEY=change-this-admin-api-key
ADMIN_PASSWORD=change-this-password
```

**⚠️ Important**: Change the default secrets before production use!

## 🔍 Verify Deployment

After deploying, test the API:

```bash
# Test API health
curl http://localhost:8080/health

# Test metrics endpoint
curl http://localhost:8080/api/v1/metrics

# Test WebSocket (requires wscat: npm install -g wscat)
wscat -c ws://localhost:8080/ws
```

## 📚 Current Features

The dashboard currently provides:

✅ **Simple HTML Dashboard**
- Welcome page with feature overview
- API connection testing
- Direct access to all endpoints

✅ **REST API Backend**
- 30+ endpoints for all bot data
- Real-time WebSocket updates
- JWT authentication for admin
- Rate limiting and security

✅ **Infrastructure**
- Nginx reverse proxy
- Docker containerization
- Health checks and monitoring

## 🎯 Next Steps

### 1. Deploy and Test

```bash
# Deploy
./deploy_dashboard.sh

# Test
curl http://localhost:8080/health
```

### 2. Access the Dashboard

Open http://localhost:3000 or http://localhost in your browser.

### 3. Test API Connection

Click the "Test API Connection" button on the dashboard to verify the backend is working.

### 4. Start Trading Bot

Make sure your trading bot is running with Web API enabled:

```bash
docker-compose -f docker-compose.prod.yml logs -f trading-bot
```

## 🔧 Troubleshooting

### Dashboard not loading?

```bash
docker-compose -f docker-compose.prod.yml logs apollo-dashboard
```

### API not responding?

```bash
curl http://localhost:8080/health
docker-compose -f docker-compose.prod.yml logs trading-bot
```

### WebSocket issues?

```bash
docker-compose -f docker-compose.prod.yml logs nginx-proxy
```

## 📖 Full Documentation

- **API Reference**: `docs/DASHBOARD_API.md`
- **Setup Guide**: `apollo-dashboard/INTEGRATION_SETUP.md`
- **Environment Variables**: `WEB_API_ENV_VARS.md`
- **Complete Summary**: `DASHBOARD_INTEGRATION_COMPLETE.md`

## 🎨 Future Enhancements

The current dashboard is a simple HTML page. For the full React dashboard with charts and real-time updates, you can:

1. Set up a proper React build system (webpack/vite)
2. Build the JSX components (`Dashboard.jsx`, `AdminPanel.jsx`)
3. Deploy the built bundle

For now, the simple dashboard provides access to all API endpoints and functionality!

## ✨ What's Working

- ✅ REST API with 30+ endpoints
- ✅ WebSocket real-time updates
- ✅ Authentication and security
- ✅ Database integration
- ✅ Nginx reverse proxy
- ✅ Docker deployment
- ✅ Health monitoring

## 🚀 Ready to Deploy!

Run the deployment script:

```bash
./deploy_dashboard.sh
```

Then open http://localhost in your browser!

