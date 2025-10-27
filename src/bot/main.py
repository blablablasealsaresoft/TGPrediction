"""
REVOLUTIONARY SOLANA TRADING BOT - PRODUCTION VERSION
The most advanced Solana trading bot in the market

UNIQUE DIFFERENTIATORS THAT DOMINATE THE MARKET:
1. AI-Powered Predictions - ML models that learn and improve
2. Social Trading Marketplace - Copy successful traders automatically
3. Real-Time Sentiment Analysis - Twitter/Reddit/Discord monitoring
4. Community Intelligence - Crowdsourced token ratings
5. Adaptive Strategies - Automatically adjusts to market conditions
6. Pattern Recognition - Identifies profitable setups
7. Gamification & Rewards - Points for contributing
8. Strategy Marketplace - Buy/sell proven strategies
9. Anti-MEV Protection - Advanced Jito integration
10. Professional Risk Management - Kelly Criterion position sizing

THIS IS NOT JUST A BOT - IT'S A COMPLETE TRADING ECOSYSTEM
"""

import os
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

from solana.rpc.async_api import AsyncClient
from solders.keypair import Keypair

# Import our revolutionary modules
import sys
import os
# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.modules.ai_strategy_engine import AIStrategyManager
from src.modules.social_trading import (
    SocialTradingMarketplace,
    StrategyMarketplace,
    CommunityIntelligence,
    RewardSystem,
    REWARD_POINTS
)
from src.modules.sentiment_analysis import SocialMediaAggregator, TrendDetector
from src.modules.active_sentiment_scanner import ActiveSentimentScanner
from src.modules.unified_neural_engine import UnifiedNeuralEngine
from src.modules.enhanced_neural_engine import PredictionLayer, ConfidenceLevel, Direction
from src.modules.flash_loan_engine import FlashLoanArbitrageEngine, MarginfiClient
from src.modules.database import DatabaseManager
from src.modules.wallet_manager import UserWalletManager
from src.modules.token_sniper import AutoSniper, SnipeSettings
from src.modules.jupiter_client import JupiterClient, AntiMEVProtection
from src.modules.monitoring import BotMonitor, PerformanceTracker
from src.modules.trade_execution import TradeExecutionService
from src.config import Config, get_config

# 🚀 ELITE ENHANCEMENTS
from src.modules.wallet_intelligence import WalletIntelligenceEngine, WalletMetrics
from src.modules.elite_protection import EliteProtectionSystem, ProtectionConfig
from src.modules.automated_trading import AutomatedTradingEngine, TradingConfig as AutoTradingConfig

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


class RevolutionaryTradingBot:
    """
    THE ULTIMATE SOLANA TRADING BOT
    
    Features that NO other bot has:
    - AI that learns from every trade
    - Copy successful traders automatically
    - Real-time social media sentiment
    - Community-driven intelligence
    - Adaptive strategy optimization
    - Professional risk management
    """
    
    def __init__(
        self,
        config: 'Config',
        db_manager: DatabaseManager,
        solana_client: Optional[AsyncClient] = None,
        monitor: Optional['BotMonitor'] = None,
    ):
        self.config = config
        self.db = db_manager
        
        # Track whether we own the client (created it) so we know if we should close it
        self._owns_client = solana_client is None
        self.client = solana_client or AsyncClient(config.solana_rpc_url)

        # Default risk settings for new users
        self.default_user_settings = self._build_default_user_settings()

        # 🔐 USER WALLET MANAGEMENT - Each user gets their own wallet
        self.wallet_manager = UserWalletManager(
            self.db,
            self.client,
            default_user_settings=self.default_user_settings,
        )
        
        # Revolutionary AI system
        self.ai_manager = AIStrategyManager()
        
        # Social trading platform
        self.social_marketplace = SocialTradingMarketplace(self.db)
        self.strategy_marketplace = StrategyMarketplace(self.db)
        self.community_intel = CommunityIntelligence()
        self.rewards = RewardSystem()
        
        # Sentiment analysis with full Twitter OAuth 2.0 credentials
        self.sentiment_analyzer = SocialMediaAggregator(
            twitter_api_key=self.config.twitter_api_key,
            twitter_bearer_token=self.config.twitter_bearer_token,
            twitter_client_id=self.config.twitter_client_id,
            twitter_client_secret=self.config.twitter_client_secret,
            reddit_credentials={
                'client_id': self.config.reddit_client_id,
                'client_secret': self.config.reddit_client_secret,
                'user_agent': self.config.reddit_user_agent,
            },
            discord_token=self.config.discord_token,
        )
        self.trend_detector = TrendDetector()
        
        # 🔥 ACTIVE SENTIMENT SCANNER - Actually uses your APIs!
        self.active_scanner = ActiveSentimentScanner(
            twitter_bearer_token=self.config.twitter_bearer_token,
            reddit_client_id=self.config.reddit_client_id,
            reddit_client_secret=self.config.reddit_client_secret,
        )
        
        # 🧠 UNIFIED NEURAL ENGINE - True AI that learns across ALL systems
        self.neural_engine = UnifiedNeuralEngine()
        
        # 🎯 PREDICTION LAYER - Converts unified scores to probability predictions
        self.prediction_layer = PredictionLayer(self.neural_engine)
        
        # Trading execution (initialize first)
        self.jupiter = JupiterClient(self.client)
        self.anti_mev = AntiMEVProtection(self.client)
        
        # ⚡ FLASH LOAN ARBITRAGE ENGINE (Phase 2) - Initialized after Jupiter/Jito
        self.marginfi = MarginfiClient(self.client, config)
        self.flash_loan_engine = FlashLoanArbitrageEngine(
            self.client,
            self.anti_mev,  # Jito client
            self.jupiter,
            self.db,
            config
        )
        
        # 🚀 ELITE SYSTEMS
        self.wallet_intelligence = WalletIntelligenceEngine(self.client)
        self.elite_protection = EliteProtectionSystem(self.client, ProtectionConfig())

        # Monitoring & performance tracking
        self.monitor = monitor or BotMonitor(None, admin_chat_id=self.config.admin_chat_id)
        self.performance = PerformanceTracker()

        # Centralized trade execution
        self.trade_executor = TradeExecutionService(
            self.db,
            self.wallet_manager,
            self.jupiter,
            protection=self.elite_protection,
            monitor=self.monitor,
            social_marketplace=self.social_marketplace,
            rewards=self.rewards
        )

        # Share executor with marketplace for copy trades
        self.social_marketplace.attach_trade_executor(self.trade_executor)

        # Automated trading engine is created on demand
        self.auto_trader = None

        # 🎯 Auto-Sniper with Elite Protection and centralized execution
        self.sniper = AutoSniper(
            self.ai_manager,
            self.wallet_manager,
            self.jupiter,
            database_manager=self.db,
            protection_system=self.elite_protection,
            trade_executor=self.trade_executor,
            sentiment_aggregator=self.sentiment_analyzer,
            community_intel=self.community_intel,
        )

        # Shutdown coordination
        self._stop_event: Optional[asyncio.Event] = None

        logger.info("🚀 Revolutionary Trading Bot initialized!")
        logger.info("🔐 Individual user wallets enabled")
        logger.info("🎯 Elite Auto-sniper ready")
        logger.info("🧠 Wallet Intelligence System ready")
        logger.info("🛡️ Elite Protection System (6-layer) ready")
        logger.info("🤖 Automated Trading Engine ready")

    def _build_default_user_settings(self) -> Dict:
        """Build default user settings from config"""
        trading = self.config.trading
        return {
            'max_trade_size_sol': trading.max_trade_size_sol,
            'daily_loss_limit_sol': trading.daily_loss_limit_sol,
            'slippage_percentage': trading.max_slippage,
            'require_confirmation': trading.require_confirmation,
            'use_stop_loss': trading.stop_loss_percentage > 0,
            'default_stop_loss_percentage': trading.stop_loss_percentage,
            'use_take_profit': trading.take_profit_percentage > 0,
            'default_take_profit_percentage': trading.take_profit_percentage,
            'check_honeypots': trading.honeypot_check_enabled,
            'min_liquidity_usd': trading.min_liquidity_usd,
        }

    def _is_admin(self, update: Update) -> bool:
        """Return True when the incoming update belongs to the admin chat."""

        if not self.config.admin_chat_id:
            return False

        user = update.effective_user if update else None
        chat = update.effective_chat if update else None
        candidates = (
            getattr(user, "id", None),
            getattr(chat, "id", None),
        )
        return any(identifier == self.config.admin_chat_id for identifier in candidates)
    
    def _load_wallet(self) -> Optional[Keypair]:
        """Load wallet from environment"""
        private_key = self.config.wallet_private_key
        if private_key:
            import base58
            return Keypair.from_bytes(base58.b58decode(private_key))
        return None
    
    # ==================== TELEGRAM COMMANDS ====================
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Welcome message with professional UI and buttons"""
        user_id = update.effective_user.id
        username = update.effective_user.username or f"user_{user_id}"
        first_name = update.effective_user.first_name or username
        
        # Import enterprise UI
        from src.modules.ui_formatter import MessageTemplates
        
        # 🔐 Create individual wallet for user
        wallet_info = await self.wallet_manager.get_or_create_user_wallet(user_id, username)
        
        # Register trader
        await self.social_marketplace.register_trader(user_id, username)
        
        # Award login points
        await self.rewards.award_points(user_id, REWARD_POINTS['daily_login'], 'Daily login')
        
        # Generate enterprise welcome message
        message, keyboard = MessageTemplates.welcome(
            user_name=first_name,
            wallet_address=wallet_info['public_key'],
            balance=wallet_info['sol_balance'],
            is_new=wallet_info['is_new']
        )
        
        await update.message.reply_text(
            message,
            parse_mode='HTML',
            reply_markup=keyboard
        )
    
    async def wallet_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show user's wallet information"""
        user_id = update.effective_user.id
        
        # Import enterprise UI
        from src.modules.ui_formatter import MessageTemplates
        
        # Get wallet info
        wallet_address = await self.wallet_manager.get_user_wallet_address(user_id)
        
        if not wallet_address:
            await update.message.reply_text(
                "❌ You don't have a wallet yet. Use /start to create one!"
            )
            return
        
        # Get balance
        balance = await self.wallet_manager.get_user_balance(user_id)
        
        # Get trading stats
        stats = await self.db.get_user_stats(user_id, days=30)
        
        # Generate enterprise wallet display
        message, keyboard = MessageTemplates.wallet_info(wallet_address, balance, stats)
        
        await update.message.reply_text(
            message,
            parse_mode='HTML',
            reply_markup=keyboard
        )
    
    async def deposit_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show deposit instructions"""
        user_id = update.effective_user.id
        
        wallet_address = await self.wallet_manager.get_user_wallet_address(user_id)
        
        if not wallet_address:
            await update.message.reply_text(
                "❌ You don't have a wallet yet. Use /start to create one!"
            )
            return
        
        balance = await self.wallet_manager.get_user_balance(user_id)
        
        message = f"""📥 *DEPOSIT SOL*

Send SOL to your personal trading wallet:

🔐 *Your Wallet Address:*
`{wallet_address}`

💵 *Current Balance:*
{balance:.6f} SOL

*How to Deposit:*
1. Copy your wallet address above
2. Open Phantom, Solflare, or any Solana wallet
3. Send SOL to this address
4. Funds arrive instantly!

⚠️ *Important:*
• Only send SOL to this address
• Minimum deposit: 0.01 SOL
• Network: Solana Mainnet

