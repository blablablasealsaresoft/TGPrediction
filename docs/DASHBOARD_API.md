# APOLLO CyberSentinel Dashboard API Documentation

## Overview

The Dashboard API provides REST endpoints and WebSocket connections for real-time monitoring and administration of the APOLLO trading bot.

**Base URL:** `http://localhost:8080/api/v1`  
**WebSocket URL:** `ws://localhost:8080/ws`

## Authentication

### API Key Authentication
For admin endpoints, include your API key in the header:
```
X-API-Key: your_admin_api_key
```

### JWT Authentication
For token-based authentication:
```
Authorization: Bearer your_jwt_token
```

## Health Check Endpoints

### GET /health
Check if the API is alive.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-11-12T08:00:00.000Z"
}
```

### GET /ready
Check if the API is ready to serve requests.

**Response:**
```json
{
  "status": "ready",
  "timestamp": "2025-11-12T08:00:00.000Z"
}
```

## Dashboard Endpoints

### GET /api/v1/metrics
Get bot performance metrics.

**Response:**
```json
{
  "totalTrades": 1247,
  "winRate": 78.5,
  "totalPnL": 342.7,
  "activeUsers": 156,
  "eliteWallets": 441,
  "predictionsToday": 89,
  "flashLoansExecuted": 23,
  "avgConfidence": 82.4
}
```

### GET /api/v1/performance
Get 7-day performance data for charts.

**Response:**
```json
[
  {
    "date": "Mon",
    "pnl": 2500,
    "trades": 45,
    "winRate": 72
  },
  ...
]
```

### GET /api/v1/trades/recent
Get recent trades.

**Query Parameters:**
- `limit` (optional): Number of trades to return (default: 20)

**Response:**
```json
[
  {
    "id": 123,
    "timestamp": "2025-11-12T07:30:00.000Z",
    "type": "buy",
    "token": "BONK",
    "amountSol": 1.5,
    "price": 0.00001234,
    "pnl": 0.15,
    "context": "prediction"
  },
  ...
]
```

### GET /api/v1/trades/top-tokens
Get top performing tokens.

**Response:**
```json
[
  {
    "symbol": "$BONK",
    "pnl": "+$4,250",
    "winRate": 85,
    "trades": 12
  },
  ...
]
```

### GET /api/v1/phases/status
Get 4-phase system status.

**Response:**
```json
{
  "predictions": "active",
  "flashLoans": "active",
  "launchPredictor": "active",
  "predictionMarkets": "active"
}
```

### GET /api/v1/phases/distribution
Get trade distribution by phase.

**Response:**
```json
[
  {
    "name": "Predictions",
    "value": 42
  },
  {
    "name": "Flash Loans",
    "value": 28
  },
  ...
]
```

### GET /api/v1/alerts
Get system alerts and notifications.

**Response:**
```json
[
  {
    "type": "success",
    "message": "Flash loan arbitrage executed: +$247 profit",
    "timestamp": "2025-11-12T08:00:00.000Z"
  },
  ...
]
```

## Admin Endpoints

**Note:** All admin endpoints require authentication via `X-API-Key` header.

### GET /api/v1/admin/services
Get status of all services.

**Response:**
```json
{
  "tradingBot": {
    "status": "healthy",
    "uptime": 99.97,
    "lastCheck": "2025-11-12T08:00:00.000Z"
  },
  "database": {
    "status": "healthy",
    "connections": 12,
    "responseTime": 45
  },
  ...
}
```

### POST /api/v1/admin/services/:service/restart
Restart a specific service.

**Parameters:**
- `service`: Service name (e.g., "tradingBot", "database")

**Response:**
```json
{
  "status": "success",
  "message": "Service tradingBot restart initiated",
  "service": "tradingBot"
}
```

### GET /api/v1/admin/config
Get current configuration.

**Response:**
```json
{
  "ALLOW_BROADCAST": false,
  "AUTO_TRADE_ENABLED": true,
  "FLASH_LOAN_ENABLED": true,
  "LAUNCH_MONITOR_ENABLED": true,
  "MIN_CONFIDENCE": 75,
  "MAX_DAILY_TRADES": 25,
  "DAILY_LIMIT_SOL": 10,
  "ELITE_WALLETS_COUNT": 441,
  "API_RATE_LIMIT": 100
}
```

### PUT /api/v1/admin/config
Update configuration.

**Request Body:**
```json
{
  "AUTO_TRADE_ENABLED": true,
  "MIN_CONFIDENCE": 80
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Configuration updated (restart required)",
  "config": {...}
}
```

### GET /api/v1/admin/logs
Get system logs.

**Response:**
```json
[
  {
    "timestamp": "2025-11-12T08:00:00.000Z",
    "level": "INFO",
    "message": "Trading bot initialized",
    "module": "Core"
  },
  ...
]
```

### GET /api/v1/admin/logs/export
Export logs as a file.

**Response:** File download

## Prediction Phase Endpoints

### GET /api/v1/predictions/stats
Get prediction accuracy statistics.

**Response:**
```json
{
  "totalPredictions": 1247,
  "avgConfidence": 82.4,
  "accuracy": 76.8
}
```

### GET /api/v1/predictions/recent
Get recent predictions.

**Query Parameters:**
- `limit` (optional): Number of predictions (default: 10)

**Response:**
```json
[
  {
    "id": "pred_123",
    "token": "BONK",
    "confidence": 87.5,
    "recommendation": "BUY",
    "timestamp": "2025-11-12T07:30:00.000Z",
    "status": "ANALYZED"
  },
  ...
]
```

## Flash Loan Phase Endpoints

### GET /api/v1/flash/stats
Get flash loan execution statistics.

**Response:**
```json
{
  "totalExecuted": 247,
  "totalProfit": 12.45,
  "avgProfit": 0.05
}
```

### GET /api/v1/flash/opportunities
Get current arbitrage opportunities.

**Response:**
```json
[
  {
    "tokenA": "BONK",
    "tokenB": "USDC",
    "dexA": "Raydium",
    "dexB": "Orca",
    "priceDiff": 0.52,
    "potentialProfit": 125.5
  },
  ...
]
```

## Launch Predictor Phase Endpoints

### GET /api/v1/launches/predictions
Get upcoming launch predictions.

**Response:**
```json
[
  {
    "token": "NEW_TOKEN",
    "confidence": 90,
    "estimatedLaunch": "2025-11-12T12:00:00.000Z",
    "socialSignals": 85,
    "eliteWalletInterest": 12
  },
  ...
]
```

### GET /api/v1/launches/stats
Get launch prediction accuracy.

**Response:**
```json
{
  "totalPredictions": 89,
  "accuracy": 82.5,
  "avgEarlyDetection": "2-6 hours"
}
```

## Prediction Markets Phase Endpoints

### GET /api/v1/markets
Get active prediction markets.

**Response:**
```json
[
  {
    "id": "market_123",
    "question": "Will $BONK pump 50%+ in 6 hours?",
    "deadline": "2025-11-12T14:00:00.000Z",
    "poolUp": 25.5,
    "poolDown": 15.3,
    "poolNeutral": 5.2
  },
  ...
]
```

### GET /api/v1/markets/:id
Get specific market details.

**Parameters:**
- `id`: Market ID

**Response:**
```json
{
  "id": "market_123",
  "question": "Will $BONK pump 50%+ in 6 hours?",
  "creator": "user_456",
  "deadline": "2025-11-12T14:00:00.000Z",
  "poolUp": 25.5,
  "poolDown": 15.3,
  "poolNeutral": 5.2,
  "resolved": false,
  "participants": 42
}
```

### GET /api/v1/markets/stats
Get market statistics.

**Response:**
```json
{
  "activeMarkets": 12,
  "totalVolume": 245.7,
  "participants": 156
}
```

## User & Wallet Endpoints

### GET /api/v1/users/stats
Get user statistics.

**Response:**
```json
{
  "totalUsers": 847,
  "activeUsers": 156
}
```

### GET /api/v1/wallets/elite
Get elite wallet tracking stats.

**Response:**
```json
{
  "totalTracked": 441,
  "averageWinRate": 68.5,
  "totalFollowers": 89
}
```

## WebSocket Events

Connect to `ws://localhost:8080/ws` for real-time updates.

