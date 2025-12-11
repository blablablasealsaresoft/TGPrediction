# 🚀 APOLLO CyberSentinel - API Documentation

**Version:** 4.5.0  
**Base URL:** `http://localhost:8080`  
**Protocol:** REST  
**Authentication:** API Key (Header-based)

---

## 📋 Table of Contents

1. [Authentication](#authentication)
2. [Health & Status Endpoints](#health--status-endpoints)
3. [Trading Endpoints](#trading-endpoints)
4. [Prediction Endpoints](#prediction-endpoints)
5. [Flash Loan Endpoints](#flash-loan-endpoints)
6. [Launch Predictor Endpoints](#launch-predictor-endpoints)
7. [Prediction Market Endpoints](#prediction-market-endpoints)
8. [Wallet Management](#wallet-management)
9. [Elite Wallet Tracking](#elite-wallet-tracking)
10. [Analytics & Statistics](#analytics--statistics)
11. [Security & Verification](#security--verification)
12. [WebSocket Streams](#websocket-streams)
13. [Rate Limits](#rate-limits)
14. [Error Codes](#error-codes)

---

## 🔐 Authentication

### API Key Authentication

All API requests require an API key passed in the header:

```http
Authorization: Bearer YOUR_API_KEY
```

**Obtaining an API Key:**
1. Start the bot via Telegram: `/start`
2. Generate API key: `/api_key`
3. Copy the key and use in your requests

**Security Best Practices:**
- Never commit API keys to version control
- Rotate keys every 90 days
- Use environment variables
- Implement rate limiting on client side

---

## 🏥 Health & Status Endpoints

### `GET /health`

Check basic service health (simple ping).

**Response:**
```json
{
  "status": "ok",
  "timestamp": "2025-11-11T17:30:00Z"
}
```

**Status Codes:**
- `200` - Service is healthy
- `503` - Service unavailable

---

### `GET /ready`

Detailed readiness check (includes dependencies).

**Response:**
```json
{
  "status": "ready",
  "timestamp": "2025-11-11T17:30:00Z",
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

**Status Codes:**
- `200` - All systems ready
- `503` - Some dependencies unavailable

---

### `GET /status`

Comprehensive system status including metrics.

**Response:**
```json
{
  "system": {
    "health": "operational",
    "uptime_seconds": 2847291,
    "uptime_percentage": "99.97%",
    "version": "4.5.0",
    "environment": "production"
  },
  "metrics": {
    "total_trades": 1247,
    "active_users": 156,
    "tokens_monitored": 208,
    "elite_wallets": 441,
    "win_rate": 78.5,
    "total_pnl_sol": 342.7,
    "security_alerts_24h": 3
  },
  "performance": {
    "avg_response_time_ms": 870,
    "requests_per_second": 45,
    "cpu_usage_percent": 23,
    "memory_usage_gb": 2.1,
    "disk_usage_gb": 15.3
  }
}
```

---

## 💰 Trading Endpoints

### `POST /api/trade/buy`

Execute a buy order for a token.

**Request:**
```json
{
  "token_address": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
  "amount_sol": 1.5,
  "slippage": 1.0,
  "confirm_risk": true
}
```

**Response:**
```json
{
  "success": true,
  "transaction_id": "5KJh7...xyz",
  "token_address": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
  "tokens_received": 15000,
  "sol_spent": 1.48,
  "price_per_token": 0.0000987,
  "timestamp": "2025-11-11T17:30:00Z"
}
```

**Parameters:**
- `token_address` (required): Solana token address
- `amount_sol` (required): Amount in SOL (0.1 - 100)
- `slippage` (optional): Max slippage % (default: 1.0)
- `confirm_risk` (required): Must be `true` to confirm

**Validation:**
- Minimum: 0.1 SOL
- Maximum: Based on tier (Bronze: 10 SOL, Gold: 50 SOL, Elite: 500 SOL)
- Token must pass 6-layer security check
- Sufficient wallet balance required

---

### `POST /api/trade/sell`

Execute a sell order for a token.

**Request:**
```json
{
  "token_address": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
  "amount_tokens": 15000,
  "slippage": 1.0
}
```

**Response:**
```json
{
  "success": true,
  "transaction_id": "8Mnh2...abc",
  "token_address": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
  "tokens_sold": 15000,
  "sol_received": 1.52,
  "price_per_token": 0.0001013,
  "profit_loss_sol": 0.04,
  "profit_loss_percent": 2.7,
  "timestamp": "2025-11-11T17:35:00Z"
}
```

---

### `GET /api/trade/positions`

Get all open positions for the user.

**Response:**
```json
{
  "positions": [
    {
      "token_address": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
      "token_name": "USDC",
      "quantity": 15000,
      "entry_price": 0.0000987,
      "current_price": 0.0001013,
      "entry_value_sol": 1.48,
      "current_value_sol": 1.52,
      "unrealized_pnl_sol": 0.04,
      "unrealized_pnl_percent": 2.7,
      "entry_time": "2025-11-11T17:30:00Z",
      "hold_duration_hours": 0.08
    }
  ],
  "total_value_sol": 1.52,
  "total_pnl_sol": 0.04,
  "total_pnl_percent": 2.7
}
```

---

## 🔮 Prediction Endpoints

### `POST /api/predict`

Get AI prediction for a token (Phase 1 feature).

**Request:**
```json
{
  "token_address": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
}
```

**Response:**
```json
{
  "prediction": {
    "direction": "UP",
    "confidence": 87,
    "confidence_level": "ULTRA",
    "expected_move": "+75%",
    "timeframe_hours": 6,
    "recommended_action": "BUY",
    "position_size_sol": 2.5,
    "take_profit_percent": 75,
    "stop_loss_percent": 8
  },
  "intelligence": {
    "ai_score": 92,
    "sentiment_score": 94,
    "smart_money_score": 88,
    "community_rating": 8.5,
    "security_score": 95
  },
  "reasoning": {
    "ai_analysis": "Contract analysis shows no honeypot indicators. Ownership renounced.",
    "sentiment": "Twitter mentions up 340% in last 2 hours. Positive sentiment 94%.",
    "smart_money": "12 elite wallets actively accumulating.",
    "community": "457 positive reviews. 8.5/10 community rating."
  },
  "learning_status": {
    "model_trained": true,
    "trades_analyzed": 1247,
    "current_accuracy": 78.5,
    "last_retrain": "2025-11-11T12:00:00Z"
  }
}
```

**Confidence Levels:**
- `ULTRA` (90-100%): Auto-execute recommended
- `HIGH` (80-89%): Strong signal
- `MEDIUM` (65-79%): Moderate signal
- `LOW` (<65%): Weak signal, avoid

---

### `POST /api/predict/enable-auto`

Enable auto-predictions (AI trades automatically on ULTRA signals).

**Request:**
```json
{
  "min_confidence": 90,
  "max_daily_trades": 25,
  "max_daily_amount_sol": 10,
  "enabled": true
}
```

**Response:**
```json
{
  "success": true,
  "auto_predictions_enabled": true,
  "settings": {
    "min_confidence": 90,
    "max_daily_trades": 25,
    "max_daily_amount_sol": 10,
    "current_trades_today": 3,
    "amount_used_today_sol": 4.2
  }
}
```

**Requirements:**
- Minimum balance: 0.5 SOL
- Tier: Gold or higher
- Risk acknowledgment required

---

### `GET /api/predict/stats`

Get prediction performance statistics.

**Response:**
```json
{
  "total_predictions": 1247,
  "wins": 979,
  "losses": 268,
  "win_rate": 78.5,
  "average_confidence": 82.3,
  "average_return_percent": 24.7,
  "best_trade_percent": 245.8,
  "worst_trade_percent": -12.3,
  "predictions_by_confidence": {
    "ultra": { "count": 342, "win_rate": 87.4 },
    "high": { "count": 489, "win_rate": 78.9 },
    "medium": { "count": 316, "win_rate": 68.2 },
    "low": { "count": 100, "win_rate": 52.0 }
  }
}
```

---

## ⚡ Flash Loan Endpoints

### `GET /api/flash/opportunities`

Get current flash loan arbitrage opportunities (Phase 2 feature).

**Response:**
```json
{
  "opportunities": [
    {
      "token_address": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
      "token_name": "USDC",
      "price_dex_a": 1.000,
      "price_dex_b": 1.005,
      "price_difference_percent": 0.5,
      "dex_a": "Raydium",
      "dex_b": "Orca",
      "liquidity_dex_a_sol": 15000,
      "liquidity_dex_b_sol": 12000,
      "max_borrow_sol": 50,
      "estimated_profit_sol": 0.25,
      "estimated_profit_percent": 0.5,
      "gas_fee_sol": 0.0001,
      "marginfi_fee_sol": 0.00005,
      "detected_at": "2025-11-11T17:30:00Z",
      "expires_in_seconds": 15
    }
  ],
  "scan_interval_seconds": 2,
  "last_scan": "2025-11-11T17:30:02Z"
}
```

---

### `POST /api/flash/execute`

Execute a flash loan arbitrage (Gold tier+).

**Request:**
```json
{
  "opportunity_id": "opp_12345",
  "borrow_amount_sol": 50
}
```

**Response:**
```json
{
  "success": true,
  "transaction_id": "3Kpq9...def",
  "borrowed_sol": 50,
  "profit_sol": 0.24,
  "profit_percent": 0.48,
  "platform_fee_sol": 0.012,
  "net_profit_sol": 0.228,
  "execution_time_ms": 387,
  "dex_from": "Raydium",
  "dex_to": "Orca",
  "timestamp": "2025-11-11T17:30:05Z"
}
```

**Tier Limits:**
- **Gold**: Up to 50 SOL, 5% platform fee
- **Platinum**: Up to 150 SOL, 3% platform fee
- **Elite**: Up to 500 SOL, 2% platform fee

---

### `POST /api/flash/enable`

Enable automatic flash loan execution.

**Request:**
```json
{
  "min_profit_percent": 0.3,
  "max_borrow_sol": 50,
  "enabled": true
}
```

**Response:**
```json
{
  "success": true,
  "flash_loans_enabled": true,
  "settings": {
    "min_profit_percent": 0.3,
    "max_borrow_sol": 50,
    "tier": "Gold",
    "platform_fee_percent": 5
  }
}
```

---

## 🎯 Launch Predictor Endpoints

### `GET /api/launch/predictions`

Get upcoming token launch predictions (Phase 3 feature).

**Response:**
```json
{
  "predictions": [
    {
      "token_address": "TBD",
      "predicted_launch_time": "2025-11-11T21:30:00Z",
      "hours_until_launch": 4,
      "confidence": 92,
      "confidence_level": "ULTRA",
      "signals": {
        "twitter_mentions": 47,
        "elite_wallet_interest": 12,
        "discord_activity": "high",
        "lp_commitment_detected": true,
        "team_verified": true,
        "team_history_score": 88
      },
      "expected_movement": {
        "initial_pump_percent": 150,
        "6h_target_percent": 300,
        "risk_level": "medium"
      },
      "auto_snipe_recommended": true
    }
  ],
  "monitoring_active": true,
  "sources": ["Twitter", "Reddit", "Discord", "441 Elite Wallets"],
  "detection_window_hours": "2-6"
}
```

---

### `POST /api/launch/monitor`

Enable/disable launch monitoring.

**Request:**
```json
{
  "enabled": true,
  "auto_snipe_ultra": true,
  "max_snipe_amount_sol": 0.5
}
```

**Response:**
```json
{
  "success": true,
  "monitoring_enabled": true,
  "auto_snipe_enabled": true,
  "settings": {
    "min_confidence_for_alert": 65,
    "min_confidence_for_auto_snipe": 90,
    "max_snipe_amount_sol": 0.5,
    "max_snipes_per_day": 10
  }
}
```

---

### `GET /api/launch/stats`

Get launch prediction performance.

**Response:**
```json
{
  "total_predictions": 89,
  "successful_predictions": 67,
  "accuracy": 75.3,
  "average_advance_notice_hours": 4.2,
  "best_performance": {
    "token_name": "MEMECOIN",
    "predicted_hours_early": 6,
    "actual_pump_percent": 487,
    "prediction_accuracy": "EXACT"
  }
}
```

---

## 🎲 Prediction Market Endpoints

### `GET /api/markets`

Browse active prediction markets (Phase 4 feature).

**Response:**
```json
{
  "markets": [
    {
      "market_id": "mkt_12345",
      "question": "Will BONK pump 50%+ in the next 6 hours?",
      "creator": "user_8059844643",
      "created_at": "2025-11-11T12:00:00Z",
      "deadline": "2025-11-11T18:00:00Z",
      "hours_until_resolution": 0.5,
      "status": "active",
      "pools": {
        "up": { "amount_sol": 15.7, "stakes": 23, "odds": 1.76 },
        "down": { "amount_sol": 8.3, "stakes": 12, "odds": 2.68 },
        "neutral": { "amount_sol": 0, "stakes": 0, "odds": 0 }
      },
      "total_pool_sol": 24.0,
      "platform_fee_percent": 3,
      "creator_bonus_percent": 1
    }
  ],
  "total_active_markets": 12,
  "total_pool_sol": 234.5
}
```

---

### `POST /api/markets/create`

Create a new prediction market (Elite tier only).

**Request:**
```json
{
  "question": "Will JUP reach $2.00 in the next 12 hours?",
  "token_address": "JUPyiwrYJFskUPiHa7hkeR8VUtAeFoSYbKedZNsDvCN",
  "deadline_hours": 12,
  "initial_stake_sol": 1.0,
  "initial_outcome": "UP"
}
```

**Response:**
```json
{
  "success": true,
  "market_id": "mkt_67890",
  "question": "Will JUP reach $2.00 in the next 12 hours?",
  "deadline": "2025-11-12T05:30:00Z",
  "initial_odds": {
    "up": 2.0,
    "down": 2.0,
    "neutral": 0
  },
  "creator_bonus": "1% of all stakes"
}
```

**Requirements:**
- Tier: Elite only
- Minimum stake: 0.5 SOL
- Maximum duration: 48 hours
- Question must be verifiable

---

### `POST /api/markets/stake`

Place a stake on a prediction market.

**Request:**
```json
{
  "market_id": "mkt_12345",
  "outcome": "UP",
  "amount_sol": 2.0
}
```

**Response:**
```json
{
  "success": true,
  "stake_id": "stk_abc123",
  "market_id": "mkt_12345",
  "outcome": "UP",
  "amount_staked_sol": 2.0,
  "current_odds": 1.65,
  "potential_payout_sol": 3.30,
  "potential_profit_sol": 1.30,
  "platform_fee_sol": 0.06,
  "staked_at": "2025-11-11T17:30:00Z"
}
```

---

### `GET /api/markets/my-stakes`

Get user's active stakes.

**Response:**
```json
{
  "active_stakes": [
    {
      "stake_id": "stk_abc123",
      "market_id": "mkt_12345",
      "question": "Will BONK pump 50%+ in the next 6 hours?",
      "outcome": "UP",
      "amount_staked_sol": 2.0,
      "odds_at_stake": 1.76,
      "current_odds": 1.65,
      "potential_payout_sol": 3.52,
      "deadline": "2025-11-11T18:00:00Z",
      "status": "pending"
    }
  ],
  "total_staked_sol": 7.5,
  "potential_winnings_sol": 15.2
}
```

---

### `GET /api/markets/leaderboard`

Get top predictors leaderboard.

**Response:**
```json
{
  "leaderboard": [
    {
      "rank": 1,
      "user_id": "user_8059844643",
      "username": "CryptoKing",
      "total_predictions": 234,
      "wins": 189,
      "win_rate": 80.8,
      "total_profit_sol": 45.7,
      "roi_percent": 312.5,
      "tier": "Elite"
    }
  ],
  "your_rank": 47,
  "total_participants": 156
}
```

---

## 👛 Wallet Management

### `GET /api/wallet/balance`

Get wallet balance and holdings.

**Response:**
```json
{
  "wallet_address": "7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU",
  "sol_balance": 12.456,
  "tokens": [
    {
      "address": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
      "name": "USDC",
      "symbol": "USDC",
      "balance": 15000,
      "value_sol": 15.0,
      "decimals": 6
    }
  ],
  "total_value_sol": 27.456,
  "total_value_usd": 5491.20
}
```

---

### `POST /api/wallet/export`

Export private key (requires additional verification).

**Request:**
```json
{
  "telegram_verification_code": "123456"
}
```

**Response:**
```json
{
  "wallet_address": "7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU",
  "private_key": "ENCRYPTED_PRIVATE_KEY_HERE",
  "warning": "⚠️ NEVER share your private key. Store securely offline."
}
```

---

## 👑 Elite Wallet Tracking

### `GET /api/elite-wallets/leaderboard`

Get elite wallet leaderboard (441 pre-loaded wallets).

**Response:**
```json
{
  "elite_wallets": [
    {
      "rank": 1,
      "wallet_address": "2CBHb5hcFiYEBRqRRYM4dFnHhQzAqLGzFPBGXhQCJ3mB",
      "score": 98,
      "tier": "Elite",
      "win_rate": 87.5,
      "total_trades": 1423,
      "total_pnl_sol": 2847.3,
      "roi_percent": 1243.7,
      "followers": 89,
      "recent_activity": "2m ago"
    }
  ],
  "total_wallets": 441,
  "scoring_algorithm": "100-point system",
  "update_frequency": "Every 30 seconds"
}
```

---

### `GET /api/elite-wallets/{wallet_address}/activity`

Get detailed activity for a specific elite wallet.

**Response:**
```json
{
  "wallet_address": "2CBHb5hcFiYEBRqRRYM4dFnHhQzAqLGzFPBGXhQCJ3mB",
  "score": 98,
  "statistics": {
    "total_trades": 1423,
    "win_rate": 87.5,
    "total_pnl_sol": 2847.3,
    "average_hold_time_hours": 4.2,
    "best_trade_percent": 876.4,
    "consecutive_wins": 23
  },
  "recent_trades": [
    {
      "token_address": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
      "type": "BUY",
      "amount_sol": 15.0,
      "timestamp": "2025-11-11T17:25:00Z",
      "outcome": "pending"
    }
  ]
}
```

---

### `POST /api/elite-wallets/copy`

Set up copy trading for an elite wallet.

**Request:**
```json
{
  "wallet_address": "2CBHb5hcFiYEBRqRRYM4dFnHhQzAqLGzFPBGXhQCJ3mB",
  "copy_amount_sol": 0.5,
  "max_daily_copies": 10
}
```

**Response:**
```json
{
  "success": true,
  "copy_relationship_id": "copy_12345",
  "wallet_address": "2CBHb5hcFiYEBRqRRYM4dFnHhQzAqLGzFPBGXhQCJ3mB",
  "wallet_score": 98,
  "settings": {
    "copy_amount_sol": 0.5,
    "max_daily_copies": 10,
    "active": true
  }
}
```

---

### `POST /api/elite-wallets/stop-copy`

Stop copying an elite wallet.

**Request:**
```json
{
  "wallet_address": "2CBHb5hcFiYEBRqRRYM4dFnHhQzAqLGzFPBGXhQCJ3mB"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Copy trading stopped for wallet 2CBHb5hcFiYEBRqRRYM4dFnHhQzAqLGzFPBGXhQCJ3mB"
}
```

---

## 📊 Analytics & Statistics

### `GET /api/analytics/performance`

Get detailed performance analytics.

**Response:**
```json
{
  "overview": {
    "total_trades": 1247,
    "wins": 979,
    "losses": 268,
    "win_rate": 78.5,
    "total_pnl_sol": 342.7,
    "roi_percent": 234.8,
    "best_day_pnl_sol": 45.7,
    "worst_day_pnl_sol": -8.3
  },
  "by_phase": {
    "predictions": { "trades": 342, "win_rate": 82.3, "pnl_sol": 156.4 },
    "flash_loans": { "trades": 156, "win_rate": 91.7, "pnl_sol": 89.2 },
    "launch_sniper": { "trades": 89, "win_rate": 75.3, "pnl_sol": 67.3 },
    "pred_markets": { "trades": 23, "win_rate": 69.6, "pnl_sol": 29.8 }
  },
  "daily_performance": [
    { "date": "2025-11-11", "trades": 47, "pnl_sol": 12.5 },
    { "date": "2025-11-10", "trades": 52, "pnl_sol": 8.3 }
  ]
}
```

---

### `GET /api/analytics/tokens`

Get token-level analytics.

**Response:**
```json
{
  "top_gainers": [
    {
      "token_address": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
      "token_name": "USDC",
      "trades": 234,
      "win_rate": 85.7,
      "total_pnl_sol": 67.8,
      "avg_return_percent": 24.3
    }
  ],
  "most_traded": [
    {
      "token_address": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
      "token_name": "USDC",
      "trade_count": 234,
      "total_volume_sol": 456.7
    }
  ]
}
```

---

## 🛡️ Security & Verification

### `POST /api/security/analyze`

Analyze a token through 8-layer security system.

**Request:**
```json
{
  "token_address": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
}
```

**Response:**
```json
{
  "token_address": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
  "overall_score": 92,
  "risk_level": "LOW",
  "recommendation": "SAFE TO TRADE",
  "layers": {
    "rugcheck": { "passed": true, "score": 95, "details": "No rug indicators" },
    "goplus": { "passed": true, "score": 94, "details": "Contract safe" },
    "tokensniffer": { "passed": true, "score": 93, "details": "No honeypot" },
    "rugdoc": { "passed": true, "score": 90, "details": "Verified safe" },
    "birdeye": { "passed": true, "score": 92, "details": "Liquidity adequate" },
    "solana_beach": { "passed": true, "score": 94, "details": "Network stats normal" },
    "internal_honeypot": { "passed": true, "score": 96, "details": "No honeypot detected" },
    "authority_check": { "passed": true, "score": 98, "details": "Authority renounced" }
  },
  "liquidity": {
    "total_sol": 15000,
    "status": "adequate"
  },
  "holders": {
    "count": 8473,
    "distribution": "healthy"
  }
}
```

**Risk Levels:**
- `CRITICAL` (0-40): Do not trade
- `HIGH` (41-60): High risk
- `MEDIUM` (61-75): Moderate risk
- `LOW` (76-100): Safe to trade

---

## 🔌 WebSocket Streams

### Connection

```javascript
const ws = new WebSocket('ws://localhost:8080/ws');

ws.onopen = () => {
  ws.send(JSON.stringify({
    type: 'authenticate',
    api_key: 'YOUR_API_KEY'
  }));
};
```

### Subscribe to Channels

```javascript
// Real-time trade updates
ws.send(JSON.stringify({
  type: 'subscribe',
  channel: 'trades'
}));

// Real-time predictions
ws.send(JSON.stringify({
  type: 'subscribe',
  channel: 'predictions'
}));

// Flash loan opportunities
ws.send(JSON.stringify({
  type: 'subscribe',
  channel: 'flash_opportunities'
}));

// Launch predictions
ws.send(JSON.stringify({
  type: 'subscribe',
  channel: 'launches'
}));

// Security alerts
ws.send(JSON.stringify({
  type: 'subscribe',
  channel: 'security_alerts'
}));
```

### Message Format

```json
{
  "channel": "predictions",
  "data": {
    "token_address": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
    "confidence": 92,
    "direction": "UP",
    "timestamp": "2025-11-11T17:30:00Z"
  }
}
```

---

## ⚡ Rate Limits

**Per API Key:**
- General endpoints: 100 requests/minute
- Trading endpoints: 20 requests/minute
- Analysis endpoints: 30 requests/minute
- WebSocket: 1000 messages/minute

**Tier Multipliers:**
- Bronze: 1x
- Silver: 2x
- Gold: 5x
- Platinum: 10x
- Elite: Unlimited

**Headers:**
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 87
X-RateLimit-Reset: 1699725600
```

---

## ⚠️ Error Codes

### HTTP Status Codes

- `200` - Success
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `429` - Too Many Requests
- `500` - Internal Server Error
- `503` - Service Unavailable

### Error Response Format

```json
{
  "error": {
    "code": "INSUFFICIENT_BALANCE",
    "message": "Insufficient SOL balance. Required: 2.5 SOL, Available: 1.2 SOL",
    "details": {
      "required_sol": 2.5,
      "available_sol": 1.2
    },
    "timestamp": "2025-11-11T17:30:00Z"
  }
}
```

### Common Error Codes

- `INVALID_API_KEY` - API key is invalid or expired
- `INSUFFICIENT_BALANCE` - Not enough SOL in wallet
- `TIER_RESTRICTION` - Feature requires higher tier
- `TOKEN_UNSAFE` - Token failed security checks
- `RATE_LIMIT_EXCEEDED` - Too many requests
- `MARKET_CLOSED` - Trading hours restriction
- `INVALID_TOKEN_ADDRESS` - Invalid Solana address
- `SLIPPAGE_EXCEEDED` - Price moved beyond slippage tolerance
- `LIQUIDITY_TOO_LOW` - Insufficient liquidity for trade
- `CIRCUIT_BREAKER_ACTIVE` - Safety circuit breaker engaged

---

## 🔗 Integration Examples

### Python

```python
import requests

API_KEY = "your_api_key_here"
BASE_URL = "http://localhost:8080"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# Get prediction
response = requests.post(
    f"{BASE_URL}/api/predict",
    json={"token_address": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"},
    headers=headers
)
prediction = response.json()
print(f"Confidence: {prediction['prediction']['confidence']}%")
```

### Node.js

```javascript
const axios = require('axios');

const API_KEY = 'your_api_key_here';
const BASE_URL = 'http://localhost:8080';

const headers = {
  'Authorization': `Bearer ${API_KEY}`,
  'Content-Type': 'application/json'
};

// Get wallet balance
axios.get(`${BASE_URL}/api/wallet/balance`, { headers })
  .then(response => {
    console.log(`SOL Balance: ${response.data.sol_balance}`);
  })
  .catch(error => {
    console.error('Error:', error.response.data);
  });
```

### cURL

```bash
# Get system status
curl -X GET http://localhost:8080/status \
  -H "Authorization: Bearer YOUR_API_KEY"

# Execute a buy order
curl -X POST http://localhost:8080/api/trade/buy \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "token_address": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
    "amount_sol": 1.5,
    "confirm_risk": true
  }'
```

---

## 📞 Support

**Documentation:** https://docs.apollosentinel.com  
**Telegram Support:** @gonehuntingbot  
**Email:** support@apollosentinel.com  
**Status Page:** https://status.apollosentinel.com

---

**Last Updated:** November 11, 2025  
**API Version:** 4.5.0  
**Made with 💎 by APOLLO CyberSentinel**
