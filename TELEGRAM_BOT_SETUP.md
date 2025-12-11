# Telegram Bot Setup

## 🔧 Update Your Telegram Bot Username

The dashboard includes a button that links to your Telegram bot. You need to update the bot username in the HTML file.

### Step 1: Find Your Bot Username

1. Open Telegram
2. Go to @BotFather
3. Send `/mybots`
4. Select your bot
5. Copy the bot username (e.g., `@ApolloTradingBot`)

### Step 2: Update the Dashboard

Open `public/dashboard.html` and find line 607:

```html
<button class="nav-btn" onclick="window.open('https://t.me/gonehuntingbot', '_blank')">
    <i class="fab fa-telegram"></i> Telegram Bot
</button>
```

Your bot username `@gonehuntingbot` has been configured!

### Step 3: Restart the Dashboard

After making the change, restart Docker:

```bash
docker-compose restart apollo-bot
```

## ✅ Navigation Flow

Now your users will experience:

1. **Landing Page** (`/`) - Epic animated landing page with all the features
2. Click **"ENTER TRADING UNIVERSE"** → Goes to Dashboard
3. **Dashboard** (`/dashboard`) - Full trading command center with navigation buttons:
   - **Overview** - System status and metrics
   - **Trading** - Trading controls
   - **AI Intelligence** - AI predictions
   - **Security** - Security features
   - **Monitoring** - Live monitoring
   - **Prediction Market** → Links to `/prediction-market`
   - **Telegram Bot** → Opens your Telegram bot in a new tab
   - **Home** → Back to landing page

## 🎨 Features Added

### Landing Page Updates:
- ✅ Replaced with enhanced neural network animation
- ✅ Floating orbs and particles
- ✅ Animated stats grid (208 pairs, 441 wallets, etc.)
- ✅ Feature cards with hover effects
- ✅ CTA button now links to `/dashboard`

### Dashboard Updates:
- ✅ Added "Prediction Market" button
- ✅ Added "Telegram Bot" button
- ✅ Fixed "Home" button to link to root `/`

## 🚀 Access Your Updated Site

- **Landing Page**: http://localhost:8080
- **Dashboard**: http://localhost:8080/dashboard
- **Prediction Market**: http://localhost:8080/prediction-market
- **Documentation**: http://localhost:8080/docs

Enjoy your epic new landing page! 🎉

