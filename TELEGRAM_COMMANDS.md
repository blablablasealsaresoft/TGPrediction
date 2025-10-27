# 🤖 COMPLETE TELEGRAM BOT COMMAND LIST
## For @gonehuntingbot

---

## 🚀 **GETTING STARTED**

### `/start`
Initialize the bot and get welcome message

### `/help`
Show all available commands with examples

### `/features`
Display all elite features and capabilities

---

## 💰 **WALLET & BALANCE**

### `/wallet`
View your personal wallet details and address

### `/deposit`
Get your wallet address to deposit SOL

### `/balance`
Check your current SOL and token balances

### `/export_wallet` or `/export_keys`
Export your wallet private key (KEEP SECURE!)

---

## 📊 **TRADING COMMANDS**

### `/buy <token_address> <amount_sol>`
Buy tokens (requires confirm token when ALLOW_BROADCAST=true)
```
Examples:
/buy EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v 0.5
/buy EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v 0.5 confirm=lYBjdXRJLcMFCLKCcOmTCCUniHOdi31A
```

### `/sell <token_address> <amount_or_percentage>`
Sell tokens
```
Examples:
/sell EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v 100%
/sell EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v 50%
/sell EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v 1000
```

---

## 🎯 **AUTO-SNIPER COMMANDS**

### `/snipe <token_address>`
Manually snipe a new token launch with Jito protection
```
Example:
/snipe 73TAoGG5uVGSAefLCHTsbppimdmNyHsciM8bYpkbN7cS
/snipe 73TAoGG5uVGSAefLCHTsbppimdmNyHsciM8bYpkbN7cS confirm=lYBjdXRJLcMFCLKCcOmTCCUniHOdi31A
```

### `/snipe_enable`
Enable auto-sniper for your account
- Automatically snipes new token launches
- Uses AI analysis for safety
- Max 5 snipes per day (configurable)

### `/snipe_disable`
Disable auto-sniper for your account

---

## 🧠 **AI & ANALYSIS**

### `/ai_analyze <token_address>` or `/analyze` or `/ai`
Get AI-powered analysis of any token
```
Example:
/ai_analyze EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v

Shows:
- Safety score (0-100)
- Honeypot risk
- Liquidity analysis
- Holder distribution
- AI confidence rating
- Social sentiment
```

---

## 🏆 **COPY TRADING (441 ELITE WALLETS)**

### `/leaderboard`
View top performing wallets (ranked by win rate & profit)
- Shows 441 elite wallets
- Displays performance metrics
- Sortable by different criteria

### `/copy_trader <wallet_address>` or `/copy`
Start copying an elite trader's trades
```
Example:
/copy_trader 23aoMRqqRyESAefLCHTsbppimdmNyHsciM8bYpkbN7cS

Options:
/copy 23aoMRqqRyESAefLCHTsbppimdmNyHsciM8bYpkbN7cS 0.1  (copy with 0.1 SOL per trade)
```

### `/stop_copy <wallet_address>`
Stop copying a trader
```
Example:
/stop_copy 23aoMRqqRyESAefLCHTsbppimdmNyHsciM8bYpkbN7cS
```

### `/rankings`
View wallet intelligence rankings (similar to leaderboard)

---

## 🤖 **AUTOMATED TRADING**

### `/autostart`
Enable automated trading for your account
- AI analyzes all opportunities
- Auto-executes high-confidence trades (>70%)
- Follows 441 elite wallets
- Max 15 trades per day
- Stop-loss/take-profit managed automatically

### `/autostop`
Disable automated trading

### `/autostatus`
Check your automation status and settings

---

## 📈 **STATS & PERFORMANCE**

### `/my_stats` or `/stats`
View your trading performance
- Total trades
- Win rate
- Total P&L
- Best/worst trades
- Current positions

### `/trending`
See trending tokens and opportunities

### `/rewards`
Check your rewards points and achievements
- Points from trades
- Referral bonuses
- Leaderboard rankings

---

## 🎯 **STRATEGY MARKETPLACE**

### `/strategies`
Browse available trading strategies from other users

### `/publish_strategy`
Publish your own trading strategy
- Set price in SOL
- Share with community
- Earn passive income from subscribers

