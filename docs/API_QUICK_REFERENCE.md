# 🚀 APOLLO API Quick Reference

**Base URL:** `http://localhost:8080/api/v1`

---

## 📊 User Profile & Stats

```bash
# Get user profile with PnL and rankings
GET /user/{user_id}/profile

# Get detailed stats for specific period
GET /user/{user_id}/stats?days=30

# Get user's trade history
GET /user/{user_id}/trades?limit=50

# Get open positions
GET /user/{user_id}/positions

# Get wallet info
GET /user/{user_id}/wallet
```

---

## 💰 Trading Commands

```bash
# Execute buy order
POST /user/{user_id}/buy
Body: {
  "token_mint": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
  "amount_sol": 0.5,
  "token_symbol": "USDC"
}

# Execute sell order
POST /user/{user_id}/sell
Body: {
  "token_mint": "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263",
  "amount_tokens": "all",
  "token_symbol": "BONK"
}
```

---

## ⚙️ Settings Management

```bash
# Get user settings
GET /user/{user_id}/settings

# Update settings
PUT /user/{user_id}/settings
Body: {
  "max_trade_size_sol": 2.0,
  "snipe_enabled": true,
  "snipe_max_amount": 0.5
}
```

---

## 🤖 AI Analysis

```bash
# Run AI analysis on token
POST /user/{user_id}/analyze
Body: {
  "token_mint": "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263"
}
```

---

## 🏆 Leaderboards & Rankings

```bash
# Get trading leaderboard
GET /leaderboard?limit=50&days=30

# Get trader rankings by reputation
GET /rankings/traders?limit=50
```

---

## 📈 System Metrics (Global)

```bash
# Get overall bot metrics
GET /metrics

# Get 7-day performance
GET /performance

# Get recent trades (all users)
GET /trades/recent?limit=20

# Get top performing tokens
GET /trades/top-tokens
```

---

## 🌐 WebSocket (Real-time Updates)

```javascript
const ws = new WebSocket('ws://localhost:8080/ws');

ws.onmessage = (event) => {
  const update = JSON.parse(event.data);
  console.log('Update:', update);
};
```

---

## 📝 cURL Examples

### Get User Profile
```bash
curl http://localhost:8080/api/v1/user/123456789/profile
```

### Execute Buy Order
```bash
curl -X POST http://localhost:8080/api/v1/user/123456789/buy \
  -H "Content-Type: application/json" \
  -d '{
    "token_mint": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
    "amount_sol": 0.5,
    "token_symbol": "USDC"
  }'
```

### Get Leaderboard
```bash
curl "http://localhost:8080/api/v1/leaderboard?limit=10&days=7"
```

### Update Settings
```bash
curl -X PUT http://localhost:8080/api/v1/user/123456789/settings \
  -H "Content-Type: application/json" \
  -d '{
    "snipe_enabled": true,
    "max_trade_size_sol": 2.0
  }'
```

---

## 🔗 Full Documentation

See `docs/WEB_DASHBOARD_USER_SYSTEM.md` for complete documentation.