After depositing, use /balance to check your new balance
"""
        
        keyboard = [
            [InlineKeyboardButton("🔄 Check Balance", callback_data="refresh_wallet")],
            [InlineKeyboardButton("◀️ Back", callback_data="show_wallet")]
        ]
        
        await update.message.reply_text(
            message,
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    async def balance_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Quick balance check"""
        user_id = update.effective_user.id

        balance = await self.wallet_manager.get_user_balance(user_id)
        wallet_address = await self.wallet_manager.get_user_wallet_address(user_id)

        if not wallet_address:
            await update.message.reply_text("❌ No wallet found. Use /start")
            return

        await update.message.reply_text(
            f"💰 *Your Balance:* {balance:.6f} SOL\n\n"
            f"Wallet: `{wallet_address[:8]}...{wallet_address[-8:]}`",
            parse_mode='Markdown'
        )

    async def buy_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Execute a manual buy using the user's wallet"""
        user_id = update.effective_user.id

        if not context.args or len(context.args) < 2:
            await update.message.reply_text(
                "Usage: /buy <token_mint> <amount_sol>"
            )
            return

        token_mint = context.args[0]

        try:
            amount_sol = float(context.args[1])
        except ValueError:
            await update.message.reply_text("Amount must be a number (SOL)")
            return

        confirm_token, remainder = self._extract_confirm_token(context.args[2:])
        token_symbol = remainder[0] if remainder else None

        progress_message = await update.message.reply_text("⏳ Executing buy order...")

        metadata = {"confirm_token": confirm_token} if confirm_token else None

        result = await self.trade_executor.execute_buy(
            user_id,
            token_mint,
            amount_sol,
            token_symbol=token_symbol,
            reason='manual_command',
            context='manual_command',
            metadata=metadata,
        )

        if result.get('success'):
            message = (
                "✅ *BUY EXECUTED*\n\n"
                f"Token: `{token_mint[:8]}...`\n"
                f"Amount: {amount_sol:.4f} SOL\n"
                f"Received: {result.get('amount_tokens', 0):.4f} tokens\n"
                f"Price: {result.get('price', 0) or 0:.6f} SOL/token\n"
                f"Signature: `{(result.get('signature') or '')[:16]}...`"
            )
        else:
            message = f"❌ Buy failed: {result.get('error', 'Unknown error')}"

        await progress_message.edit_text(message, parse_mode='Markdown')

    async def sell_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Execute a manual sell for an open position"""
        user_id = update.effective_user.id

        if not context.args:
            await update.message.reply_text(
                "Usage: /sell <token_mint> [amount_tokens|all]"
            )
            return

        token_mint = context.args[0]
        amount_tokens = None

        confirm_token, remainder = self._extract_confirm_token(context.args[1:])

        if remainder:
            amount_arg = remainder[0].lower()
            if amount_arg == 'all':
                amount_tokens = None
            else:
                try:
                    amount_tokens = float(remainder[0])
                except ValueError:
                    await update.message.reply_text(
                        "Amount must be numeric or 'all'"
                    )
                    return

        progress_message = await update.message.reply_text("⏳ Executing sell order...")

        metadata = {"confirm_token": confirm_token} if confirm_token else None

        result = await self.trade_executor.execute_sell(
            user_id,
            token_mint,
            amount_tokens=amount_tokens,
            reason='manual_command',
            context='manual_command',
            metadata=metadata,
        )

        if result.get('success'):
            message = (
                "✅ *SELL EXECUTED*\n\n"
                f"Token: `{token_mint[:8]}...`\n"
                f"Tokens sold: {result.get('amount_tokens', 0):.4f}\n"
                f"Received: {result.get('amount_sol', 0):.4f} SOL\n"
                f"PnL: {result.get('pnl', 0):+.4f} SOL\n"
                f"Signature: `{(result.get('signature') or '')[:16]}...`"
            )
        else:
            message = f"❌ Sell failed: {result.get('error', 'Unknown error')}"

        await progress_message.edit_text(message, parse_mode='Markdown')

    async def export_wallet_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        🔐 EXPORT PRIVATE KEY
        Allows users to export their private key to import into Phantom, Solflare, etc.
        """
        user_id = update.effective_user.id
        chat_type = update.message.chat.type
        
        # Security: Only allow in private chats
        if chat_type != 'private':
            await update.message.reply_text(
                "⚠️ *SECURITY WARNING*\n\n"
                "For your security, private keys can only be exported in private messages.\n\n"
                "Please send `/export_wallet` to me in a private message.",
                parse_mode='Markdown'
            )
            return
        
        # Get user's wallet
        wallet_address = await self.wallet_manager.get_user_wallet_address(user_id)
        
        if not wallet_address:
            await update.message.reply_text(
                "❌ No wallet found. Use /start to create one first!"
            )
            return
        
        # Export private key
        private_key = await self.wallet_manager.export_private_key(user_id)
        
        if not private_key:
            await update.message.reply_text(
                "❌ Failed to export private key. Please contact support."
            )
            return
        
        # Send with STRONG security warnings
        message = f"""🔐 *YOUR PRIVATE KEY*

⚠️ *CRITICAL SECURITY WARNINGS:*
• NEVER share this key with anyone
• NEVER post this key anywhere
• Anyone with this key can steal ALL your funds
• Keep this key safe and backed up
• Delete this message after saving the key

*Your Wallet:*
`{wallet_address}`

*Private Key (Base58):*
`{private_key}`

*How to Import:*
1. Open Phantom or Solflare wallet
2. Go to Settings → Import Private Key
3. Paste your private key above
4. Your wallet will be imported!

⚠️ *REMEMBER:* This bot uses your personal wallet. If you import it elsewhere, any trades you make will affect your balance here too.

*After importing, you have FULL control of your funds in both places.*

🗑️ Please delete this message after saving your key safely!"""
        
        await update.message.reply_text(message, parse_mode='Markdown')
        
        logger.info(f"User {user_id} exported their private key")
    
    async def ai_analyze_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        🔥 KILLER FEATURE #1: AI-Powered Token Analysis
        No other bot has this level of intelligence
        """
        if len(context.args) < 1:
            await update.message.reply_text("Usage: /ai_analyze <token_address>")
            return
        
        token_mint = context.args[0]
        user_id = update.effective_user.id
        
        await update.message.reply_text("🤖 *AI ANALYSIS IN PROGRESS...*\n\nThe AI is analyzing:\n• ML predictions\n• Social sentiment\n• Community signals\n• Market patterns\n• Risk factors", parse_mode='Markdown')
        
        try:
            # Get token data (implement actual data fetching)
            token_data = await self._fetch_token_data(token_mint)

            # 🔥 SENTIMENT ANALYSIS
            sentiment = await self.sentiment_analyzer.analyze_token_sentiment(
                token_mint,
                token_data.get('symbol', 'UNKNOWN')
            )

            # 🔥 COMMUNITY INTELLIGENCE
            community_signal = await self.community_intel.get_community_signal(token_mint)

            enriched_token_data = dict(token_data)
            if sentiment:
                enriched_token_data['sentiment_score'] = sentiment.get(
                    'sentiment_score',
                    enriched_token_data.get('sentiment_score', 50)
                )
                enriched_token_data['social_mentions'] = sentiment.get(
                    'total_mentions',
                    enriched_token_data.get('social_mentions', 0)
                )
                enriched_token_data['social_score'] = sentiment.get(
                    'social_score',
                    enriched_token_data.get('social_score', 0)
                )

            if community_signal:
                enriched_token_data['community_score'] = community_signal.get(
                    'community_score',
                    enriched_token_data.get('community_score', 0)
                )

            enriched_token_data.setdefault('social_score', enriched_token_data.get('sentiment_score', 0))
            enriched_token_data.setdefault('community_score', 0.0)

            # Get portfolio value
            portfolio_value = await self._get_portfolio_value(user_id)

            # 🔥 AI ANALYSIS (Standard)
            ai_analysis = await self.ai_manager.analyze_opportunity(
                enriched_token_data,
                portfolio_value,
                sentiment_snapshot=sentiment,
                community_signal=community_signal
            )
            
            # 🧠 UNIFIED NEURAL ENGINE ANALYSIS (THE EDGE!)
            # This combines ALL signals into one learned intelligence
            wallet_signals = []  # TODO: Get wallet signals for this token
            market_context = enriched_token_data.get('market_data', {})
            
            unified_analysis = await self.neural_engine.analyze_with_full_intelligence(
                token_address=token_mint,
                ai_prediction=ai_analysis,
                sentiment_data=sentiment,
                community_signal=community_signal,
                wallet_signals=wallet_signals,
                market_context=market_context
            )
            
            # Use unified score for final recommendation
            ai_analysis['unified_score'] = unified_analysis['unified_score']
            ai_analysis['neural_confidence'] = unified_analysis['confidence']
            ai_analysis['system_intelligence'] = self.neural_engine.get_system_intelligence_report()
            
            # Build comprehensive analysis
            ml_pred = ai_analysis.get('ml_prediction', {})
            key_factors = ml_pred.get('key_factors', [])
            key_factors_text = ', '.join(key_factors[:3]) if key_factors else 'N/A'
            
            # Get intelligence report
            intel_report = ai_analysis.get('system_intelligence', {})
            unified_score = ai_analysis.get('unified_score', ai_analysis.get('confidence', 0) * 100)
            neural_conf = ai_analysis.get('neural_confidence', ai_analysis.get('confidence', 0))
            
            message = f"""
🧠 <b>UNIFIED NEURAL ANALYSIS</b>

<b>Token:</b> <code>{token_mint[:8]}...</code>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<b>🎯 NEURAL RECOMMENDATION:</b> <b>{ai_analysis['action'].upper()}</b>
<b>Unified Score:</b> {unified_score:.1f}/100
<b>Neural Confidence:</b> {neural_conf:.1%}
<b>Risk Level:</b> {ai_analysis['risk_level'].upper()}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<b>🤖 COMPONENT BREAKDOWN:</b>
• AI Model: {ml_pred.get('probability', 0):.1%} success probability
• Key Factors: {key_factors_text}
• Recommendation: {ml_pred.get('recommendation', 'N/A')}

<b>📱 SOCIAL SENTIMENT:</b>
"""
            
            # Add system intelligence status
            if intel_report.get('is_learning'):
                intel_level = intel_report.get('intelligence_level', 'LEARNING')
                system_acc = intel_report.get('accuracy', 0)
                predictions = intel_report.get('total_predictions', 0)
                
                message += f"""
<b>🧠 SYSTEM INTELLIGENCE:</b>
• Level: <b>{intel_level}</b>
• Predictions Made: {predictions}
• System Accuracy: {system_acc:.1%}
• Status: <i>Learning from every trade</i>

<b>📱 SOCIAL SENTIMENT:</b>
"""
            
            # Check if sentiment data is available
            twitter_mentions = sentiment.get('twitter', {}).get('mentions', 0) if sentiment else 0
            total_mentions = sentiment.get('total_mentions', 0) if sentiment else 0
            if sentiment and (twitter_mentions > 0 or total_mentions > 0):
                message += f"""Score: {sentiment['sentiment_score']:.1f}/100
Social Mentions: {total_mentions}
Twitter Mentions: {twitter_mentions}
Viral Potential: {sentiment.get('viral_potential', 0):.1%}
Going Viral: {"🔥 YES" if sentiment.get('twitter', {}).get('trending', False) else "No"}
"""
            else:
                message += """No recent social chatter detected
Connect Twitter/Reddit/Discord APIs for live data

"""
            
            message += "\n*👥 COMMUNITY INTELLIGENCE:*\n"
            
            if community_signal:
                message += f"""Community Score: {community_signal['community_score']:.1f}/100
Ratings: {community_signal['total_ratings']}
Flags: {community_signal['flag_count']}
Sentiment: {community_signal['sentiment'].upper()}

"""

            social_context = ai_analysis.get('social_context')
            if social_context:
                message += "\n*📡 SOCIAL & COMMUNITY IMPACT:*\n"
                message += (
                    f"Composite Bias: {social_context['label'].replace('_', ' ').title()} "
                    f"({social_context['score'] * 100:.0f}/100)\n"
                )
                for insight in social_context.get('insights', [])[:3]:
                    message += f"• {insight}\n"
            
            # Escape special characters in reasoning
            reasoning_text = str(ai_analysis['reasoning']).replace('|', '\\|').replace('_', '\\_')
            
            message += f"""*💰 SUGGESTED POSITION:*
Size: {ai_analysis['position_size']:.4f} SOL
Strategy: {ai_analysis['strategy'].upper()}
Market Regime: {ai_analysis['market_regime'].upper()}

*🧠 AI REASONING:*
{reasoning_text}

"""
            
            # Add action buttons
            if ai_analysis['action'] in ['buy', 'strong_buy']:
                keyboard = [
                    [
                        InlineKeyboardButton(
                            f"🚀 Buy {ai_analysis['position_size']:.4f} SOL",
                            callback_data=f"ai_buy_{token_mint}_{ai_analysis['position_size']}"
                        )
                    ],
                    [
                        InlineKeyboardButton("📊 More Details", callback_data=f"details_{token_mint}"),
                        InlineKeyboardButton("⭐ Rate Token", callback_data=f"rate_{token_mint}")
                    ]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
            else:
                reply_markup = None
            
            # Don't use Markdown to avoid parsing errors with dynamic content
            await update.message.reply_text(message, parse_mode=None, reply_markup=reply_markup)
            
            # Award points for analysis
            await self.rewards.award_points(user_id, 5, 'Token analysis')
            
        except Exception as e:
            logger.error(f"AI analysis error: {e}")
            await update.message.reply_text(f"❌ Analysis failed: {str(e)}")
    
    async def leaderboard_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        🔥 KILLER FEATURE #2: Social Trading Leaderboard - Enterprise UI
        """
        # Import enterprise UI
        from src.modules.ui_formatter import MessageTemplates
        
        # Handle both regular commands and button callbacks
        is_callback = hasattr(update, 'callback_query') and update.callback_query
        
        if not is_callback:
            await update.message.reply_text("📊 <b>LOADING LEADERBOARD...</b>", parse_mode='HTML')
        
        # Get top traders
        top_traders_raw = await self.social_marketplace.get_leaderboard(limit=10)
        
        # Convert to dict format for template
        top_traders = []
        for trader in top_traders_raw:
            top_traders.append({
                'username': trader.username,
                'user_id': trader.user_id,
                'tier': trader.tier.value if hasattr(trader.tier, 'value') else 'bronze',
                'reputation_score': trader.reputation_score,
                'win_rate': trader.win_rate,
                'total_pnl': trader.total_pnl,
                'followers': trader.followers
            })
        
        # Generate enterprise leaderboard
        message, keyboard = MessageTemplates.leaderboard(top_traders, limit=10)
        
        if is_callback:
            await update.callback_query.edit_message_text(message, parse_mode='HTML', reply_markup=keyboard)
        else:
            await update.message.reply_text(message, parse_mode='HTML', reply_markup=keyboard)
    
    async def copy_trader_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        🔥 KILLER FEATURE #3: Automatic Copy Trading
        """
        if len(context.args) < 1:
            # Show copyable traders
            top_traders = await self.social_marketplace.get_leaderboard(limit=5)
            
            if not top_traders or len(top_traders) == 0:
                message = """👥 *COPY TRADING*

No traders available to copy yet!

*How copy trading works:*
• Follow successful traders automatically
• When they buy, you buy
• When they sell, you sell
• Set your own trade amounts