### Connection
```javascript
const ws = new WebSocket('ws://localhost:8080/ws');

ws.onopen = () => {
  console.log('Connected to WebSocket');
};
```

### Events

#### metrics_update
Real-time metrics update (every 3 seconds).

```json
{
  "type": "metrics_update",
  "timestamp": "2025-11-12T08:00:00.000Z",
  "data": {
    "totalTrades": 1248,
    "winRate": 78.6,
    ...
  }
}
```

#### log_entry
New log entry.

```json
{
  "type": "log_entry",
  "timestamp": "2025-11-12T08:00:00.000Z",
  "level": "INFO",
  "message": "Trade executed successfully",
  "module": "Trading"
}
```

#### trade_notification
New trade executed.

```json
{
  "type": "trade_notification",
  "timestamp": "2025-11-12T08:00:00.000Z",
  "trade": {
    "id": 124,
    "type": "buy",
    "token": "BONK",
    "amount": 1.5,
    "price": 0.00001234
  }
}
```

## Error Responses

All endpoints may return error responses:

### 400 Bad Request
```json
{
  "error": "Invalid request parameters"
}
```

### 401 Unauthorized
```json
{
  "error": "Missing authorization header"
}
```

### 403 Forbidden
```json
{
  "error": "Admin privileges required"
}
```

