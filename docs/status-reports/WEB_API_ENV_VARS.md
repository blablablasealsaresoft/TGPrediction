# Web API Environment Variables

Add these to your `.env` file to enable the Web API dashboard:

```bash
# ============================================================================
# 🌐 WEB API / DASHBOARD CONFIGURATION
# ============================================================================

# Enable Web API server
WEB_API_ENABLED=true

# Web API server host and port
WEB_API_HOST=0.0.0.0
WEB_API_PORT=8080

# CORS origins (comma-separated)
WEB_API_CORS_ORIGINS=http://localhost:3000,http://localhost,http://127.0.0.1:3000

# JWT secret for authentication (change in production)
WEB_API_JWT_SECRET=your-jwt-secret-key-min-32-characters-long-change-me

# Admin API key for admin endpoints (change in production)
WEB_API_ADMIN_API_KEY=your-admin-api-key-change-in-production

# Admin password for login (change in production)
ADMIN_PASSWORD=admin-password-change-me
```

## Installation Instructions

1. Copy the above variables to your `.env` file
2. Change the secret keys and passwords to secure values
3. Restart the bot: `docker-compose -f docker-compose.prod.yml restart trading-bot`
4. The Web API will start automatically on port 8080

## Frontend Configuration

The frontend environment variables are in `apollo-dashboard/frontend/.env`:

```bash
REACT_APP_API_URL=http://localhost:8080/api/v1
REACT_APP_WS_URL=ws://localhost:8080/ws
REACT_APP_API_KEY=your-admin-api-key-change-in-production
NODE_ENV=production
```

## Accessing the Dashboard

- **Dashboard**: http://localhost (via nginx) or http://localhost:3000 (direct)
- **Admin Panel**: http://localhost/admin
- **API Health**: http://localhost:8080/health
- **API Docs**: See docs/API.md

## Security Notes

- Always change default passwords and API keys in production
- Use HTTPS in production (configure nginx SSL)
- Restrict admin API access by IP if possible
- Enable JWT token expiration