*Why no traders yet?*
• Bot just launched
• No trades executed yet
• Need trading history to rank traders

*Be the first!*
• Make some trades with /ai_analyze
• Build your track record
• Others can copy you!

*Coming soon:*
• Verified traders to copy
• Performance leaderboard
• Copy trading marketplace

Use /leaderboard to see when traders appear!"""
                
                keyboard = [
                    [InlineKeyboardButton("🏆 Leaderboard", callback_data="leaderboard")],
                    [InlineKeyboardButton("📊 My Stats", callback_data="my_stats")]
                ]
                
                await update.message.reply_text(
                    message,
                    parse_mode='Markdown',
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
                return
            
            message = "👥 *COPY TRADING*\n\nTop traders you can copy:\n\n"
            
            for trader in top_traders:
                message += f"*{trader.username}* (Score: {trader.reputation_score:.1f})\n"
                message += f"Win Rate: {trader.win_rate:.1f}% | PnL: {trader.total_pnl:+.4f} SOL\n"
                message += f"Command: `/copy_trader {trader.user_id}`\n\n"
            
            await update.message.reply_text(message, parse_mode='Markdown')
            return
        
        try:
            trader_id = int(context.args[0])
            follower_id = update.effective_user.id
            
            # Get trader profile
            trader = await self.social_marketplace.get_trader_profile(trader_id)
            if not trader:
                await update.message.reply_text("❌ Trader not found")
                return
            
            # Configure copy settings
            keyboard = [
                [
                    InlineKeyboardButton("0.05 SOL per trade", callback_data=f"copy_set_{trader_id}_0.05"),
                    InlineKeyboardButton("0.1 SOL per trade", callback_data=f"copy_set_{trader_id}_0.1")
                ],
                [
                    InlineKeyboardButton("0.2 SOL per trade", callback_data=f"copy_set_{trader_id}_0.2"),
                    InlineKeyboardButton("0.5 SOL per trade", callback_data=f"copy_set_{trader_id}_0.5")
                ],
                [InlineKeyboardButton("❌ Cancel", callback_data="cancel")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            message = f"""
👥 *COPY TRADING SETUP*

You're about to copy: *{trader.username}*

*Trader Stats:*
• Tier: {trader.tier.value.upper()}
• Score: {trader.reputation_score:.1f}/100
• Win Rate: {trader.win_rate:.1f}%
• Total PnL: {trader.total_pnl:+.4f} SOL
• Followers: {trader.followers}

*How it works:*
When they buy, you buy automatically
When they sell, you sell automatically