### 404 Not Found
```json
{
  "error": "Resource not found"
}
```

### 429 Too Many Requests
```json
{
  "error": "Rate limit exceeded"
}
```

### 500 Internal Server Error
```json
{
  "error": "Internal server error",
  "detail": "Error message"
}
```

### 503 Service Unavailable
```json
{
  "status": "not ready",
  "error": "Service unavailable"
}
```

## Rate Limiting

- **API endpoints:** 100 requests/second
- **Dashboard endpoints:** 50 requests/second

Rate limits are applied per IP address.

## CORS

CORS is enabled for the following origins (configurable via `WEB_API_CORS_ORIGINS`):
- `http://localhost:3000`
- `http://localhost`

## Examples

### JavaScript/Fetch
```javascript
// Get metrics
const response = await fetch('http://localhost:8080/api/v1/metrics');
const metrics = await response.json();
console.log(metrics);

// Admin endpoint with API key
const response = await fetch('http://localhost:8080/api/v1/admin/services', {
  headers: {
    'X-API-Key': 'your_admin_api_key'
  }
});
const services = await response.json();
```

### cURL
```bash
# Get metrics
curl http://localhost:8080/api/v1/metrics

# Admin endpoint with API key
curl -H "X-API-Key: your_admin_api_key" \
     http://localhost:8080/api/v1/admin/services

# Update config
curl -X PUT \
     -H "X-API-Key: your_admin_api_key" \
     -H "Content-Type: application/json" \
     -d '{"AUTO_TRADE_ENABLED": true}' \
     http://localhost:8080/api/v1/admin/config
```

### Python
```python
import requests

# Get metrics
response = requests.get('http://localhost:8080/api/v1/metrics')
metrics = response.json()
print(metrics)

# Admin endpoint with API key
headers = {'X-API-Key': 'your_admin_api_key'}
response = requests.get('http://localhost:8080/api/v1/admin/services', headers=headers)
services = response.json()
```

## Support

For issues or questions:
- Check the logs: `docker-compose -f docker-compose.prod.yml logs -f trading-bot`
- Verify configuration: See `WEB_API_ENV_VARS.md`
- Test health: `curl http://localhost:8080/health`

