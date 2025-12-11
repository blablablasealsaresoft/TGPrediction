# 🔌 APOLLO CyberSentinel API Documentation
## Enterprise Trading Platform REST API v2.0

**Base URL**: `https://api.apollo-sentinel.com/v1`  
**Protocol**: HTTPS only  
**Authentication**: Bearer Token  
**Rate Limit**: 1,000 requests/minute (authenticated)  
**Status Page**: https://status.apollo-sentinel.com

---

## 📋 Table of Contents

1. [Authentication](#authentication)
2. [Core Endpoints](#core-endpoints)
3. [Trading Operations](#trading-operations)
4. [Intelligence Queries](#intelligence-queries)
5. [Market Data](#market-data)
6. [User Management](#user-management)
7. [WebSocket Streaming](#websocket-streaming)
8. [Error Handling](#error-handling)
9. [Code Examples](#code-examples)

---

## 🔐 Authentication

### API Key Generation

```bash
# Via Telegram Bot
/api_key create

# Response
✅ API Key Created:
Key: apk_1a2b3c4d5e6f7g8h9i0j
Secret: sct_9z8y7x6w5v4u3t2s1r0q

⚠️ Store your secret securely. It won't be shown again.
```

### Authentication Header

```http
Authorization: Bearer YOUR_API_KEY
```

### Authentication Example

```javascript
const axios = require('axios');

const api = axios.create({
  baseURL: 'https://api.apollo-sentinel.com/v1',
  headers: {
    'Authorization': 'Bearer apk_1a2b3c4d5e6f7g8h9i0j',
    'Content-Type': 'application/json'
  }
});
```

---

## 🎯 Core Endpoints

### Health Check

Check system status and availability.

**Endpoint**: `GET /health`

**Request**:
```http
GET /v1/health HTTP/1.1
Host: api.apollo-sentinel.com
```

**Response**:
```json
{
  "status": "ok",
  "version": "2.0.0",
  "uptime": 86400,
  "services": {
    "trading_engine": "online",
    "ai_predictor": "online",
    "database": "online",
    "redis": "online"
  },
  "timestamp": "2025-11-11T08:17:22Z"
}
```

**Status Codes**:
- `200 OK` - All systems operational
- `503 Service Unavailable` - System degraded or starting up

---

### System Metrics

Get real-time system performance metrics.

**Endpoint**: `GET /metrics`

**Request**:
```http
GET /v1/metrics HTTP/1.1
Host: api.apollo-sentinel.com
Authorization: Bearer YOUR_API_KEY
```

**Response**:
```json
{
  "trading_pairs": 208,
  "elite_wallets": 441,
  "active_users": 1523,
  "predictions_today": 8745,
  "accuracy_rate": 78.5,
  "api_integrations": {
    "total": 26,
    "online": 26,
    "degraded": 0
  },
  "performance": {
    "avg_response_time_ms": 87,
    "prediction_time_ms": 1842,
    "trade_execution_ms": 643
  },
  "uptime_percent": 99.94
}
```

---

## 💹 Trading Operations

### Get Prediction

Request AI prediction for a specific token.

**Endpoint**: `POST /predict`

**Request**:
```http
POST /v1/predict HTTP/1.1
Host: api.apollo-sentinel.com
Authorization: Bearer YOUR_API_KEY
Content-Type: application/json

{
  "token_address": "So11111111111111111111111111111111111111112",
  "amount": 1.0,
  "timeframe": "6h"
}
```

**Response**:
```json
{
  "prediction_id": "pred_a1b2c3d4e5f6",
  "token": {
    "address": "So11111111111111111111111111111111111111112",
    "symbol": "SOL",
    "name": "Wrapped SOL"
  },
  "prediction": {
    "direction": "UP",
    "confidence": 87.3,
    "confidence_level": "ULTRA",
    "expected_move": "+75%",
    "timeframe": "6h",
    "recommendation": "BUY"
  },
  "intelligence": {
    "ai_score": 92,
    "sentiment_score": 94,
    "smart_money_score": 88,
    "community_rating": 8.5,
    "security_score": 96
  },
  "risk_management": {
    "recommended_amount": 2.5,
    "take_profit": "+75%",
    "stop_loss": "-8%",
    "risk_reward_ratio": 9.375
  },
  "reasoning": [
    "Strong bullish technical patterns detected",
    "12 elite wallets accumulating",
    "Social sentiment extremely positive (94%)",
    "Contract security verified (8/8 checks passed)"
  ],
  "timestamp": "2025-11-11T08:17:22Z"
}
```

**Parameters**:
- `token_address` (required): Solana token mint address
- `amount` (optional): Position size in SOL (default: 1.0)
- `timeframe` (optional): Prediction window: `1h`, `6h`, `24h`, `7d` (default: `6h`)

**Status Codes**:
- `200 OK` - Prediction generated successfully
- `400 Bad Request` - Invalid token address or parameters
- `429 Too Many Requests` - Rate limit exceeded
- `503 Service Unavailable` - AI engine temporarily unavailable

---

### Execute Trade

Execute a trade based on bot recommendation.

**Endpoint**: `POST /trade`

**Request**:
```http
POST /v1/trade HTTP/1.1
Host: api.apollo-sentinel.com
Authorization: Bearer YOUR_API_KEY
Content-Type: application/json

{
  "token_address": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
  "action": "BUY",
  "amount": 1.5,
  "slippage": 1.0,
  "mev_protection": true
}
```

**Response**:
```json
{
  "trade_id": "trade_x1y2z3a4b5c6",
  "status": "executed",
  "token": {
    "address": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
    "symbol": "USDC",
    "name": "USD Coin"
  },
  "action": "BUY",
  "amount_sol": 1.5,
  "tokens_received": 157.32,
  "execution": {
    "price": 1.0048,
    "slippage_actual": 0.48,
    "transaction_hash": "5xK8...n3Qm",
    "block": 187523491,
    "timestamp": "2025-11-11T08:17:25Z"
  },
  "fees": {
    "solana_network": 0.000005,
    "platform_fee": 0.075,
    "total_sol": 0.075005
  },
  "mev_protected": true
}
```

**Parameters**:
- `token_address` (required): Token to trade
- `action` (required): `BUY` or `SELL`
- `amount` (required): Amount in SOL (for buy) or tokens (for sell)
- `slippage` (optional): Max slippage percentage (default: 1.0%)
- `mev_protection` (optional): Enable Jito bundling (default: true)

**Status Codes**:
- `200 OK` - Trade executed successfully
- `400 Bad Request` - Invalid parameters
- `402 Payment Required` - Insufficient balance
- `403 Forbidden` - ALLOW_BROADCAST disabled (testnet only)
- `429 Too Many Requests` - Rate limit exceeded
- `500 Internal Server Error` - Trade execution failed

---

### Flash Loan Opportunities

Get current arbitrage opportunities.

**Endpoint**: `GET /flash/opportunities`

**Request**:
```http
GET /v1/flash/opportunities?min_profit=0.5 HTTP/1.1
Host: api.apollo-sentinel.com
Authorization: Bearer YOUR_API_KEY
```

**Response**:
```json
{
  "count": 3,
  "opportunities": [
    {
      "id": "arb_m1n2o3p4q5r6",
      "token": {
        "address": "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263",
        "symbol": "BONK",
        "name": "Bonk"
      },
      "price_difference": 5.2,
      "dex_from": {
        "name": "Raydium",
        "price": 0.00001234
      },
      "dex_to": {
        "name": "Orca",
        "price": 0.00001298
      },
      "potential_profit": {
        "percentage": 5.2,
        "sol": 2.6,
        "usd": 273.52
      },
      "recommended_amount": 50,
      "expires_in": 45,
      "confidence": "high",
      "detected_at": "2025-11-11T08:17:18Z"
    },
    {
      "id": "arb_s7t8u9v0w1x2",
      "token": {
        "address": "7GCihgDB8fe6KNjn2MYtkzZcRjQy3t9GHdC8uHYmW2hr",
        "symbol": "POPCAT",
        "name": "Popcat"
      },
      "price_difference": 3.8,
      "dex_from": {
        "name": "Orca",
        "price": 0.00089123
      },
      "dex_to": {
        "name": "Meteora",
        "price": 0.00092511
      },
      "potential_profit": {
        "percentage": 3.8,
        "sol": 1.9,
        "usd": 199.78
      },
      "recommended_amount": 50,
      "expires_in": 32,
      "confidence": "medium",
      "detected_at": "2025-11-11T08:17:20Z"
    }
  ],
  "scan_interval_seconds": 2,
  "last_scan": "2025-11-11T08:17:22Z"
}
```

**Query Parameters**:
- `min_profit` (optional): Minimum profit in % (default: 0.5)
- `max_amount` (optional): Maximum loan amount in SOL (default: 500)
- `dex` (optional): Filter by specific DEX: `raydium`, `orca`, `meteora`

---

### Launch Predictions

Get upcoming token launch predictions.

**Endpoint**: `GET /launches/upcoming`

**Request**:
```http
GET /v1/launches/upcoming?confidence=high HTTP/1.1
Host: api.apollo-sentinel.com
Authorization: Bearer YOUR_API_KEY
```

**Response**:
```json
{
  "count": 4,
  "launches": [
    {
      "prediction_id": "launch_y9z0a1b2c3d4",
      "token": {
        "symbol": "NEWCAT",
        "name": "New Cat Coin",
        "category": "meme"
      },
      "prediction": {
        "estimated_launch": "2025-11-11T14:30:00Z",
        "confidence": 91,
        "confidence_level": "ULTRA",
        "hours_until_launch": 4.5
      },
      "intelligence": {
        "team_score": 88,
        "social_velocity": 94,
        "whale_interest": 12,
        "community_size": 5420
      },
      "signals": [
        "Founder active on Twitter (verified account)",
        "LP commit detected 4.2 hours ago",
        "12 elite wallets showing early interest",
        "Community engagement spike (+340% in 24h)"
      ],
      "recommendation": "AUTO_SNIPE",
      "detected_at": "2025-11-11T06:45:32Z"
    },
    {
      "prediction_id": "launch_e5f6g7h8i9j0",
      "token": {
        "symbol": "SOLROCKET",
        "name": "Solana Rocket",
        "category": "utility"
      },
      "prediction": {
        "estimated_launch": "2025-11-11T16:00:00Z",
        "confidence": 85,
        "confidence_level": "HIGH",
        "hours_until_launch": 6.0
      },
      "intelligence": {
        "team_score": 92,
        "social_velocity": 78,
        "whale_interest": 8,
        "community_size": 3210
      },
      "signals": [
        "Team has successful prior projects",
        "Whitepaper published and audited",
        "Discord server active (2K+ members)",
        "Marketing campaign started"
      ],
      "recommendation": "MONITOR",
      "detected_at": "2025-11-11T07:12:18Z"
    }
  ],
  "monitoring_active": true,
  "check_interval_seconds": 10
}
```

**Query Parameters**:
- `confidence` (optional): Filter by confidence: `ultra`, `high`, `medium` (default: all)
- `hours` (optional): Time window in hours (default: 24)
- `category` (optional): Token category: `meme`, `utility`, `defi`, `nft`

---

## 🧠 Intelligence Queries

### Elite Wallet Rankings

Get top performing tracked wallets.

**Endpoint**: `GET /wallets/elite`

**Request**:
```http
GET /v1/wallets/elite?limit=10&sort=winrate HTTP/1.1
Host: api.apollo-sentinel.com
Authorization: Bearer YOUR_API_KEY
```

**Response**:
```json
{
  "count": 441,
  "showing": 10,
  "wallets": [
    {
      "id": 1928855074,
      "address": "2CBHb5hcFiYEBRqRRYM4dFnHhQzAqLGzFPBGXhQCJ3mB",
      "score": 97.8,
      "tier": "ELITE",
      "stats": {
        "win_rate": 84.5,
        "total_trades": 423,
        "total_pnl_sol": 1247.32,
        "total_pnl_usd": 131277.86,
        "avg_hold_time_hours": 8.3,
        "best_trade_pnl": "+3850%"
      },
      "performance": {
        "last_7d": "+18.2%",
        "last_30d": "+67.4%",
        "last_90d": "+142.8%"
      },
      "followers": 87,
      "recent_activity": {
        "last_trade": "2025-11-11T06:23:45Z",
        "tokens_held": 12,
        "active": true
      }
    }
  ]
}
```

**Query Parameters**:
- `limit` (optional): Results per page (default: 20, max: 100)
- `offset` (optional): Pagination offset (default: 0)
- `sort` (optional): Sort by `score`, `winrate`, `pnl`, `trades` (default: `score`)
- `tier` (optional): Filter by tier: `elite`, `platinum`, `gold`

---

### Token Sentiment Analysis

Get comprehensive sentiment analysis for a token.

**Endpoint**: `GET /sentiment/{token_address}`

**Request**:
```http
GET /v1/sentiment/So11111111111111111111111111111111111111112 HTTP/1.1
Host: api.apollo-sentinel.com
Authorization: Bearer YOUR_API_KEY
```

**Response**:
```json
{
  "token": {
    "address": "So11111111111111111111111111111111111111112",
    "symbol": "SOL",
    "name": "Wrapped SOL"
  },
  "overall_sentiment": {
    "score": 94,
    "label": "VERY_POSITIVE",
    "confidence": 89
  },
  "sources": {
    "twitter": {
      "score": 96,
      "mentions_24h": 8742,
      "trending": true,
      "top_influencers": 23
    },
    "reddit": {
      "score": 91,
      "posts_24h": 342,
      "upvote_ratio": 0.94,
      "subreddits": ["solana", "cryptocurrency", "cryptomoonshots"]
    },
    "discord": {
      "score": 93,
      "messages_24h": 1247,
      "active_users": 523,
      "sentiment": "positive"
    }
  },
  "keywords": [
    "bullish",
    "breakout",
    "accumulation",
    "fundamentals",
    "ecosystem"
  ],
  "red_flags": [],
  "momentum": "increasing",
  "updated_at": "2025-11-11T08:17:22Z"
}
```

---

## 📊 Market Data

### Token Information

Get detailed token information and statistics.

**Endpoint**: `GET /tokens/{token_address}`

**Request**:
```http
GET /v1/tokens/EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v HTTP/1.1
Host: api.apollo-sentinel.com
Authorization: Bearer YOUR_API_KEY
```

**Response**:
```json
{
  "address": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
  "symbol": "USDC",
  "name": "USD Coin",
  "decimals": 6,
  "supply": {
    "total": 1200000000,
    "circulating": 1150000000
  },
  "price": {
    "usd": 1.0002,
    "sol": 0.00952,
    "change_24h": 0.02
  },
  "volume": {
    "24h_usd": 142000000,
    "24h_sol": 1352381
  },
  "liquidity": {
    "total_usd": 89000000,
    "locked_percent": 85.2
  },
  "holders": {
    "total": 342567,
    "top_10_percent": 23.4
  },
  "security": {
    "verified": true,
    "audit_status": "passed",
    "honeypot_risk": false,
    "score": 98
  },
  "markets": [
    {
      "dex": "Raydium",
      "pair": "USDC-SOL",
      "liquidity_usd": 42000000,
      "volume_24h_usd": 87000000
    },
    {
      "dex": "Orca",
      "pair": "USDC-SOL",
      "liquidity_usd": 31000000,
      "volume_24h_usd": 55000000
    }
  ],
  "updated_at": "2025-11-11T08:17:22Z"
}
```

---

### Price History

Get historical price data (OHLCV).

**Endpoint**: `GET /tokens/{token_address}/price/history`

**Request**:
```http
GET /v1/tokens/So11111111111111111111111111111111111111112/price/history?interval=1h&limit=24 HTTP/1.1
Host: api.apollo-sentinel.com
Authorization: Bearer YOUR_API_KEY
```

**Response**:
```json
{
  "token": {
    "address": "So11111111111111111111111111111111111111112",
    "symbol": "SOL"
  },
  "interval": "1h",
  "data": [
    {
      "timestamp": "2025-11-11T08:00:00Z",
      "open": 104.25,
      "high": 105.87,
      "low": 103.98,
      "close": 105.32,
      "volume_usd": 42350000,
      "volume_sol": 402341
    },
    {
      "timestamp": "2025-11-11T07:00:00Z",
      "open": 103.89,
      "high": 104.52,
      "low": 103.15,
      "close": 104.25,
      "volume_usd": 38920000,
      "volume_sol": 374182
    }
  ]
}
```

**Query Parameters**:
- `interval` (required): `1m`, `5m`, `15m`, `1h`, `4h`, `1d`, `1w`
- `limit` (optional): Number of candles (default: 100, max: 1000)
- `from` (optional): Start timestamp (ISO 8601)
- `to` (optional): End timestamp (ISO 8601)

---

## 👤 User Management

### Get User Profile

Retrieve user account information and statistics.

**Endpoint**: `GET /user/profile`

**Request**:
```http
GET /v1/user/profile HTTP/1.1
Host: api.apollo-sentinel.com
Authorization: Bearer YOUR_API_KEY
```

**Response**:
```json
{
  "user_id": "user_k1l2m3n4o5p6",
  "telegram_id": 8059844643,
  "tier": "GOLD",
  "created_at": "2025-01-15T10:30:00Z",
  "wallet": {
    "address": "9xQeWvG816bUx9EPjHmaT23yvVM2ZWbrrpZb9PusVFin",
    "balance_sol": 12.458,
    "balance_usd": 1310.82
  },
  "trading_stats": {
    "total_trades": 87,
    "win_rate": 76.4,
    "total_pnl_sol": 8.342,
    "total_pnl_usd": 877.31,
    "best_trade": "+285%",
    "worst_trade": "-12%"
  },
  "ai_stats": {
    "predictions_made": 134,
    "accuracy_rate": 78.4,
    "ultra_predictions": 23,
    "high_predictions": 56
  },
  "features": {
    "auto_predictions": true,
    "flash_loans": true,
    "launch_monitor": true,
    "copy_trading": true
  },
  "limits": {
    "daily_trades": 25,
    "flash_loan_max": 50,
    "api_calls_per_minute": 1000
  }
}
```

---

### Get Trade History

Retrieve user's trading history.

**Endpoint**: `GET /user/trades`

**Request**:
```http
GET /v1/user/trades?limit=10&status=completed HTTP/1.1
Host: api.apollo-sentinel.com
Authorization: Bearer YOUR_API_KEY
```

**Response**:
```json
{
  "count": 87,
  "showing": 10,
  "trades": [
    {
      "trade_id": "trade_q1r2s3t4u5v6",
      "type": "BUY",
      "token": {
        "address": "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263",
        "symbol": "BONK",
        "name": "Bonk"
      },
      "amount_sol": 2.5,
      "tokens_received": 125000000,
      "entry_price": 0.00000002,
      "exit_price": 0.00000057,
      "pnl_percent": 285.0,
      "pnl_sol": 7.125,
      "pnl_usd": 749.62,
      "status": "completed",
      "opened_at": "2025-11-08T14:23:15Z",
      "closed_at": "2025-11-09T09:12:48Z",
      "hold_time_hours": 18.8,
      "transaction_hashes": {
        "entry": "5xK8...n3Qm",
        "exit": "7yM9...p5Rn"
      }
    }
  ]
}
```

**Query Parameters**:
- `limit` (optional): Results per page (default: 20, max: 100)
- `offset` (optional): Pagination offset (default: 0)
- `status` (optional): Filter by `open`, `completed`, `failed`
- `from` (optional): Start date (ISO 8601)
- `to` (optional): End date (ISO 8601)

---

## 🔌 WebSocket Streaming

### Connect to WebSocket

Real-time data streaming for live updates.

**Endpoint**: `wss://api.apollo-sentinel.com/v1/ws`

**Authentication**:
```javascript
const ws = new WebSocket('wss://api.apollo-sentinel.com/v1/ws');

ws.onopen = () => {
  ws.send(JSON.stringify({
    type: 'auth',
    token: 'YOUR_API_KEY'
  }));
};
```

### Subscribe to Channels

```javascript
// Subscribe to price updates
ws.send(JSON.stringify({
  type: 'subscribe',
  channel: 'price',
  token: 'So11111111111111111111111111111111111111112'
}));

// Subscribe to new predictions
ws.send(JSON.stringify({
  type: 'subscribe',
  channel: 'predictions'
}));

// Subscribe to flash opportunities
ws.send(JSON.stringify({
  type: 'subscribe',
  channel: 'flash_opportunities'
}));

// Subscribe to launch alerts
ws.send(JSON.stringify({
  type: 'subscribe',
  channel: 'launches',
  confidence: 'ultra'
}));
```

### Message Format

**Price Update**:
```json
{
  "channel": "price",
  "token": "So11111111111111111111111111111111111111112",
  "symbol": "SOL",
  "price_usd": 105.32,
  "change_24h": 2.45,
  "timestamp": "2025-11-11T08:17:22Z"
}
```

**New Prediction**:
```json
{
  "channel": "predictions",
  "prediction_id": "pred_w1x2y3z4a5b6",
  "token": "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263",
  "direction": "UP",
  "confidence": 91,
  "confidence_level": "ULTRA",
  "expected_move": "+120%",
  "timestamp": "2025-11-11T08:17:22Z"
}
```

**Flash Opportunity**:
```json
{
  "channel": "flash_opportunities",
  "opportunity_id": "arb_c5d6e7f8g9h0",
  "token": "7GCihgDB8fe6KNjn2MYtkzZcRjQy3t9GHdC8uHYmW2hr",
  "price_diff": 5.2,
  "potential_profit_sol": 2.6,
  "dex_from": "Raydium",
  "dex_to": "Orca",
  "expires_in": 45,
  "timestamp": "2025-11-11T08:17:22Z"
}
```

**Launch Alert**:
```json
{
  "channel": "launches",
  "prediction_id": "launch_i9j0k1l2m3n4",
  "token": "NEWCAT",
  "confidence": 94,
  "estimated_launch": "2025-11-11T14:30:00Z",
  "hours_until": 4.2,
  "recommendation": "AUTO_SNIPE",
  "timestamp": "2025-11-11T10:18:00Z"
}
```

---

## ⚠️ Error Handling

### Error Response Format

```json
{
  "error": {
    "code": "INVALID_TOKEN_ADDRESS",
    "message": "The provided token address is invalid or does not exist",
    "details": {
      "token_address": "InvalidAddress123",
      "validation_error": "Invalid base58 encoding"
    },
    "timestamp": "2025-11-11T08:17:22Z",
    "request_id": "req_o5p6q7r8s9t0"
  }
}
```

### Common Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `INVALID_TOKEN` | 401 | Invalid or expired API token |
| `RATE_LIMIT_EXCEEDED` | 429 | Too many requests |
| `INVALID_TOKEN_ADDRESS` | 400 | Invalid Solana token address |
| `INSUFFICIENT_BALANCE` | 402 | Not enough SOL for operation |
| `SERVICE_UNAVAILABLE` | 503 | Service temporarily down |
| `PREDICTION_FAILED` | 500 | AI prediction generation failed |
| `TRADE_EXECUTION_FAILED` | 500 | Trade could not be executed |
| `NOT_FOUND` | 404 | Resource not found |

### Retry Logic

For `429` (rate limit) and `503` (service unavailable) errors:

```javascript
async function retryRequest(fn, maxRetries = 3) {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await fn();
    } catch (error) {
      if (error.response?.status === 429) {
        const retryAfter = error.response.headers['retry-after'] || Math.pow(2, i);
        await new Promise(resolve => setTimeout(resolve, retryAfter * 1000));
      } else if (error.response?.status === 503 && i < maxRetries - 1) {
        await new Promise(resolve => setTimeout(resolve, 5000));
      } else {
        throw error;
      }
    }
  }
}
```

---

## 💻 Code Examples

### Node.js Example

```javascript
const axios = require('axios');

class ApolloClient {
  constructor(apiKey) {
    this.api = axios.create({
      baseURL: 'https://api.apollo-sentinel.com/v1',
      headers: {
        'Authorization': `Bearer ${apiKey}`,
        'Content-Type': 'application/json'
      }
    });
  }

  async getPrediction(tokenAddress, amount = 1.0) {
    const response = await this.api.post('/predict', {
      token_address: tokenAddress,
      amount: amount,
      timeframe: '6h'
    });
    return response.data;
  }

  async getFlashOpportunities(minProfit = 0.5) {
    const response = await this.api.get('/flash/opportunities', {
      params: { min_profit: minProfit }
    });
    return response.data;
  }

  async getEliteWallets(limit = 10) {
    const response = await this.api.get('/wallets/elite', {
      params: { limit, sort: 'winrate' }
    });
    return response.data;
  }
}

// Usage
const client = new ApolloClient('YOUR_API_KEY');

// Get prediction
const prediction = await client.getPrediction('So11111111111111111111111111111111111111112');
console.log(`Direction: ${prediction.prediction.direction}`);
console.log(`Confidence: ${prediction.prediction.confidence}%`);

// Get flash opportunities
const opportunities = await client.getFlashOpportunities(1.0);
console.log(`Found ${opportunities.count} opportunities`);

// Get elite wallets
const wallets = await client.getEliteWallets(20);
console.log(`Top wallet win rate: ${wallets.wallets[0].stats.win_rate}%`);
```

### Python Example

```python
import requests

class ApolloClient:
    def __init__(self, api_key):
        self.base_url = 'https://api.apollo-sentinel.com/v1'
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
    
    def get_prediction(self, token_address, amount=1.0):
        response = requests.post(
            f'{self.base_url}/predict',
            headers=self.headers,
            json={
                'token_address': token_address,
                'amount': amount,
                'timeframe': '6h'
            }
        )
        return response.json()
    
    def get_flash_opportunities(self, min_profit=0.5):
        response = requests.get(
            f'{self.base_url}/flash/opportunities',
            headers=self.headers,
            params={'min_profit': min_profit}
        )
        return response.json()
    
    def get_elite_wallets(self, limit=10):
        response = requests.get(
            f'{self.base_url}/wallets/elite',
            headers=self.headers,
            params={'limit': limit, 'sort': 'winrate'}
        )
        return response.json()

# Usage
client = ApolloClient('YOUR_API_KEY')

# Get prediction
prediction = client.get_prediction('So11111111111111111111111111111111111111112')
print(f"Direction: {prediction['prediction']['direction']}")
print(f"Confidence: {prediction['prediction']['confidence']}%")

# Get flash opportunities
opportunities = client.get_flash_opportunities(1.0)
print(f"Found {opportunities['count']} opportunities")

# Get elite wallets
wallets = client.get_elite_wallets(20)
print(f"Top wallet win rate: {wallets['wallets'][0]['stats']['win_rate']}%")
```

---

## 📞 Support

**API Issues**: api-support@apollo-sentinel.com  
**Documentation**: https://docs.apollo-sentinel.com  
**Status Page**: https://status.apollo-sentinel.com  
**Rate Limit Increase**: enterprise@apollo-sentinel.com

---

**Version**: 2.0.0  
**Last Updated**: November 11, 2025  
**Changelog**: https://docs.apollo-sentinel.com/changelog