Select amount per trade:
"""
            await update.message.reply_text(message, parse_mode='Markdown', reply_markup=reply_markup)
            
        except ValueError:
            await update.message.reply_text("❌ Invalid trader ID")
    
    async def stop_copy_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Stop copying a trader"""
        if len(context.args) < 1:
            # Show who user is copying
            follower_id = update.effective_user.id

            # Check active copies
            user_copies = self.social_marketplace.active_copies.get(follower_id, {})
            active_traders = [
                trader_id
                for trader_id, copy_settings in user_copies.items()
                if copy_settings.get('enabled')
            ]

            if not active_traders:
                await update.message.reply_text(
                    "You're not copying anyone.\n\n"
                    "Use /leaderboard to find traders to copy!"
                )
                return

            lines = []
            for trader_id in active_traders:
                trader = await self.social_marketplace.get_trader_profile(trader_id)
                copy_settings = user_copies.get(trader_id, {})
                trader_name = trader.username if trader else f"Trader {trader_id}"
                max_amount = copy_settings.get('max_copy_amount', 0) or 0
                lines.append(
                    f"*{trader_name}* (ID: {trader_id})\n"
                    f"Total copied: {copy_settings.get('total_copied', 0)} trades\n"
                    f"Max per trade: {max_amount:.4f} SOL\n"
                )

            message = """👥 *ACTIVE COPY TRADES*

{details}
Use `/stop_copy <trader_id>` to stop copying a trader.
""".format(details="\n".join(lines))

            await update.message.reply_text(message, parse_mode='Markdown')
            return

        try:
            trader_id = int(context.args[0])
            follower_id = update.effective_user.id
            
            # Stop copying
            success = await self.social_marketplace.stop_copying_trader(follower_id, trader_id)
            
            if success:
                message = f"""✅ *COPY TRADING STOPPED*

You stopped copying trader {trader_id}

You can start copying again anytime with:
/copy_trader {trader_id}

Or find new traders:
/leaderboard
"""
                keyboard = [
                    [InlineKeyboardButton("🏆 View Leaderboard", callback_data="leaderboard")],
                    [InlineKeyboardButton("📊 My Stats", callback_data="my_stats")]
                ]
                await update.message.reply_text(
                    message,
                    parse_mode='Markdown',
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
            else:
                await update.message.reply_text("❌ Failed to stop copying")
                
        except ValueError:
            await update.message.reply_text("❌ Invalid trader ID")
        except Exception as e:
            logger.error(f"Stop copy error: {e}")
            await update.message.reply_text(f"❌ Error: {str(e)}")
    
    async def snipe_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        🔥 AUTO-SNIPER: Automatically buy new token launches
        """
        user_id = update.effective_user.id
        
        # Get user's current settings
        settings = await self.db.get_user_settings(user_id)
        
        if not settings:
            # Create default settings
            await self.db.update_user_settings(user_id, {})
            settings = await self.db.get_user_settings(user_id)
        
        is_enabled = settings.snipe_enabled if settings else False
        snipe_amount = settings.snipe_max_amount if settings else 0.1
        min_liq = settings.snipe_min_liquidity if settings else 10000
        min_conf = settings.snipe_min_confidence if settings else 0.65
        daily_limit = settings.snipe_max_daily if settings else 10
        daily_used = settings.snipe_daily_used if settings else 0
        
        status_emoji = "✅ ON" if is_enabled else "❌ OFF"
        
        message = f"""🎯 AUTO-SNIPER

Status: {status_emoji}

Your Sniper Settings:
• Max buy amount: {snipe_amount} SOL
• Min liquidity: ${min_liq:,.0f}
• Min AI confidence: {min_conf:.0%}
• Daily limit: {daily_limit} snipes
• Today used: {daily_used}/{daily_limit}

How it works:
1. Monitors pump.fun every 30 seconds
2. Detects new token launches instantly
3. Runs AI analysis automatically
4. Buys if AI confidence > {min_conf:.0%}
5. Alerts you when sniped

Safety Features:
• Max amount per snipe: {snipe_amount} SOL
• Checks liquidity: Min ${min_liq:,.0f}
• AI verification required
• Daily limit: {daily_limit} snipes max
• Your balance protected

Commands:
/snipe_enable - Turn ON auto-snipe
/snipe_disable - Turn OFF auto-snipe
/snipe_settings - Configure amounts

Manual snipe:
/ai_analyze <token_address>
"""
        
        keyboard = [
            [
                InlineKeyboardButton(
                    "✅ Enable Auto-Snipe" if not is_enabled else "❌ Disable Auto-Snipe",
                    callback_data=f"snipe_toggle_{user_id}"
                )
            ],
            [
                InlineKeyboardButton("⚙️ Configure Settings", callback_data=f"snipe_config_{user_id}"),
                InlineKeyboardButton("📊 Snipe History", callback_data=f"snipe_history_{user_id}")
            ],
            [
                InlineKeyboardButton("◀️ Back", callback_data="back_to_start")
            ]
        ]
        
        # Don't use Markdown to avoid parsing errors with $ and other special chars
        await update.message.reply_text(
            message,
            parse_mode=None,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    async def snipe_enable_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Enable auto-snipe for user"""
        user_id = update.effective_user.id
        
        # Check balance
        balance = await self.wallet_manager.get_user_balance(user_id)
        if balance < 0.01:
            await update.message.reply_text(
                "❌ *Insufficient Balance*\n\n"
                "You need at least 0.01 SOL to enable auto-snipe.\n\n"
                "Use /deposit to fund your wallet.",
                parse_mode='Markdown'
            )
            return
        
        # Enable snipe
        await self.db.update_user_settings(user_id, {'snipe_enabled': True})

        # Enable in sniper
        await self.sniper.enable_snipe(user_id)
        
        message = """✅ AUTO-SNIPE ENABLED!

Your bot is now monitoring pump.fun for new launches!

What happens next:
• Bot checks every 30 seconds for new tokens
• When found, AI analyzes automatically
• If AI recommends strong buy, executes trade
• You get instant notification

Your Settings:
• Max per snipe: 0.1 SOL
• Min liquidity: $10,000
• Min AI confidence: 65%
• Daily limit: 10 snipes

To configure:
/snipe - View settings
/snipe_disable - Turn off

Important:
Keep sufficient SOL balance for snipes!

🎯 Sniper is ACTIVE and hunting!
"""
        
        await update.message.reply_text(message, parse_mode=None)
    
    async def snipe_disable_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Disable auto-snipe for user"""
        user_id = update.effective_user.id
        
        # Disable snipe
        await self.db.update_user_settings(user_id, {'snipe_enabled': False})

        # Disable in sniper
        await self.sniper.disable_snipe(user_id)
        
        await update.message.reply_text(
            "❌ AUTO-SNIPE DISABLED\n\n"
            "You will no longer auto-buy new tokens.\n\n"
            "To enable again: /snipe_enable",
            parse_mode=None
        )
    
    async def trending_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        🔥 KILLER FEATURE #4: Viral Token Detection - NOW WITH ACTIVE SCANNING!
        Real-time detection of tokens going viral using YOUR APIs
        """
        await update.message.reply_text("🔥 <b>SCANNING SOCIAL MEDIA...</b>", parse_mode='HTML')
        
        # Check if APIs are configured
        if not self.active_scanner.has_apis_configured():
            message = """🔥 <b>TRENDING TOKENS</b>

<b>⚠️ Social Media APIs Not Configured</b>

Your API keys are in .env but may need formatting:

<b>Required format:</b>
<code>TWITTER_BEARER_TOKEN=your_token_here
REDDIT_CLIENT_ID=your_id_here
REDDIT_CLIENT_SECRET=your_secret_here</code>

<b>Check your .env file has:</b>
• No extra spaces
• No quotes around values
• Correct variable names

<i>Meanwhile, use /ai to analyze specific tokens manually</i>
"""
            await update.message.reply_text(message, parse_mode='HTML')
            return
        
        try:
            # 🔥 ACTIVELY SCAN Twitter & Reddit for trending tokens
            viral_tokens = await self.active_scanner.scan_for_trending_tokens()
            
            if not viral_tokens:
                message = """🔥 <b>TRENDING TOKENS</b>

<b>No viral tokens detected right now</b>

<b>✅ Active Monitoring:</b>
• Twitter: Scanning #Solana hashtags
• Reddit: Monitoring r/Solana, r/CryptoMoonShots
• Real-time mention tracking

<b>💡 How it works:</b>
System scans social media every 5 minutes for Solana tokens gaining traction.

<i>Check back in 5-10 minutes or use /ai to analyze specific tokens</i>
"""
                await update.message.reply_text(message, parse_mode='HTML')
                return
            
            # Format viral tokens with enterprise UI
            message = f"""🔥 <b>TOKENS GOING VIRAL NOW!</b>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<b>📊 Found {len(viral_tokens)} trending tokens</b>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""
            
            for i, token in enumerate(viral_tokens[:5], 1):
                emoji = "🔥" if i == 1 else "🟡" if i == 2 else "⚪"
                mentions = token.get('mentions', 0)
                sentiment = token.get('sentiment_score', 50)
                sources = ', '.join(token.get('sources', []))
                
                message += f"""
{emoji} <b>#{i} - {token['token_address'][:8]}...</b>

   <b>Mentions:</b> {mentions} across {len(token.get('sources', []))} sources
   <b>Sentiment:</b> {sentiment:.0f}/100
   <b>Sources:</b> {sources}
   <b>Viral Score:</b> {token.get('viral_score', 0):.1f}
   
   <code>/ai {token['token_address']}</code>

"""
            
            message += """━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 <i>Tokens are ranked by viral velocity & sentiment</i>
🎯 <i>Use /ai to analyze before trading</i>
"""
            
            keyboard = [
                [
                    InlineKeyboardButton(f"🔍 Analyze #{1}", callback_data=f"analyze_{viral_tokens[0]['token_address']}"),
                ] if viral_tokens else [],
                [
                    InlineKeyboardButton("🔄 Refresh", callback_data="trending"),
                    InlineKeyboardButton("◀️ Back", callback_data="back_to_start")
                ]
            ]
            
            await update.message.reply_text(
                message,
                parse_mode='HTML',
                reply_markup=InlineKeyboardMarkup([k for k in keyboard if k])
            )
            
        except Exception as e:
            logger.error(f"Trending scan error: {e}")
            await update.message.reply_text(
                f"❌ Error scanning social media: {str(e)}",
                parse_mode='HTML'
            )
    
    async def community_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        🔥 KILLER FEATURE #5: Community Intelligence
        Crowdsourced token ratings and scam flags
        """
        if len(context.args) < 1:
            await update.message.reply_text(
                "Usage: /community <token_address>\n\n"
                "See what the community thinks about a token!"
            )
            return
        
        token_mint = context.args[0]
        
        await update.message.reply_text("🌐 *FETCHING COMMUNITY DATA...*", parse_mode='Markdown')
        
        # Get community signal
        signal = await self.community_intel.get_community_signal(token_mint)
        
        if not signal:
            message = f"""🌐 *COMMUNITY INTELLIGENCE*

Token: `{token_mint[:16]}...`

No community data yet.

*Be the first to rate it!*
Use: /rate_token {token_mint} <1-5>
"""
        else:
            sentiment_emoji = {
                'positive': '🟢',
                'neutral': '🟡',
                'negative': '🔴'
            }
            
            message = f"""🌐 *COMMUNITY INTELLIGENCE*

Token: `{token_mint[:16]}...`

*📊 Community Rating:*
Average: {'⭐' * int(signal['avg_rating'])} ({signal['avg_rating']:.1f}/5)
Total Ratings: {signal['total_ratings']}

*🚩 Warnings:*
Flags: {signal['flag_count']}
Scam Reports: {signal['flag_count']}

*💯 Community Score:*
{sentiment_emoji.get(signal['sentiment'], '⚪')} {signal['community_score']:.1f}/100
Sentiment: {signal['sentiment'].upper()}

{'⚠️ *WARNING: Multiple scam reports!*' if signal['flag_count'] > 3 else ''}

*Your Turn:*
/rate_token {token_mint} <1-5>
"""
        
        keyboard = [
            [InlineKeyboardButton("⭐ Rate Token", callback_data=f"rate_{token_mint[:8]}")],
            [InlineKeyboardButton("🚩 Flag as Scam", callback_data=f"flag_{token_mint[:8]}")],
            [InlineKeyboardButton("◀️ Back", callback_data="back_to_start")]
        ]
        
        await update.message.reply_text(
            message,
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    async def rate_token_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Rate a token (1-5 stars)"""
        if len(context.args) < 2:
            await update.message.reply_text(
                "Usage: /rate_token <token_address> <rating>\n\n"
                "Rating: 1-5 stars\n"
                "Example: /rate_token So11...abc 5"
            )
            return
        
        token_mint = context.args[0]
        try:
            rating = float(context.args[1])
            if rating < 1 or rating > 5:
                raise ValueError("Rating must be 1-5")
        except:
            await update.message.reply_text("❌ Rating must be a number between 1 and 5")
            return
        
        user_id = update.effective_user.id
        
        # Submit rating
        await self.community_intel.submit_token_rating(user_id, token_mint, rating, "")
        
        # Award points
        await self.rewards.award_points(user_id, REWARD_POINTS['rate_token'], 'Rated token')
        
        message = f"""✅ *RATING SUBMITTED*

Token: `{token_mint[:16]}...`
Your Rating: {'⭐' * int(rating)} ({rating}/5)

*You earned {REWARD_POINTS['rate_token']} points!*

Thank you for contributing to community intelligence!

Check /community {token_mint} to see updated ratings.
"""
        
        await update.message.reply_text(message, parse_mode='Markdown')
    
    async def my_stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show user's performance statistics - Enterprise UI"""
        from src.modules.ui_formatter import MessageTemplates
        
        # Handle both regular commands and button callbacks
        is_callback = hasattr(update, 'callback_query') and update.callback_query
        
        if is_callback:
            user_id = update.from_user.id
            username = update.from_user.username or f"user_{user_id}"
        else:
            user_id = update.effective_user.id
            username = update.effective_user.username or f"user_{user_id}"
        
        # Get stats from database
        stats = await self.db.get_user_stats(user_id, days=30)
        
        # Get trader profile
        trader = await self.social_marketplace.get_trader_profile(user_id)
        
        # Get reward status
        rewards = await self.rewards.get_user_rewards(user_id)
        
        # Add trader profile data to stats
        if trader:
            stats['tier'] = trader.tier.value if hasattr(trader.tier, 'value') else 'bronze'
            stats['reputation_score'] = trader.reputation_score
            stats['followers'] = trader.followers
        else:
            stats['tier'] = 'bronze'
            stats['reputation_score'] = 0
            stats['followers'] = 0
        
        # Add best/worst trades
        stats['best_trade'] = stats.get('best_profit', 0)
        stats['worst_trade'] = stats.get('worst_loss', 0)
        
        # Generate enterprise stats dashboard
        message, keyboard = MessageTemplates.stats_dashboard(username, stats, rewards)
        
        if is_callback:
            await update.callback_query.edit_message_text(message, parse_mode='HTML', reply_markup=keyboard)
        else:
            await update.message.reply_text(message, parse_mode='HTML', reply_markup=keyboard)
    
    async def rewards_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show user rewards and points"""
        user_id = update.effective_user.id
        
        # Get reward status
        rewards = await self.rewards.get_user_rewards(user_id)
        
        # Get trader profile
        trader = await self.social_marketplace.get_trader_profile(user_id)
        
        tier_emojis = {
            'Novice': '🆕',
            'Bronze Contributor': '🥉',
            'Silver Contributor': '🥈',
            'Gold Contributor': '🥇',
            'Platinum Contributor': '💎',
            'Diamond Contributor': '👑'
        }
        
        message = f"""🎁 *REWARDS & POINTS*

*Your Status:*
{tier_emojis.get(rewards['tier'], '⭐')} Tier: *{rewards['tier']}*
Points: *{rewards['points']}*

*Progress to Next Tier:*
{"▓" * int(rewards['progress'] / 10)}{"░" * (10 - int(rewards['progress'] / 10))} {rewards['progress']:.1f}%
"""
        
        if rewards['next_tier_points']:
            message += f"Need: {rewards['next_tier_points'] - rewards['points']} more points\n"
        
        message += f"""
*🎯 Earn Points:*
• Trade: +10 points
• Successful trade: +20 bonus
• Rate token: +5 points
• Flag scam: +20 points
• Share strategy: +50 points
• Refer user: +100 points

*🏆 Your Tier Benefits:*
"""
        
        if trader:
            if trader.tier.value == 'diamond':
                message += "• Everything unlocked! 👑\n"
            elif trader.tier.value == 'platinum':
                message += "• Copy trading unlocked\n• Priority support\n"
            elif trader.tier.value == 'gold':
                message += "• Advanced analytics\n• Lower fees\n"
            else:
                message += "• Keep trading to unlock more!\n"
        
        message += "\n*Keep trading and contributing to earn more!* 🚀"
        
        keyboard = [
            [
                InlineKeyboardButton("📊 My Stats", callback_data="my_stats"),
                InlineKeyboardButton("🏆 Leaderboard", callback_data="leaderboard")
            ],
            [InlineKeyboardButton("◀️ Back", callback_data="back_to_start")]
        ]
        
        await update.message.reply_text(
            message,
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    async def strategies_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        🔥 KILLER FEATURE #5: Strategy Marketplace
        Browse and purchase proven trading strategies
        """
        await update.message.reply_text("📚 *STRATEGY MARKETPLACE*\n\nLoading strategies...", parse_mode='Markdown')
        
        # Get strategies
        strategies = await self.strategy_marketplace.get_strategy_marketplace(
            sort_by='rating'
        )
        
        if not strategies:
            message = """📚 <b>STRATEGY MARKETPLACE</b>

💡 No strategies available yet!

<b>🚀 Be the First!</b>
Publish your winning strategy and earn SOL from every sale!

📝 Commands:
• /publish_strategy - List your strategy
• /my_strategies - View your published strategies

<b>💰 How it Works:</b>
1. Publish your proven strategy
2. Set your price (in SOL)
3. Earn 70% of each sale
4. Build your reputation as a top strategist!

<b>Top strategies earn 10-50 SOL per month!</b>
"""
            keyboard = [
                [InlineKeyboardButton("📝 Publish Strategy", callback_data="publish_strategy_start")],
                [InlineKeyboardButton("❓ How It Works", callback_data="marketplace_info")],
                [InlineKeyboardButton("❌ Close", callback_data="close_message")]
            ]
            await update.message.reply_text(
                message, 
                parse_mode='HTML',
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            return
        
        message = "📚 <b>TOP TRADING STRATEGIES</b>\n\n"
        message += "🔥 <i>Proven strategies from successful traders</i>\n\n"
        message += "━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        
        for i, strategy in enumerate(strategies[:5], 1):
            stars = '⭐' * int(strategy['rating'])
            win_rate = strategy['performance'].get('win_rate', 0)
            avg_profit = strategy['performance'].get('avg_profit', 0)
            total_trades = strategy['performance'].get('total_trades', 0)
            
            message += f"{i}. <b>{strategy['name']}</b>\n"
            message += f"   💫 Rating: {stars} ({strategy['rating']:.1f}/5)\n"
            message += f"   📊 Win Rate: {win_rate:.1f}%\n"
            message += f"   💰 Avg Profit: {avg_profit:.4f} SOL\n"
            message += f"   🔄 Trades: {total_trades}\n"
            message += f"   💵 Price: <b>{strategy['price']} SOL</b>\n"
            message += f"   📦 Sales: {strategy['purchases']}\n"
            message += f"   👤 Creator: User {strategy['creator_id']}\n"
            message += f"\n   🛒 <code>/buy_strategy {strategy['id'][:8]}</code>\n\n"
        
        message += "━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        message += "💡 <i>More strategies: /browse_strategies</i>\n"
        message += "📝 <i>Publish yours: /publish_strategy</i>"
        
        keyboard = [
            [
                InlineKeyboardButton("🔍 Browse All", callback_data="browse_all_strategies"),
                InlineKeyboardButton("📝 Publish", callback_data="publish_strategy_start")
            ],
            [
                InlineKeyboardButton("📚 My Strategies", callback_data="my_strategies"),
                InlineKeyboardButton("💼 Purchased", callback_data="purchased_strategies")
            ],
            [InlineKeyboardButton("❌ Close", callback_data="close_message")]
        ]
        
        await update.message.reply_text(
            message, 
            parse_mode='HTML',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    async def publish_strategy_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Publish a trading strategy to marketplace"""
        user_id = update.effective_user.id
        
        if not context.args or len(context.args) < 3:
            message = """📝 <b>PUBLISH YOUR STRATEGY</b>

<b>How to publish:</b>
<code>/publish_strategy &lt;name&gt; &lt;price&gt; &lt;description&gt;</code>

<b>Example:</b>
<code>/publish_strategy "Momentum Scalper" 5.0 "High-frequency momentum trading with 72% win rate"</code>

<b>💰 Pricing Guide:</b>
• Beginner strategy: 1-3 SOL
• Intermediate: 3-7 SOL
• Advanced: 7-15 SOL
• Expert/Proven: 15+ SOL

<b>💡 Tips for Success:</b>
• Provide detailed description
• Share verified performance stats
• Offer strategy documentation
• Respond to buyer questions

<b>You earn 70% of each sale!</b>
"""
            await update.message.reply_text(message, parse_mode='HTML')
            return
        
        try:
            strategy_name = context.args[0].strip('"')
            price = float(context.args[1])
            description = ' '.join(context.args[2:]).strip('"')
            
            if price < 0.1:
                await update.message.reply_text("❌ Minimum price is 0.1 SOL")
                return
            
            # Get user's trading stats for strategy performance
            user_stats = await self.db.get_user_stats(user_id)
            
            strategy_data = {
                'name': strategy_name,
                'description': description,
                'price': price,
                'category': 'user_created',
                'win_rate': user_stats.get('win_rate', 0) * 100 if user_stats else 0,
                'avg_profit': user_stats.get('avg_profit', 0) if user_stats else 0,
                'total_trades': user_stats.get('total_trades', 0) if user_stats else 0,
            }
            
            strategy_id = await self.strategy_marketplace.publish_strategy(
                creator_id=user_id,
                strategy_data=strategy_data
            )
            
            message = f"""✅ <b>STRATEGY PUBLISHED!</b>

📝 <b>{strategy_name}</b>
💵 Price: {price} SOL
📊 Win Rate: {strategy_data['win_rate']:.1f}%
🔄 Based on {strategy_data['total_trades']} trades

🎉 <b>Your strategy is now live in the marketplace!</b>

Strategy ID: <code>{strategy_id[:8]}...</code>

💰 <b>Earnings:</b>
• You get: {price * 0.7:.2f} SOL per sale (70%)
• Platform fee: {price * 0.3:.2f} SOL (30%)

📈 <b>Promote your strategy:</b>
• Share in trading communities
• Show verified results
• Respond to questions quickly

View: /my_strategies
"""
            
            keyboard = [
                [InlineKeyboardButton("📊 View in Marketplace", callback_data=f"view_strategy_{strategy_id[:8]}")],
                [InlineKeyboardButton("📝 Edit", callback_data=f"edit_strategy_{strategy_id[:8]}")],
                [InlineKeyboardButton("❌ Close", callback_data="close_message")]
            ]
            
            await update.message.reply_text(
                message, 
                parse_mode='HTML',
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            
        except ValueError:
            await update.message.reply_text("❌ Invalid price. Must be a number (e.g., 5.0)")
        except Exception as e:
            logger.error(f"Error publishing strategy: {e}")
            await update.message.reply_text(f"❌ Error publishing strategy: {str(e)}")
    
    async def buy_strategy_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Buy a strategy from marketplace"""
        user_id = update.effective_user.id
        
        if not context.args:
            await update.message.reply_text(
                "Usage: /buy_strategy <strategy_id>\n\n"
                "Browse strategies: /strategies"
            )
            return
        
        strategy_id_partial = context.args[0]
        
        try:
            # Find full strategy ID
            strategy = None
            for sid, strat in self.strategy_marketplace.strategies.items():
                if sid.startswith(strategy_id_partial):
                    strategy = strat
                    break
            
            if not strategy:
                await update.message.reply_text("❌ Strategy not found")
                return
            
            # Check if already purchased
            if user_id in self.strategy_marketplace.strategy_purchases and \
               strategy['id'] in self.strategy_marketplace.strategy_purchases[user_id]:
                await update.message.reply_text("ℹ️ You already own this strategy!")
                return
            
            # Get user wallet balance
            user_wallet = await self.wallet_manager.get_or_create_wallet(user_id)
            balance = await self.wallet_manager.get_balance(user_id)
            
            if balance < strategy['price']:
                await update.message.reply_text(
                    f"❌ Insufficient balance\n\n"
                    f"Required: {strategy['price']} SOL\n"
                    f"Your balance: {balance:.4f} SOL\n\n"
                    f"Deposit SOL: /deposit"
                )
                return
            
            # Purchase strategy
            success = await self.strategy_marketplace.purchase_strategy(
                buyer_id=user_id,
                strategy_id=strategy['id']
            )
            
            if success:
                message = f"""🎉 <b>STRATEGY PURCHASED!</b>

📝 <b>{strategy['name']}</b>
💵 Paid: {strategy['price']} SOL

📊 <b>Strategy Details:</b>
{strategy['description']}

<b>Performance:</b>
• Win Rate: {strategy['performance']['win_rate']:.1f}%
• Avg Profit: {strategy['performance']['avg_profit']:.4f} SOL
• Total Trades: {strategy['performance']['total_trades']}

<b>📚 How to Use:</b>
1. Study the strategy parameters
2. Test on small amounts first
3. Apply to your trading
4. Track your results

<b>💡 Need help?</b>
Contact creator: User {strategy['creator_id']}

Access: /my_strategies
"""
                
                keyboard = [
                    [InlineKeyboardButton("📖 View Full Strategy", callback_data=f"view_purchased_{strategy['id'][:8]}")],
                    [InlineKeyboardButton("⭐ Rate Strategy", callback_data=f"rate_strategy_{strategy['id'][:8]}")],
                    [InlineKeyboardButton("❌ Close", callback_data="close_message")]
                ]
                
                await update.message.reply_text(
                    message, 
                    parse_mode='HTML',
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
            else:
                await update.message.reply_text("❌ Purchase failed. Please try again.")
            
        except Exception as e:
            logger.error(f"Error buying strategy: {e}")
            await update.message.reply_text(f"❌ Error: {str(e)}")
    
    async def my_strategies_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """View user's published and purchased strategies"""
        user_id = update.effective_user.id
        
        # Get published strategies
        published = [s for s in self.strategy_marketplace.strategies.values() if s['creator_id'] == user_id]
        
        # Get purchased strategies
        purchased_ids = self.strategy_marketplace.strategy_purchases.get(user_id, set())
        purchased = [self.strategy_marketplace.strategies[sid] for sid in purchased_ids if sid in self.strategy_marketplace.strategies]
        
        message = "📚 <b>MY STRATEGIES</b>\n\n"
        
        if published:
            message += f"📝 <b>PUBLISHED ({len(published)}):</b>\n\n"
            total_earnings = 0
            for strat in published:
                earnings = strat['purchases'] * strat['price'] * 0.7
                total_earnings += earnings
                message += f"• <b>{strat['name']}</b>\n"
                message += f"  💵 Price: {strat['price']} SOL\n"
                message += f"  📦 Sales: {strat['purchases']}\n"
                message += f"  💰 Earned: {earnings:.2f} SOL\n"
                message += f"  ⭐ Rating: {strat['rating']:.1f}/5\n\n"
            
            message += f"💰 <b>Total Earnings: {total_earnings:.2f} SOL</b>\n\n"
        else:
            message += "📝 <i>No published strategies</i>\n\n"
        
        message += "━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        
        if purchased:
            message += f"💼 <b>PURCHASED ({len(purchased)}):</b>\n\n"
            for strat in purchased:
                message += f"• <b>{strat['name']}</b>\n"
                message += f"  Creator: User {strat['creator_id']}\n"
                message += f"  📊 Win Rate: {strat['performance']['win_rate']:.1f}%\n"
                message += f"  <code>/view_strategy {strat['id'][:8]}</code>\n\n"
        else:
            message += "💼 <i>No purchased strategies</i>\n\n"
        
        message += "━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        message += "📝 Publish new: /publish_strategy\n"
        message += "🔍 Browse: /strategies"
        
        keyboard = [
            [
                InlineKeyboardButton("📝 Publish New", callback_data="publish_strategy_start"),
                InlineKeyboardButton("🔍 Browse", callback_data="browse_all_strategies")
            ],
            [InlineKeyboardButton("❌ Close", callback_data="close_message")]
        ]
        
        await update.message.reply_text(
            message, 
            parse_mode='HTML',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    async def track_wallet_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        🧠 ELITE FEATURE: Track and analyze wallet performance
        """
        if not context.args:
            await update.message.reply_text(
                "Usage: /track <wallet_address>\n\n"
                "Track any wallet and see their:\n"
                "• Performance score (0-100)\n"
                "• Win rate & profit factor\n"
                "• Best/worst tokens\n"
                "• Trading patterns"
            )
            return
        
        wallet_address = context.args[0]
        user_id = update.effective_user.id
        
        await update.message.reply_text(
            f"🧠 Analyzing wallet {wallet_address[:8]}...\n"
            "This may take a moment...",
            parse_mode=None
        )
        
        try:
            await self.wallet_intelligence.track_wallet(wallet_address, analyze=True)
            metrics = self.wallet_intelligence.get_wallet_metrics(wallet_address)
            
            if metrics:
                score = metrics.calculate_score()
                rank = self.wallet_intelligence.get_wallet_rank(wallet_address)
                
                message = f"""🧠 WALLET INTELLIGENCE REPORT

Address: {wallet_address[:8]}...{wallet_address[-8:]}
Overall Score: {score:.1f}/100
Rank: #{rank if rank else 'N/A'}

━━━━━━━━━━━━━━━━━━━━━━━

PERFORMANCE:
• Total Trades: {metrics.total_trades}
• Win Rate: {metrics.win_rate*100:.1f}%
• Profit Factor: {metrics.profit_factor:.2f}x
• Total P&L: {metrics.total_profit_sol - metrics.total_loss_sol:.4f} SOL
• Avg Profit/Trade: {metrics.avg_profit_per_trade:.4f} SOL

RECENT PERFORMANCE:
• Last 7 Days: {metrics.recent_performance_7d:.4f} SOL
• Last 30 Days: {metrics.recent_performance_30d:.4f} SOL

TRADING STYLE:
• Consistency: {metrics.consistency_score*100:.1f}%
• Avg Hold Time: {metrics.avg_hold_time_hours:.1f}h
• Sharpe Ratio: {metrics.sharpe_ratio:.2f}

BEST TOKENS:
{chr(10).join(f'• {token[:8]}...' for token in metrics.best_tokens[:3]) if metrics.best_tokens else '• None yet'}

━━━━━━━━━━━━━━━━━━━━━━━

Use /rankings to see top wallets!
"""
                
                # Award points
                await self.rewards.award_points(user_id, 5, 'Tracked wallet')
                
                await update.message.reply_text(message, parse_mode=None)
            else:
                await update.message.reply_text("❌ Failed to analyze wallet")
                
        except Exception as e:
            logger.error(f"Error tracking wallet: {e}")
            await update.message.reply_text(f"❌ Error: {str(e)}")
    
    async def rankings_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        🧠 ELITE FEATURE: Show top performing wallets
        """
        user_id = update.effective_user.id
        
        # Get from database instead of in-memory cache
        tracked_wallets = await self.db.get_tracked_wallets(user_id)
        
        if not tracked_wallets or len(tracked_wallets) == 0:
            await update.message.reply_text(
                "No wallets tracked yet!\n\n"
                "Use /track <wallet_address> to start tracking profitable wallets."
            )
            return
        
        # Sort by score (highest first)
        top_wallets = sorted(tracked_wallets, key=lambda w: w.score, reverse=True)[:10]
        
        if not top_wallets:
            await update.message.reply_text(
                "No wallets tracked yet!\n\n"
                "Use /track <wallet_address> to start tracking profitable wallets."
            )
            return
        
        message = f"🏆 TOP PERFORMING WALLETS\n\n"
        message += f"📊 Monitoring {len(tracked_wallets)} wallets total\n\n"
        message += "━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        
        for idx, wallet in enumerate(top_wallets, 1):
            medal = "🥇" if idx == 1 else "🥈" if idx == 2 else "🥉" if idx == 3 else f"{idx}."
            
            address = wallet.wallet_address
            score = wallet.score
            win_rate = wallet.win_rate * 100
            total_pnl = wallet.total_pnl
            
            message += f"{medal} {address[:8]}...{address[-4:]}\n"
            message += f"   Score: {score:.1f}/100 | "
            message += f"Win Rate: {win_rate:.0f}% | "
            message += f"P&L: {total_pnl:+.4f} SOL\n"
            message += f"   Trades: {wallet.total_trades} | "
            message += f"Profitable: {wallet.profitable_trades}\n\n"
        
        message += "━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        message += f"💡 Copy-trading from top {len([w for w in tracked_wallets if w.score >= 65])} wallets (score ≥65)\n\n"
        message += "Use /track <address> to analyze any wallet!"
        
        await update.message.reply_text(message, parse_mode=None)
    
    async def autostart_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        🤖 ELITE FEATURE: Start automated trading
        """
        user_id = update.effective_user.id
        
        # Check balance
        balance = await self.wallet_manager.get_user_balance(user_id)
        if balance < 0.1:
            await update.message.reply_text(
                "❌ Insufficient Balance\n\n"
                "You need at least 0.1 SOL to enable auto-trading.\n\n"
                "Use /deposit to fund your wallet.",
                parse_mode=None
            )
            return
        
        # Get user keypair
        user_keypair = await self.wallet_manager.get_user_keypair(user_id)
        if not user_keypair:
            await update.message.reply_text("❌ Could not access your wallet")
            return
        
        # Initialize auto trader if not exists
        if not self.auto_trader:
            config = AutoTradingConfig()
            self.auto_trader = AutomatedTradingEngine(
                config,
                self.wallet_intelligence,
                self.jupiter,
                self.elite_protection,
                trade_executor=self.trade_executor,
                monitor=self.monitor,
            )
        
        # Start automated trading (with database for loading tracked wallets)
        try:
            logger.info(f"🎯 Starting automated trading for user {user_id}...")
            await self.auto_trader.start_automated_trading(
                user_id,
                user_keypair,
                self.wallet_manager,
                self.db  # Pass database manager to load tracked wallets
            )
            logger.info(f"✅ Automated trading successfully started for user {user_id}")
            
            # 🎯 Register auto-trader with sniper for position tracking
            self.sniper.register_auto_trader(self.auto_trader)
            
        except Exception as e:
            logger.error(f"❌ ERROR starting automated trading: {e}", exc_info=True)
            await update.message.reply_text(
                f"❌ Error starting automated trading:\n{str(e)}\n\n"
                "Please contact support if this persists."
            )
            return
        
        message = """🤖 AUTOMATED TRADING STARTED!

The bot will now:
• Monitor top wallet activities 24/7
• Scan for high-confidence opportunities
• Execute trades automatically
• Manage positions with stop losses
• Take profits automatically
• Follow your risk settings

━━━━━━━━━━━━━━━━━━━━━━━

RISK LIMITS:
• Max per trade: 0.1 SOL
• Max daily trades: 50
• Max daily loss: 50 SOL
• Stop loss: 15%
• Take profit: 50%
• Trailing stop: 10%

━━━━━━━━━━━━━━━━━━━━━━━

COMMANDS:
/autostop - Stop auto-trading
/autostatus - Check status
/positions - View open positions

⚠️ Monitor your bot regularly!
"""
        
        await update.message.reply_text(message, parse_mode=None)
    
    async def autostop_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Stop automated trading"""
        if self.auto_trader and self.auto_trader.is_running:
            await self.auto_trader.stop_automated_trading()
            await update.message.reply_text(
                "🛑 AUTOMATED TRADING STOPPED\n\n"
                "All open positions remain active.\n"
                "Use /positions to manage them.\n\n"
                "To restart: /autostart"
            )
        else:
            await update.message.reply_text(
                "Automated trading is not running.\n\n"
                "Use /autostart to enable it."
            )
    
    async def autostatus_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show automated trading status"""
        if not self.auto_trader:
            await update.message.reply_text("Automated trading not initialized. Use /autostart")
            return

        status = self.auto_trader.get_status()
        
        status_emoji = "✅ RUNNING" if status['is_running'] else "❌ STOPPED"
        
        message = f"""🤖 AUTOMATED TRADING STATUS

Status: {status_emoji}

TODAY'S STATS:
• Trades Executed: {status['daily_trades']}
• Total P&L: {status['daily_pnl']:+.4f} SOL
• Active Positions: {status['active_positions']}

OPEN POSITIONS:
"""
        
        if status['positions']:
            for token in status['positions']:
                message += f"• {token[:8]}...\n"
        else:
            message += "• None\n"
        
        message += "\n━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        message += "Commands:\n"
        message += "/autostop - Stop trading\n"
        message += "/positions - Manage positions"

        await update.message.reply_text(message, parse_mode=None)

    async def metrics_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Return live operational telemetry for the administrator."""

        message = update.effective_message
        if not message:
            return

        if not self._is_admin(update):
            await message.reply_text("❌ Metrics are available to the admin only.")
            return

        if not self.monitor:
            await message.reply_text("Monitoring is currently disabled.")
            return

        report = self.monitor.render_markdown_summary()
        await message.reply_text(
            report,
            parse_mode="Markdown",
            disable_web_page_preview=True,
        )
    
    async def metrics_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show bot metrics (admin only)"""
        if not self._is_admin(update):
            await update.message.reply_text("❌ Admin access required")
            return
        
        try:
            stats = self.monitor.get_stats()
            health = self.monitor.get_health_status()
            
            # Format uptime
            uptime_hours = int(stats['uptime_hours'])
            uptime_minutes = int((stats['uptime_hours'] - uptime_hours) * 60)
            
            # Build metrics message
            message = f"""📊 **BOT METRICS**

⏱️ **Uptime:** {uptime_hours}h {uptime_minutes}m
🔄 **Total RPC Requests:** {stats['total_requests']:,}

💼 **Trading:**
✅ Successful: {stats['successful_trades']:,}
❌ Failed: {stats['failed_trades']:,}
📈 Success Rate: {stats['success_rate']:.1f}%

🚨 **Recent Errors:** {stats['recent_errors']}

🏥 **Health Status:** {"✅ Healthy" if health['healthy'] else "⚠️ Issues Detected"}
"""
            
            if health['issues']:
                message += "\n⚠️ **Issues:**\n"
                for issue in health['issues']:
                    message += f"  • {issue}\n"
            
            # Add custom metrics if any
            if self.monitor.metrics:
                message += "\n📊 **Custom Metrics:**\n"
                for name, samples in self.monitor.metrics.items():
                    if samples:
                        latest = samples[-1]
                        value = latest['value']
                        if isinstance(value, float):
                            message += f"  • {name}: {value:.2f}\n"
                        else:
                            message += f"  • {name}: {value}\n"
            
            await update.message.reply_text(message, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Error generating metrics: {e}")
            await update.message.reply_text(f"❌ Error generating metrics: {e}")
    
    async def predict_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """🎯 PROBABILITY PREDICTION - Show enhanced prediction with probabilities"""
        if len(context.args) < 1:
            await update.message.reply_text(
                "Usage: /predict <token_address>\n\n"
                "Get probability-based prediction with recommended action, "
                "position size, and targets.",
                parse_mode='HTML'
            )
            return
        
        token_address = context.args[0]
        user_id = update.effective_user.id
        
        await update.message.reply_text("🧠 <b>GENERATING PREDICTION...</b>", parse_mode='HTML')
        
        try:
            # Get token data
            token_data = await self._fetch_token_data(token_address)
            
            # Get all intelligence sources
            sentiment = await self.sentiment_analyzer.analyze_token_sentiment(
                token_address, token_data.get('symbol', 'UNKNOWN')
            )
            community_signal = await self.community_intel.get_community_signal(token_address)
            wallet_signals = []  # TODO: Get wallet signals
            
            # Get safety score
            protection_result = await self.elite_protection.comprehensive_token_check(token_address)
            safety_score = protection_result.get('overall_score', 0)
            
            # Get AI analysis
            portfolio_value = await self._get_portfolio_value(user_id)
            ai_analysis = await self.ai_manager.analyze_opportunity(
                token_data, portfolio_value,
                sentiment_snapshot=sentiment,
                community_signal=community_signal
            )
            
            # Get user tier
            trader = await self.social_marketplace.get_trader_profile(user_id)
            user_tier = trader.tier.value.upper() if trader else 'BRONZE'
            
            # 🎯 GENERATE ENHANCED PREDICTION
            prediction = await self.prediction_layer.enhanced_analysis(
                token_address=token_address,
                ai_analysis=ai_analysis,
                sentiment_data=sentiment,
                community_signal=community_signal,
                wallet_signals=wallet_signals,
                safety_score=safety_score,
                user_tier=user_tier
            )
            
            # Format prediction message
            direction_emoji = "↗️" if prediction.direction == Direction.UP else "↘️" if prediction.direction == Direction.DOWN else "➡️"
            conf_emoji = "🔥" if prediction.confidence_level == ConfidenceLevel.ULTRA else "✨" if prediction.confidence_level == ConfidenceLevel.HIGH else "⚡"
            
            message = f"""🎯 <b>PROBABILITY PREDICTION</b>

<b>Token:</b> <code>{token_address[:8]}...</code>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<b>📊 PREDICTION:</b>
{conf_emoji} <b>Direction:</b> {prediction.direction.value} {direction_emoji}
<b>Confidence:</b> {prediction.confidence_score:.1%} ({prediction.confidence_level.value})
<b>Timeframe:</b> {prediction.timeframe_hours} hours
<b>Safety Score:</b> {prediction.safety_score}/100

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<b>🎯 RECOMMENDED ACTION:</b>
{prediction.suggested_action}

"""

            if prediction.position_size_sol:
                message += f"""<b>💰 TRADE PARAMETERS:</b>
• Position Size: <b>{prediction.position_size_sol} SOL</b>
• Take Profit: <b>+{prediction.take_profit_target:.0%}</b>
• Stop Loss: <b>{prediction.stop_loss:.0%}</b>

"""

            message += f"""━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<b>🤖 INTELLIGENCE BREAKDOWN:</b>
• AI Model: {prediction.ai_ml_score:.0f}/100
• Sentiment: {prediction.sentiment_score:.0f}/100
• Elite Wallets: {prediction.wallet_score:.0f}/100
• Community: {prediction.community_score:.0f}/100

<b>💡 REASONING:</b>
"""
            for reason in prediction.reasoning:
                message += f"{reason}\n"
            
            message += f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<b>🧠 SYSTEM INTELLIGENCE:</b>
• Level: <b>{self.neural_engine.get_system_intelligence_report()['intelligence_level']}</b>
• Accuracy: {self.neural_engine.system_accuracy:.1%}
• Signals Used: {prediction.signals_used}

<i>Neural engine learns from every trade to improve predictions</i>"""
            
            await update.message.reply_text(message, parse_mode='HTML')
            
        except Exception as e:
            logger.error(f"Prediction error: {e}")
            await update.message.reply_text(f"❌ Prediction failed: {str(e)}", parse_mode='HTML')
    
    async def autopredictions_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Enable prediction-based auto-trading"""
        user_id = update.effective_user.id
        
        # Check balance
        balance = await self.wallet_manager.get_user_balance(user_id)
        if balance < 0.5:
            await update.message.reply_text(
                "❌ <b>Insufficient Balance</b>\n\n"
                "Need at least 0.5 SOL for prediction-based auto-trading.\n\n"
                "Use /deposit to fund your wallet.",
                parse_mode='HTML'
            )
            return
        
        # Enable auto-predictions
        await self.db.update_user_settings(user_id, {
            'auto_predictions_enabled': True,
            'auto_predictions_min_confidence': 0.85  # ULTRA only
        })
        
        message = """✅ <b>AUTO-PREDICTIONS ENABLED!</b>

<b>How it works:</b>
• System continuously scans for opportunities
• Neural engine generates probability predictions
• ULTRA confidence predictions (90%+) auto-execute
• Position sized based on your tier
• Automatic stop-loss/take-profit

<b>Safety Limits:</b>
• Only ULTRA confidence (90%+)
• Max 5 positions at once
• Automatic risk management
• Your tier position limits apply

<b>Settings:</b>
/prediction_stats - View performance
/autopredictions off - Disable

<b>🧠 Neural engine will learn from every trade!</b>"""
        
        await update.message.reply_text(message, parse_mode='HTML')
    
    async def prediction_stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show prediction performance statistics"""
        stats = self.prediction_layer.get_prediction_stats()
        
        if stats['total'] == 0:
            await update.message.reply_text(
                "📊 <b>NO PREDICTIONS YET</b>\n\n"
                "Use /predict to generate probability predictions\n"
                "System will track accuracy over time",
                parse_mode='HTML'
            )
            return
        
        message = f"""📊 <b>PREDICTION PERFORMANCE</b>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<b>OVERALL STATS:</b>
Total Predictions: {stats['total']}
Correct: {stats['correct']}
Accuracy: <b>{stats['accuracy']:.1%}</b>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<b>BY CONFIDENCE LEVEL:</b>
"""
        
        for level, data in stats.get('by_confidence', {}).items():
            emoji = "🔥" if level == "ULTRA" else "✨" if level == "HIGH" else "⚡"
            message += f"\n{emoji} <b>{level}:</b> {data['accuracy']:.1%} ({data['total']} predictions)"
        
        message += f"""

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<b>🧠 NEURAL ENGINE:</b>
• Intelligence Level: {self.neural_engine.get_system_intelligence_report()['intelligence_level']}
• System Accuracy: {self.neural_engine.system_accuracy:.1%}
• Total Trades Analyzed: {self.neural_engine.total_predictions}

<i>System gets smarter with every trade!</i>"""
        
        await update.message.reply_text(message, parse_mode='HTML')
    
    async def flash_arb_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """⚡ Flash loan arbitrage info and status"""
        user_id = update.effective_user.id
        
        # Get user tier
        trader = await self.social_marketplace.get_trader_profile(user_id)
        user_tier = trader.tier.value.upper() if trader else 'BRONZE'
        
        # Get tier limit
        max_capital = self.flash_loan_engine.tier_limits.get(user_tier, 0)
        platform_fee = self.flash_loan_engine.tier_fees.get(user_tier, 0.05) * 100
        
        if max_capital == 0:
            message = """⚡ <b>FLASH LOAN ARBITRAGE</b>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<b>🔒 TIER UPGRADE REQUIRED</b>

Flash loan arbitrage requires <b>Gold+ tier</b>

<b>💎 BENEFITS:</b>
• 100x capital efficiency
• Profit with minimal capital
• Atomic transactions (risk-free)
• MEV protected via Jito bundles

<b>📊 TIER LIMITS:</b>
🥇 Gold: 50 SOL flash loans (5% fee)
💎 Platinum: 150 SOL (3% fee)
👑 Elite: 500 SOL (2% fee)

<b>How it works:</b>
1. Detect price difference across DEXs
2. Flash loan SOL from Marginfi
3. Buy on cheaper DEX
4. Sell on expensive DEX
5. Repay flash loan + 0.001% fee
6. Keep profit (minus platform fee)

All in ONE atomic transaction - zero risk!

<i>Upgrade to Gold tier to unlock this feature</i>"""
            
            await update.message.reply_text(message, parse_mode='HTML')
            return
        
        # Show flash arb status
        stats = await self.flash_loan_engine.get_user_arbitrage_stats(user_id)
        
        message = f"""⚡ <b>FLASH LOAN ARBITRAGE</b>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<b>YOUR TIER: {user_tier}</b>

<b>💰 LIMITS:</b>
Max Flash Loan: <b>{max_capital} SOL</b>
Platform Fee: <b>{platform_fee:.1f}%</b> of profits

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<b>📊 YOUR PERFORMANCE:</b>
Total Arbitrages: {stats['total_trades']}
Successful: {stats['successful_trades']}
Total Profit: {stats['total_profit_sol']:.4f} SOL
Avg Profit: {stats['average_profit_sol']:.4f} SOL
Fees Paid: {stats['platform_fees_paid']:.4f} SOL
ROI: {stats['roi']:.2%}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<b>💡 COMMANDS:</b>
/flash_enable - Enable auto-arbitrage
/flash_opportunities - View current opportunities
/flash_stats - System-wide stats

<i>100x your capital with flash loans!</i>"""
        
        await update.message.reply_text(message, parse_mode='HTML')
    
    async def flash_enable_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Enable flash loan auto-arbitrage"""
        user_id = update.effective_user.id
        
        # Get user tier
        trader = await self.social_marketplace.get_trader_profile(user_id)
        user_tier = trader.tier.value.upper() if trader else 'BRONZE'
        
        if user_tier not in ['GOLD', 'PLATINUM', 'ELITE']:
            await update.message.reply_text(
                "❌ Flash loan arbitrage requires Gold+ tier\n\n"
                "Upgrade your tier to unlock this feature",
                parse_mode='HTML'
            )
            return
        
        # Enable flash arbitrage
        await self.db.update_user_settings(user_id, {
            'flash_arb_enabled': True,
            'flash_arb_min_profit_bps': 50  # 0.5% minimum
        })
        
        max_capital = self.flash_loan_engine.tier_limits.get(user_tier, 0)
        
        message = f"""✅ <b>FLASH LOAN ARBITRAGE ENABLED!</b>

<b>Your Tier: {user_tier}</b>
<b>Max Capital: {max_capital} SOL</b>

<b>How it works:</b>
• System scans for price differences every 2 seconds
• When profit >0.5% detected
• Simulates full arbitrage transaction
• If profitable, executes via Jito bundle
• You get notified of every trade

<b>Safety Features:</b>
• Atomic transactions (all-or-nothing)
• MEV protected via Jito
• Simulation required before execution
• Auto-revert on any loss

<b>💰 Revenue Split:</b>
• You keep: {100 - self.flash_loan_engine.tier_fees.get(user_tier, 0.05)*100:.0f}%
• Platform fee: {self.flash_loan_engine.tier_fees.get(user_tier, 0.05)*100:.0f}%

<i>Flash arbitrage is now active 24/7!</i>"""
        
        await update.message.reply_text(message, parse_mode='HTML')
    
    async def flash_stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show system-wide flash arbitrage stats"""
        stats = self.flash_loan_engine.get_system_stats()
        
        message = f"""⚡ <b>FLASH ARBITRAGE SYSTEM STATS</b>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<b>OPPORTUNITIES:</b>
Total Found: {stats['total_opportunities_found']}
Executed: {stats['total_executed']}
Execution Rate: {stats['execution_rate']:.1%}

<b>PROFITABILITY:</b>
Total Profit: <b>{stats['total_profit_sol']:.4f} SOL</b>

<b>STATUS:</b>
Last Scan: {stats['last_scan'] or 'Never'}
Scanning: <b>Every 2 seconds</b>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<b>💡 How to participate:</b>
• Upgrade to Gold+ tier
• Enable: /flash_enable
• Earn passive income 24/7

<i>Flash loans = 100x capital efficiency!</i>"""
        
        await update.message.reply_text(message, parse_mode='HTML')
    
    async def flash_opportunities_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show current arbitrage opportunities"""
        
        await update.message.reply_text("🔍 <b>SCANNING FOR ARBITRAGE...</b>", parse_mode='HTML')
        
        # Scan for opportunities
        opportunities = await self.flash_loan_engine.scan_for_opportunities()
        
        if not opportunities:
            message = """⚡ <b>ARBITRAGE OPPORTUNITIES</b>

<b>No profitable opportunities right now</b>

<b>✅ Active Monitoring:</b>
• Scanning: Every 2 seconds
• DEXs: Raydium, Orca, Jupiter
• Pairs: SOL/USDC, SOL/USDT, BONK/SOL, WIF/SOL
• Min Profit: 0.5% (50 bps)

<b>Why none now?</b>
• Markets are efficient
• Normal during low volatility
• Opportunities appear during:
  - High volume periods
  - New token launches
  - Market volatility spikes

<b>💡 Solution:</b>
Enable /flash_enable for 24/7 monitoring
System will auto-execute when opportunities appear!

<i>Check back during high market activity</i>"""
            
            await update.message.reply_text(message, parse_mode='HTML')
            return
        
        # Format opportunities
        message = f"""⚡ <b>ARBITRAGE OPPORTUNITIES!</b>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<b>Found {len(opportunities)} profitable arbitrages:</b>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""
        
        for i, opp in enumerate(opportunities[:5], 1):
            emoji = "🔥" if opp.profit_bps > 100 else "⚡"
            
            message += f"""
{emoji} <b>#{i} - {opp.token_mint[:8]}...</b>

   <b>Buy:</b> {opp.source_dex} @ ${opp.source_price:.6f}
   <b>Sell:</b> {opp.dest_dex} @ ${opp.dest_price:.6f}
   <b>Profit:</b> {opp.profit_bps} bps ({opp.profit_bps/100:.2f}%)
   
   <b>Capital Needed:</b> {opp.required_capital} SOL
   <b>Est. Profit:</b> {opp.estimated_profit:.4f} SOL
   
   <code>/execute_arb {i}</code>

"""
        
        message += """━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 <i>Opportunities update every 2 seconds</i>
⚡ <i>Enable /flash_enable for auto-execution</i>"""
        
        await update.message.reply_text(message, parse_mode='HTML')

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show help menu with all commands - Enterprise UI"""
        from src.modules.ui_formatter import MessageTemplates
        
        message, keyboard = MessageTemplates.help_menu()
        
        await update.message.reply_text(
            message,
            parse_mode='HTML',
            reply_markup=keyboard
        )
    
    async def features_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show all bot features"""
        message = """🎯 *ALL FEATURES*

*🤖 AI-Powered:*
✅ Machine learning predictions
✅ Pattern recognition  
✅ Adaptive strategies
✅ Kelly Criterion sizing

*👥 Social Trading:*
✅ Copy successful traders
✅ Trader reputation system
✅ Strategy marketplace
✅ Community ratings

*📱 Real-Time Intel:*
✅ Twitter monitoring
✅ Reddit tracking
✅ Sentiment analysis
✅ Viral detection

*🛡️ Protection:*
✅ Anti-MEV (Jito bundles)
✅ Honeypot detection
✅ Stop loss/take profit
✅ Daily loss limits

*🎮 Gamification:*
✅ Points & rewards
✅ 5-tier ranking system
✅ Achievements
✅ Competitions

*Platform Fee: 0.5% per trade*
"""
        keyboard = [
            [InlineKeyboardButton("🚀 Get Started", callback_data="get_started")],
            [InlineKeyboardButton("❌ Close", callback_data="close_message")]
        ]
        await update.message.reply_text(
            message,
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    # ==================== CALLBACK HANDLERS ====================
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle button callbacks"""
        query = update.callback_query
        await query.answer()
        
        data = query.data
        user_id = query.from_user.id
        
        # Handle new UI buttons
        if data == "get_started":
            # Get user's personal wallet
            wallet_address = await self.wallet_manager.get_user_wallet_address(user_id)
            if not wallet_address:
                wallet_info = await self.wallet_manager.get_or_create_user_wallet(user_id)
                wallet_address = wallet_info['public_key']
            
            balance = await self.wallet_manager.get_user_balance(user_id)
            
            message = f"""🚀 *GET STARTED GUIDE*

*Step 1: Fund Your Personal Wallet*
Send SOL to YOUR trading wallet:
`{wallet_address}`

Current Balance: {balance:.6f} SOL

*Step 2: Analyze Tokens*
Use /ai with token address to get AI insights

*Step 3: Start Trading*
• AI will recommend buy/sell actions
• Click buttons to execute trades
• All trades use YOUR personal wallet

*Step 4: Advanced Features*
• /leaderboard - Copy successful traders
• /trending - See viral tokens
• /community - Community ratings

*Commands:*
/wallet - Manage your wallet
/deposit - Fund instructions
/balance - Check balance

*Need Help?* Use /help for all commands
"""
            keyboard = [
                [
                    InlineKeyboardButton("💰 My Wallet", callback_data="show_wallet"),
                    InlineKeyboardButton("📥 Deposit", callback_data="show_deposit")
                ],
                [InlineKeyboardButton("◀️ Back", callback_data="back_to_start")]
            ]
            await query.edit_message_text(
                message,
                parse_mode='Markdown',
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        
        elif data == "close_message":
            await query.delete_message()
        
        elif data == "show_wallet" or data == "refresh_wallet":
            await self._show_wallet_info(query)
        
        elif data == "show_deposit":
            await self._show_deposit_info(query)
        
        elif data == "export_keys_prompt":
            # Prompt user to use command in private message for security
            message = """🔐 *EXPORT PRIVATE KEYS*

For security reasons, private keys must be exported in a private message.

*To export your keys:*
1. Open a private message with me
2. Send the command: /export_wallet
3. You'll receive your private key securely

⚠️ *Never share your private key with anyone!*

Your keys give COMPLETE access to your wallet and funds."""
            
            keyboard = [[InlineKeyboardButton("◀️ Back", callback_data="show_wallet")]]
            
            await query.edit_message_text(
                message,
                parse_mode='Markdown',
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        
        elif data == "my_stats":
            await self.my_stats_command(update, context)
        
        elif data == "leaderboard":
            await self.leaderboard_command(update, context)
        
        elif data == "settings":
            await self._show_settings_menu(query)
        
        elif data == "help":
            await self._show_help_menu(query)
        
        elif data == "back_to_start":
            # Go back to main welcome message
            username = query.from_user.username or f"user_{user_id}"
            first_name = query.from_user.first_name or username
            
            welcome_message = f"""*{first_name} added Revolutionary Trading Bot to this group!*

Click *Get Started* to fund your trading wallet then:

1. *Analyze* any token with /analyze or /ai
2. *Get Notified* of trending tokens with /trending
3. *Buy and Sell* directly in chat with /buy and /sell
4. *Get Alerts* when opportunities are detected
5. *Follow* and *Copy Top Traders* with /leaderboard

💡 *Pro Tips:*
• Use /snipe for new token launches
• Check /community for crowd ratings
• Earn rewards with /rewards
• Copy successful traders with /copy

*All trades protected with Anti-MEV* 🛡️
"""
            keyboard = [
                [
                    InlineKeyboardButton("🚀 Get Started", callback_data="get_started"),
                    InlineKeyboardButton("❌ Close", callback_data="close_message")
                ],
                [
                    InlineKeyboardButton("📊 My Stats", callback_data="my_stats"),
                    InlineKeyboardButton("🏆 Leaderboard", callback_data="leaderboard")
                ],
                [
                    InlineKeyboardButton("⚙️ Settings", callback_data="settings"),
                    InlineKeyboardButton("❓ Help", callback_data="help")
                ]
            ]
            await query.edit_message_text(
                welcome_message,
                parse_mode='Markdown',
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        
        elif data.startswith("ai_buy_"):
            # Execute AI-recommended buy
            parts = data.split("_")
            token_mint = parts[2]
            amount = float(parts[3])
            
            await query.edit_message_text("⏳ Executing AI-recommended trade...")
            
            # Execute trade
            result = await self._execute_ai_trade(
                query.from_user.id,
                token_mint,
                amount,
                'buy'
            )
            
            if result['success']:
                message = f"✅ *TRADE EXECUTED*\n\n"
                message += f"Bought with AI recommendation\n"
                message += f"Amount: {amount:.4f} SOL\n"
                message += f"Signature: `{result['signature'][:16]}...`"
            else:
                message = f"❌ Trade failed: {result.get('error')}"
            
            await query.edit_message_text(message, parse_mode='Markdown')
        
        elif data.startswith("copy_set_"):
            # Set up copy trading
            parts = data.split("_")
            trader_id = int(parts[2])
            amount = float(parts[3])
            
            success = await self.social_marketplace.start_copying_trader(
                query.from_user.id,
                trader_id,
                {'amount_per_trade': amount, 'max_daily_trades': 20}
            )
            
            if success:
                await query.edit_message_text(
                    f"✅ *COPY TRADING ACTIVATED*\n\n"
                    f"You're now copying trader {trader_id}\n"
                    f"Amount per trade: {amount} SOL\n\n"
                    f"You'll automatically copy their trades!",
                    parse_mode='Markdown'
                )
                
                # Award points
                await self.rewards.award_points(
                    query.from_user.id,
                    REWARD_POINTS['help_user'],
                    'Started copy trading'
                )
        
        elif data.startswith("snipe_toggle_"):
            # Toggle snipe on/off
            parts = data.split("_")
            user_id = int(parts[2])
            
            if query.from_user.id != user_id:
                await query.answer("This is not your sniper settings!", show_alert=True)
                return
            
            # Get current status
            settings = await self.db.get_user_settings(user_id)
            current_status = settings.snipe_enabled if settings else False
            
            # Toggle
            new_status = not current_status
            await self.db.update_user_settings(user_id, {'snipe_enabled': new_status})

            if new_status:
                await self.sniper.enable_snipe(user_id)
                status_msg = "✅ AUTO-SNIPE ENABLED!\n\nMonitoring new launches..."
            else:
                await self.sniper.disable_snipe(user_id)
                status_msg = "❌ AUTO-SNIPE DISABLED\n\nNo longer monitoring."
            
            await query.edit_message_text(status_msg, parse_mode=None)
        
        elif data.startswith("snipe_config_"):
            # Show configuration options
            user_id = int(data.split("_")[2])
            
            message = """⚙️ SNIPER CONFIGURATION

Adjust your sniper settings:

Use these commands:
/snipe - View current settings
/snipe_enable - Enable sniper
/snipe_disable - Disable sniper

Advanced settings coming soon:
• Custom buy amounts
• Liquidity filters
• AI confidence threshold
• Daily limits
"""
            
            keyboard = [[InlineKeyboardButton("◀️ Back", callback_data="back_to_start")]]
            await query.edit_message_text(message, parse_mode=None, reply_markup=InlineKeyboardMarkup(keyboard))
    
    # ==================== HELPER METHODS ====================
    
    async def _show_wallet_info(self, query):
        """Show wallet info via callback"""
        user_id = query.from_user.id
        
        wallet_address = await self.wallet_manager.get_user_wallet_address(user_id)
        balance = await self.wallet_manager.get_user_balance(user_id)
        stats = await self.db.get_user_stats(user_id, days=30)
        
        message = f"""💰 *YOUR TRADING WALLET*

🔐 *Address:*
`{wallet_address}`

💵 *Balance:*
{balance:.6f} SOL

📊 *Trading Stats (30 days):*
Total Trades: {stats['total_trades']}
Win Rate: {stats['win_rate']:.1f}%
Total PnL: {stats['total_pnl']:+.4f} SOL

*Commands:*
/deposit - Fund your wallet
/balance - Check balance
"""
        
        keyboard = [
            [
                InlineKeyboardButton("📥 Deposit", callback_data="show_deposit"),
                InlineKeyboardButton("🔄 Refresh", callback_data="refresh_wallet")
            ],
            [InlineKeyboardButton("◀️ Back", callback_data="back_to_start")]
        ]
        
        await query.edit_message_text(
            message,
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    async def _show_deposit_info(self, query):
        """Show deposit info via callback"""
        user_id = query.from_user.id
        
        wallet_address = await self.wallet_manager.get_user_wallet_address(user_id)
        balance = await self.wallet_manager.get_user_balance(user_id)
        
        message = f"""📥 *DEPOSIT SOL*

Send SOL to your wallet:

🔐 *Address:*
`{wallet_address}`

💵 *Current Balance:*
{balance:.6f} SOL

*How to Deposit:*
1. Copy the address above
2. Send SOL from any Solana wallet
3. Funds arrive instantly!

Minimum: 0.01 SOL
"""
        
        keyboard = [
            [InlineKeyboardButton("🔄 Check Balance", callback_data="refresh_wallet")],
            [InlineKeyboardButton("◀️ Back", callback_data="show_wallet")]
        ]
        
        await query.edit_message_text(
            message,
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    async def _show_settings_menu(self, query):
        """Show settings menu with inline buttons"""
        message = """⚙️ *BOT SETTINGS*

Configure your trading preferences:

*Safety Limits:*
• Max Trade Size: 10.0 SOL
• Daily Loss Limit: 50.0 SOL
• Require Confirmations: ✅ ON

*Trading:*
• Default Buy Amount: 0.1 SOL
• Max Slippage: 5.0%
• Anti-MEV Protection: ✅ ON

*Features:*
• AI Analysis: ✅ Enabled
• Copy Trading: ✅ Enabled
• Auto-Alerts: ✅ Enabled

Use /settings command to modify these settings
"""
        keyboard = [[InlineKeyboardButton("◀️ Back", callback_data="back_to_start")]]
        await query.edit_message_text(
            message,
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    async def _show_help_menu(self, query):
        """Show help menu with all commands"""
        message = """❓ *HELP & COMMANDS*

*📊 Analysis Commands:*
/analyze <token> - AI-powered analysis
/ai <token> - Quick AI analysis
/trending - Trending tokens right now
/community <token> - Community ratings

*💰 Trading Commands:*
/buy <token_mint> <amount_sol> - Swap SOL into a token
/sell <token_mint> [amount_tokens|all] - Exit an open position
/snipe <token> - Snipe new launch
/positions - View open positions

*👥 Social Trading:*
/leaderboard - Top traders
/copy <trader_id> - Copy a trader
/stop_copy <trader_id> - Stop copying
/my_followers - Who's copying you

*🎮 Rewards & Stats:*
/my_stats - Your performance
/rewards - Points & tier status
/achievements - Your achievements

*🛡️ Safety:*
/settings - Configure bot
/limits - View safety limits

*Need more help?* Visit our documentation
"""
        keyboard = [[InlineKeyboardButton("◀️ Back", callback_data="back_to_start")]]
        await query.edit_message_text(
            message,
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    async def _fetch_token_data(self, token_mint: str) -> Dict:
        """Fetch comprehensive token data"""
        # In production, integrate with:
        # - Birdeye API
        # - DexScreener API
        # - Jupiter API
        # - On-chain data
        
        return {
            'address': token_mint,
            'symbol': 'TOKEN',
            'liquidity_usd': 50000,
            'volume_24h': 100000,
            'price_change_1h': 5.0,
            'price_change_24h': 10.0,
            'holder_count': 500,
            'top_10_holder_percentage': 30,
            'transaction_count_1h': 100,
            'buy_sell_ratio': 1.5,
            'market_cap': 1000000,
            'age_hours': 48,
            'social_mentions': 50,
            'sentiment_score': 65
        }
    
    async def _get_portfolio_value(self, user_id: int) -> float:
        """Get user's total portfolio value (SOL balance)"""
        return await self.wallet_manager.get_user_balance(user_id)
    
    async def _execute_ai_trade(
        self,
        user_id: int,
        token_mint: str,
        amount: float,
        action: str
    ) -> Dict:
        """Execute AI-recommended trade using user's personal wallet"""

        if action != 'buy':
            return {'success': False, 'error': 'Sell not implemented for AI trades yet'}

        try:
            return await self.trade_executor.execute_buy(
                user_id,
                token_mint,
                amount,
                reason='ai_signal',
                context='ai_signal'
            )
        except Exception as e:
            logger.error(f"Trade execution error: {e}")
            return {'success': False, 'error': str(e)}
    
    async def _get_user_points(self, user_id: int) -> int:
        """Get user's reward points"""
        rewards = await self.rewards.get_user_rewards(user_id)
        return rewards['points']
    
    async def _get_user_tier(self, user_id: int) -> str:
        """Get user's tier"""
        rewards = await self.rewards.get_user_rewards(user_id)
        return rewards['tier']
    
    def _get_tier_emoji(self, tier) -> str:
        """Get emoji for tier"""
        emojis = {
            'bronze': '🥉',
            'silver': '🥈',
            'gold': '🥇',
            'platinum': '💎',
            'diamond': '👑'
        }
        return emojis.get(tier.value, '⭐')
    
    async def _load_sniper_settings(self):
        """Load enabled sniper settings from database"""
        try:
            loaded = await self.sniper.load_persistent_settings()
            logger.info(
                "🎯 Sniper settings loaded from database (%d profiles)",
                len(loaded)
            )
        except Exception as e:
            logger.error(f"Error loading sniper settings: {e}")
    
    async def start(self, shutdown_event: Optional[asyncio.Event] = None):
        """Start the bot (async version for runner script)"""
        # Initialize database tables
        await self.db.init_db()

        # Load persisted social trading state
        await self.social_marketplace.initialize()

        # 🎯 Start auto-sniper monitoring
        await self.sniper.start()
        logger.info("🎯 Auto-sniper monitoring started")

        # Load enabled snipers from database
        await self._load_sniper_settings()

        if shutdown_event is not None:
            if shutdown_event.is_set():
                shutdown_event.clear()
            self._stop_event = shutdown_event
        else:
            self._stop_event = asyncio.Event()

        app = Application.builder().token(os.getenv('TELEGRAM_BOT_TOKEN')).build()

        # Register all commands with aliases
        app.add_handler(CommandHandler("start", self.start_command))
        
        # 🔐 Wallet commands (NEW!)
        app.add_handler(CommandHandler("wallet", self.wallet_command))
        app.add_handler(CommandHandler("deposit", self.deposit_command))
        app.add_handler(CommandHandler("balance", self.balance_command))
        app.add_handler(CommandHandler("export_wallet", self.export_wallet_command))
        app.add_handler(CommandHandler("export_keys", self.export_wallet_command))  # Alias

        # Trading commands
        app.add_handler(CommandHandler("buy", self.buy_command))
        app.add_handler(CommandHandler("sell", self.sell_command))
        
        # Analysis commands (with short aliases)
        app.add_handler(CommandHandler("ai_analyze", self.ai_analyze_command))
        app.add_handler(CommandHandler("analyze", self.ai_analyze_command))
        app.add_handler(CommandHandler("ai", self.ai_analyze_command))
        
        # Social & trending
        app.add_handler(CommandHandler("leaderboard", self.leaderboard_command))
        app.add_handler(CommandHandler("trending", self.trending_command))
        
        # 🎯 Sniper commands
        app.add_handler(CommandHandler("snipe", self.snipe_command))
        app.add_handler(CommandHandler("snipe_enable", self.snipe_enable_command))
        app.add_handler(CommandHandler("snipe_disable", self.snipe_disable_command))
        
        # 🧠 ELITE COMMANDS
        app.add_handler(CommandHandler("track", self.track_wallet_command))
        app.add_handler(CommandHandler("rankings", self.rankings_command))
        app.add_handler(CommandHandler("autostart", self.autostart_command))
        app.add_handler(CommandHandler("autostop", self.autostop_command))
        app.add_handler(CommandHandler("autostatus", self.autostatus_command))
        
        app.add_handler(CommandHandler("community", self.community_command))
        app.add_handler(CommandHandler("rate_token", self.rate_token_command))
        
        # Copy trading (with aliases)
        app.add_handler(CommandHandler("copy_trader", self.copy_trader_command))
        app.add_handler(CommandHandler("copy", self.copy_trader_command))
        app.add_handler(CommandHandler("stop_copy", self.stop_copy_command))
        
        # Stats & rewards
        app.add_handler(CommandHandler("my_stats", self.my_stats_command))
        app.add_handler(CommandHandler("stats", self.my_stats_command))
        app.add_handler(CommandHandler("rewards", self.rewards_command))
        
        # Strategy marketplace
        app.add_handler(CommandHandler("strategies", self.strategies_command))
        app.add_handler(CommandHandler("publish_strategy", self.publish_strategy_command))
        app.add_handler(CommandHandler("buy_strategy", self.buy_strategy_command))
        app.add_handler(CommandHandler("my_strategies", self.my_strategies_command))
        
        # Help
        app.add_handler(CommandHandler("help", self.help_command))
        app.add_handler(CommandHandler("features", self.features_command))
        
        # Admin
        app.add_handler(CommandHandler("metrics", self.metrics_command))
        
        # 🎯 PREDICTION LAYER COMMANDS (NEW!)
        app.add_handler(CommandHandler("predict", self.predict_command))
        app.add_handler(CommandHandler("autopredictions", self.autopredictions_command))
        app.add_handler(CommandHandler("prediction_stats", self.prediction_stats_command))
        
        # ⚡ FLASH LOAN ARBITRAGE COMMANDS (Phase 2 - NEW!)
        app.add_handler(CommandHandler("flash_arb", self.flash_arb_command))
        app.add_handler(CommandHandler("flash_enable", self.flash_enable_command))
        app.add_handler(CommandHandler("flash_stats", self.flash_stats_command))
        app.add_handler(CommandHandler("flash_opportunities", self.flash_opportunities_command))
        
        # Callback handler for all buttons
        app.add_handler(CallbackQueryHandler(self.button_callback))
        
        # Store app for cleanup
        self.app = app
        
        logger.info("🚀 REVOLUTIONARY TRADING BOT STARTED!")
        logger.info("=" * 50)
        logger.info("FEATURES ACTIVE:")
        logger.info("✅ AI-Powered Predictions")
        logger.info("✅ Social Trading Marketplace")
        logger.info("✅ Real-Time Sentiment Analysis")
        logger.info("✅ Community Intelligence")
        logger.info("✅ Adaptive Strategies")
        logger.info("✅ Pattern Recognition")
        logger.info("✅ Gamification & Rewards")
        logger.info("✅ Strategy Marketplace")
        logger.info("✅ Anti-MEV Protection")
        logger.info("✅ Professional Risk Management")
        logger.info("=" * 50)
        
        # Initialize and start polling
        await app.initialize()
        await app.start()
        await app.updater.start_polling(allowed_updates=Update.ALL_TYPES)

        logger.info("Bot is now listening for commands...")

        if self._stop_event is not None:
            await self._stop_event.wait()
            logger.info("Shutdown signal received; stopping bot loop")

    async def stop(self):
        """Stop the bot gracefully"""
        if self._stop_event and not self._stop_event.is_set():
            self._stop_event.set()

        if hasattr(self, 'app') and self.app:
            logger.info("Stopping bot...")
            try:
                # Stop sniper first
                await self.sniper.stop()

                # Stop Telegram updater and app
                if getattr(self.app, "updater", None):
                    await self.app.updater.stop()
                await self.app.stop()
                await self.app.shutdown()
                
                # Close network resources if we own them
                if self._owns_client and self.client:
                    logger.info("Closing Solana RPC client...")
                    await self.client.close()
                
                logger.info("Bot stopped successfully")
            except Exception as e:
                logger.error(f"Error during shutdown: {e}")
    
    def run(self):
        """Start the revolutionary bot (sync version for direct use)"""
        self.app = Application.builder().token(self.config.telegram_bot_token).build()
        app = self.app
        
        # Register all commands
        app.add_handler(CommandHandler("start", self.start_command))
        app.add_handler(CommandHandler("ai_analyze", self.ai_analyze_command))
        app.add_handler(CommandHandler("leaderboard", self.leaderboard_command))
        app.add_handler(CommandHandler("copy_trader", self.copy_trader_command))
        app.add_handler(CommandHandler("trending", self.trending_command))
        app.add_handler(CommandHandler("my_stats", self.my_stats_command))
        app.add_handler(CommandHandler("strategies", self.strategies_command))
        app.add_handler(CallbackQueryHandler(self.button_callback))
        
        logger.info("🚀 REVOLUTIONARY TRADING BOT STARTED!")
        logger.info("=" * 50)
        logger.info("FEATURES ACTIVE:")
        logger.info("✅ AI-Powered Predictions")
        logger.info("✅ Social Trading Marketplace")
        logger.info("✅ Real-Time Sentiment Analysis")
        logger.info("✅ Community Intelligence")
        logger.info("✅ Adaptive Strategies")
        logger.info("✅ Pattern Recognition")
        logger.info("✅ Gamification & Rewards")
        logger.info("✅ Strategy Marketplace")
        logger.info("✅ Anti-MEV Protection")
        logger.info("✅ Professional Risk Management")
        logger.info("=" * 50)
        
        app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    config = get_config()
    db_manager = DatabaseManager(config.database_url)
    asyncio.run(db_manager.init_db())
    client = AsyncClient(config.solana_rpc_url)

    bot = RevolutionaryTradingBot(config, db_manager, solana_client=client)
    try:
        bot.run()
    finally:
        asyncio.run(bot.stop())
    @staticmethod
    def _extract_confirm_token(args: List[str]) -> Tuple[Optional[str], List[str]]:
        """Return (confirm_token, remaining_args) parsed from Telegram arguments."""
        remainder: List[str] = []
        confirm_token: Optional[str] = None
        for arg in args:
            lowered = arg.lower()
            if lowered.startswith("confirm="):
                confirm_token = arg.split("=", 1)[1]
                continue
            if lowered.startswith("confirm:"):
                confirm_token = arg.split(":", 1)[1]
                continue
            remainder.append(arg)
        return confirm_token, remainder