### `/buy_strategy <strategy_id>`
Purchase a strategy from the marketplace

### `/my_strategies`
View strategies you own or published

---

## 🌟 **COMMUNITY FEATURES**

### `/community`
View community stats and engagement

### `/rate_token <token_address> <rating_1-5>`
Rate a token and share feedback
```
Example:
/rate_token EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v 5
```

### `/track <wallet_address>`
Manually track a new wallet for intelligence
```
Example:
/track 23aoMRqqRyESAefLCHTsbppimdmNyHsciM8bYpkbN7cS
```

---

## 🔧 **ADMIN COMMANDS**

### `/metrics`
View system metrics (admin only)
- Total users
- Total trades
- Success rates
- Revenue stats

---

## 🎮 **QUICK START WORKFLOW**

```
1. /start                           → Initialize
2. /wallet                          → Get deposit address
3. /balance                         → Verify balance
4. /leaderboard                     → See 441 elite traders
5. /copy 23aoMRqqRyESAefLC... 0.1   → Start copy trading
6. /autostart                       → Enable automation
7. /snipe_enable                    → Enable auto-sniper
8. /my_stats                        → Monitor performance
```

---

## 💡 **EXAMPLE COMMAND SEQUENCES**

### **Passive Income Setup:**
```
/start
/autostart                          → Enable AI auto-trading
/snipe_enable                       → Enable auto-sniper
/copy 23aoMRqqRyESAefLC... 0.1      → Copy top trader
/autostatus                         → Verify it's running
```

### **Active Trading:**
```
/analyze EPjFWdd5AufqSS...         → AI analysis
/buy EPjFWdd5AufqSS... 0.5         → Buy if good
/my_stats                           → Check position
/sell EPjFWdd5AufqSS... 100%       → Sell when profitable
```

### **Sniping New Launches:**
```
/snipe_enable                       → Auto-snipe new tokens
/trending                           → Find hot new launches
/snipe 73TAoGG5uVGSAef... 0.2      → Manual snipe
```

### **Strategy Trading:**
```
/strategies                         → Browse strategies
/buy_strategy 123                   → Purchase strategy
/my_strategies                      → View your strategies
```

---

## 🔒 **SAFETY NOTES**

### **When ALLOW_BROADCAST=false (current setting):**
- All commands work (simulation mode)
- No real transactions executed
- Perfect for testing

### **When ALLOW_BROADCAST=true (live trading):**
- Add confirm token to ALL trade commands:
```
/buy TOKEN 0.5 confirm=lYBjdXRJLcMFCLKCcOmTCCUniHOdi31A
/sell TOKEN 100% confirm=lYBjdXRJLcMFCLKCcOmTCCUniHOdi31A
/snipe TOKEN confirm=lYBjdXRJLcMFCLKCcOmTCCUniHOdi31A
```

---

## 🚦 **COMMAND ALIASES**

Some commands have shortcuts:
- `/copy` = `/copy_trader`
- `/stats` = `/my_stats`
- `/analyze` = `/ai_analyze` = `/ai`
- `/export_keys` = `/export_wallet`

---

## 🎯 **PRO TIPS**

1. **Start with /autostart** → Let AI do the work
2. **Enable /snipe_enable** → Catch new launches
3. **Copy 3-5 top traders** → Diversify signals
4. **/my_stats daily** → Monitor performance
5. **Use /analyze** before manual trades → AI confidence check

---

## 📱 **INTERACTIVE BUTTONS**

Most commands return interactive buttons:
- Leaderboard → Click to copy trader
- Strategies → Click to buy
- Analysis → Quick buy/sell buttons
- Stats → Quick action buttons

Just click instead of typing! 🖱️

---

## ⚡ **FASTEST WORKFLOWS**

### **Setup (2 minutes):**
```
/start
/autostart
/snipe_enable
```
Done! Bot is now auto-trading + auto-sniping.

### **Check Performance (30 seconds):**
```
/my_stats
/rewards
/leaderboard
```

### **Manual Trade (1 minute):**
```
/analyze <token>
/buy <token> 0.5
/my_stats
```

---

**🔥 YOUR BOT IS READY!** Just message **@gonehuntingbot** and try `/start`! 🚀

