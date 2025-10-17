"""
SOLANA TRADING BOT - EDUCATIONAL FRAMEWORK
⚠️ WARNING: This is a starting framework, NOT production-ready!
- Test thoroughly on devnet first
- Never use large amounts of real money without extensive testing
- Understand the risks of automated trading
- Keep your private keys secure
"""

import os
import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from decimal import Decimal

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    MessageHandler,
    filters
)

# Solana imports
from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Confirmed
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.transaction import Transaction
from solders.system_program import transfer, TransferParams
from spl.token.async_client import AsyncToken
from spl.token.constants import TOKEN_PROGRAM_ID

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Configuration
class Config:
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE')
    SOLANA_RPC_URL = os.getenv('SOLANA_RPC_URL', 'https://api.mainnet-beta.solana.com')
    # NEVER hardcode private keys in production!
    WALLET_PRIVATE_KEY = os.getenv('WALLET_PRIVATE_KEY', '')
    
    # Trading parameters
    MAX_SLIPPAGE = 0.05  # 5%
    DEFAULT_BUY_AMOUNT_SOL = 0.1  # Default buy amount
    MIN_PROFIT_PERCENTAGE = 2.0  # Minimum profit % to trigger auto-sell
    
    # Safety limits
    MAX_TRADE_SIZE_SOL = 1.0  # Maximum per trade
    DAILY_LOSS_LIMIT_SOL = 5.0  # Stop trading if losses exceed this
    REQUIRE_CONFIRMATION = True  # Require user confirmation for trades
    
    # Anti-scam features
    MIN_LIQUIDITY_USD = 10000  # Minimum liquidity required
    CHECK_MINT_AUTHORITY = True  # Check if mint authority is revoked
    CHECK_FREEZE_AUTHORITY = True  # Check if freeze authority is revoked


class WalletTracker:
    """Track and rank wallets based on profitability"""
    
    def __init__(self):
        self.tracked_wallets: Dict[str, Dict] = {}
        self.wallet_scores: Dict[str, float] = {}
        
    def add_wallet(self, address: str, label: str = ""):
        """Add a wallet to track"""
        self.tracked_wallets[address] = {
            'label': label,
            'added_at': datetime.now(),
            'transactions': [],
            'pnl': 0.0,
            'win_rate': 0.0,
            'total_trades': 0
        }
        
    async def analyze_wallet(self, client: AsyncClient, address: str) -> Dict:
        """Analyze wallet's trading patterns and profitability"""
        try:
            pubkey = Pubkey.from_string(address)
            
            # Get recent signatures
            signatures = await client.get_signatures_for_address(
                pubkey,
                limit=100
            )
            
            transactions = []
            profitable_trades = 0
            total_pnl = 0.0
            
            for sig_info in signatures.value:
                try:
                    tx = await client.get_transaction(
                        sig_info.signature,
                        encoding="jsonParsed",
                        max_supported_transaction_version=0
                    )
                    
                    if tx.value:
                        # Analyze transaction for trading patterns
                        tx_data = self._parse_transaction(tx.value)
                        if tx_data:
                            transactions.append(tx_data)
                            if tx_data.get('pnl', 0) > 0:
                                profitable_trades += 1
                            total_pnl += tx_data.get('pnl', 0)
                            
                except Exception as e:
                    logger.error(f"Error analyzing tx: {e}")
                    continue
            
            total_trades = len(transactions)
            win_rate = (profitable_trades / total_trades * 100) if total_trades > 0 else 0
            
            # Calculate wallet score (0-100)
            score = self._calculate_wallet_score(win_rate, total_pnl, total_trades)
            
            return {
                'address': address,
                'total_trades': total_trades,
                'profitable_trades': profitable_trades,
                'win_rate': win_rate,
                'total_pnl': total_pnl,
                'score': score,
                'transactions': transactions[:10]  # Last 10 transactions
            }
            
        except Exception as e:
            logger.error(f"Error analyzing wallet {address}: {e}")
            return {}
    
    def _parse_transaction(self, tx_data) -> Optional[Dict]:
        """Parse transaction data to extract trading info"""
        # This is a simplified version - you'd need to parse DEX-specific data
        return {
            'timestamp': datetime.now(),
            'type': 'swap',
            'pnl': 0.0,  # Calculate actual PnL
            'token': 'UNKNOWN'
        }
    
    def _calculate_wallet_score(self, win_rate: float, pnl: float, trades: int) -> float:
        """Calculate overall wallet score (0-100)"""
        # Weighted scoring system
        win_rate_score = min(win_rate, 100) * 0.4
        pnl_score = min(max(pnl / 10, 0), 100) * 0.4  # Normalize PnL
        volume_score = min(trades / 100 * 100, 100) * 0.2
        
        return win_rate_score + pnl_score + volume_score
    
    def get_top_wallets(self, limit: int = 10) -> List[Tuple[str, float]]:
        """Get top performing wallets"""
        sorted_wallets = sorted(
            self.wallet_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )
        return sorted_wallets[:limit]


class TokenAnalyzer:
    """Analyze tokens for scams and opportunities"""
    
    def __init__(self, client: AsyncClient):
        self.client = client
        self.honeypot_cache: Dict[str, bool] = {}
        
    async def check_token_safety(self, token_mint: str) -> Dict:
        """Comprehensive token safety check"""
        safety_report = {
            'is_safe': True,
            'warnings': [],
            'score': 100
        }
        
        try:
            mint_pubkey = Pubkey.from_string(token_mint)
            
            # Check if already flagged
            if token_mint in self.honeypot_cache:
                safety_report['is_safe'] = False
                safety_report['warnings'].append("Known honeypot")
                return safety_report
            
            # Get token account info
            account_info = await self.client.get_account_info(mint_pubkey)
            
            if not account_info.value:
                safety_report['warnings'].append("Token mint not found")
                safety_report['score'] -= 50
                return safety_report
            
            # Check mint authority (should be revoked for safe tokens)
            # Note: This is simplified - you'd parse the actual account data
            if Config.CHECK_MINT_AUTHORITY:
                # Actual implementation would check if mint authority is None
                pass
            
            # Check freeze authority
            if Config.CHECK_FREEZE_AUTHORITY:
                # Actual implementation would check if freeze authority is None
                pass
            
            # Check liquidity
            liquidity = await self._check_liquidity(token_mint)
            if liquidity < Config.MIN_LIQUIDITY_USD:
                safety_report['warnings'].append(f"Low liquidity: ${liquidity:,.2f}")
                safety_report['score'] -= 30
            
            # Check for suspicious patterns
            suspicious = await self._check_suspicious_patterns(token_mint)
            if suspicious:
                safety_report['warnings'].append("Suspicious trading patterns detected")
                safety_report['score'] -= 20
            
            # Final safety determination
            safety_report['is_safe'] = len(safety_report['warnings']) == 0 and safety_report['score'] >= 70
            
            return safety_report
            
        except Exception as e:
            logger.error(f"Error checking token safety: {e}")
            return {
                'is_safe': False,
                'warnings': [f"Error analyzing token: {str(e)}"],
                'score': 0
            }
    
    async def _check_liquidity(self, token_mint: str) -> float:
        """Check token liquidity on DEXes"""
        # Implement actual liquidity check via Raydium/Orca APIs
        return 50000.0  # Placeholder
    
    async def _check_suspicious_patterns(self, token_mint: str) -> bool:
        """Check for suspicious patterns like pump and dumps"""
        # Implement pattern detection
        return False  # Placeholder
    
    async def detect_honeypot(self, token_mint: str) -> bool:
        """Detect if token is a honeypot"""
        try:
            # Try to simulate a sell transaction (without executing)
            # If it fails, likely a honeypot
            
            # Check if token has been flagged by community
            # This would integrate with honeypot detection APIs
            
            return False  # Placeholder
            
        except Exception as e:
            logger.error(f"Honeypot detection error: {e}")
            return True  # Err on the side of caution


class TradingEngine:
    """Execute trades with safety checks"""
    
    def __init__(self, client: AsyncClient, keypair: Keypair):
        self.client = client
        self.keypair = keypair
        self.daily_loss = 0.0
        self.last_reset = datetime.now()
        self.auto_trading_enabled = False
        
    def enable_auto_trading(self, enabled: bool):
        """Enable/disable auto trading"""
        self.auto_trading_enabled = enabled
        logger.info(f"Auto trading: {'ENABLED' if enabled else 'DISABLED'}")
        
    async def execute_buy(
        self,
        token_mint: str,
        amount_sol: float,
        slippage: float = Config.MAX_SLIPPAGE
    ) -> Dict:
        """Execute buy order with safety checks"""
        
        # Safety checks
        if not await self._pre_trade_checks(amount_sol):
            return {'success': False, 'error': 'Safety checks failed'}
        
        try:
            logger.info(f"Executing BUY: {amount_sol} SOL for {token_mint}")
            
            # This is where you'd integrate with Jupiter, Raydium, or Orca
            # For now, this is a placeholder structure
            
            # Get quote
            quote = await self._get_swap_quote(
                'So11111111111111111111111111111111111111112',  # SOL mint
                token_mint,
                amount_sol
            )
            
            if not quote:
                return {'success': False, 'error': 'Failed to get quote'}
            
            # Build and send transaction
            # tx = await self._build_swap_transaction(quote)
            # signature = await self.client.send_transaction(tx, self.keypair)
            
            # Placeholder response
            return {
                'success': True,
                'signature': 'PLACEHOLDER_SIGNATURE',
                'amount_sol': amount_sol,
                'token_mint': token_mint,
                'tokens_received': quote.get('out_amount', 0)
            }
            
        except Exception as e:
            logger.error(f"Buy execution error: {e}")
            return {'success': False, 'error': str(e)}
    
    async def execute_sell(
        self,
        token_mint: str,
        amount_tokens: float,
        slippage: float = Config.MAX_SLIPPAGE
    ) -> Dict:
        """Execute sell order with anti-MEV protection"""
        
        try:
            logger.info(f"Executing SELL: {amount_tokens} tokens of {token_mint}")
            
            # Anti-MEV: Use private RPC or Jito bundles
            # This requires integration with Jito or similar services
            
            # Get quote
            quote = await self._get_swap_quote(
                token_mint,
                'So11111111111111111111111111111111111111112',  # SOL mint
                amount_tokens
            )
            
            if not quote:
                return {'success': False, 'error': 'Failed to get quote'}
            
            # Build transaction with anti-MEV protection
            # tx = await self._build_swap_transaction(quote, anti_mev=True)
            
            return {
                'success': True,
                'signature': 'PLACEHOLDER_SIGNATURE',
                'amount_tokens': amount_tokens,
                'sol_received': quote.get('out_amount', 0)
            }
            
        except Exception as e:
            logger.error(f"Sell execution error: {e}")
            return {'success': False, 'error': str(e)}
    
    async def snipe_token(self, token_mint: str, amount_sol: float) -> Dict:
        """Snipe token at launch (buy as soon as liquidity is added)"""
        
        logger.info(f"Setting up snipe for {token_mint}")
        
        # Monitor for liquidity addition
        max_attempts = 100
        for attempt in range(max_attempts):
            try:
                # Check if liquidity pool exists
                has_liquidity = await self._check_pool_exists(token_mint)
                
                if has_liquidity:
                    logger.info(f"Liquidity detected! Executing snipe...")
                    return await self.execute_buy(token_mint, amount_sol)
                
                await asyncio.sleep(0.1)  # Check every 100ms
                
            except Exception as e:
                logger.error(f"Snipe error: {e}")
                
        return {'success': False, 'error': 'Snipe timeout - no liquidity detected'}
    
    async def _pre_trade_checks(self, amount_sol: float) -> bool:
        """Pre-trade safety checks"""
        
        # Reset daily loss counter if needed
        if (datetime.now() - self.last_reset).days >= 1:
            self.daily_loss = 0.0
            self.last_reset = datetime.now()
        
        # Check daily loss limit
        if self.daily_loss >= Config.DAILY_LOSS_LIMIT_SOL:
            logger.warning("Daily loss limit reached!")
            return False
        
        # Check trade size limit
        if amount_sol > Config.MAX_TRADE_SIZE_SOL:
            logger.warning(f"Trade size exceeds limit: {amount_sol} > {Config.MAX_TRADE_SIZE_SOL}")
            return False
        
        # Check wallet balance
        balance = await self._get_balance()
        if balance < amount_sol:
            logger.warning(f"Insufficient balance: {balance} < {amount_sol}")
            return False
        
        return True
    
    async def _get_balance(self) -> float:
        """Get SOL balance"""
        try:
            response = await self.client.get_balance(self.keypair.pubkey())
            return response.value / 1e9  # Convert lamports to SOL
        except Exception as e:
            logger.error(f"Error getting balance: {e}")
            return 0.0
    
    async def _get_swap_quote(self, input_mint: str, output_mint: str, amount: float) -> Optional[Dict]:
        """Get swap quote from Jupiter or other aggregator"""
        # Integrate with Jupiter API
        # https://quote-api.jup.ag/v6/quote
        return {'out_amount': amount * 1000}  # Placeholder
    
    async def _check_pool_exists(self, token_mint: str) -> bool:
        """Check if liquidity pool exists for token"""
        # Check Raydium/Orca pools
        return False  # Placeholder


class SolanaTradingBot:
    """Main bot class"""
    
    def __init__(self):
        self.client = AsyncClient(Config.SOLANA_RPC_URL)
        
        # Initialize wallet (NEVER hardcode private keys!)
        if Config.WALLET_PRIVATE_KEY:
            # In production, use secure key management
            self.keypair = Keypair.from_base58_string(Config.WALLET_PRIVATE_KEY)
        else:
            logger.warning("No wallet configured - trades will not execute")
            self.keypair = None
        
        self.wallet_tracker = WalletTracker()
        self.token_analyzer = TokenAnalyzer(self.client)
        self.trading_engine = TradingEngine(self.client, self.keypair) if self.keypair else None
        
        # User settings
        self.user_settings: Dict[int, Dict] = {}
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        user_id = update.effective_user.id
        
        welcome_message = """
🚀 *SOLANA TRADING BOT*

⚠️ *IMPORTANT WARNINGS:*
• This bot can lose ALL your money
• Start with small amounts
• Test on devnet first
• Never share private keys
• Crypto trading is extremely risky

*Available Commands:*
/balance - Check wallet balance
/track <wallet> - Track a wallet
/analyze <token> - Analyze token safety
/buy <token> <amount> - Buy tokens
/sell <token> <amount> - Sell tokens
/snipe <token> <amount> - Snipe token launch
/leaderboard - Top wallets
/settings - Configure bot
/help - Show all commands

Ready to trade? Use /settings first!
"""
        await update.message.reply_text(welcome_message, parse_mode='Markdown')
    
    async def balance_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Check wallet balance"""
        if not self.trading_engine:
            await update.message.reply_text("❌ No wallet configured")
            return
        
        balance = await self.trading_engine._get_balance()
        
        message = f"""
💰 *Wallet Balance*

SOL: `{balance:.4f}`
Wallet: `{str(self.keypair.pubkey())[:8]}...`

Daily Loss: `{self.trading_engine.daily_loss:.4f}` SOL
Loss Limit: `{Config.DAILY_LOSS_LIMIT_SOL}` SOL
"""
        await update.message.reply_text(message, parse_mode='Markdown')
    
    async def track_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Track a wallet"""
        if len(context.args) < 1:
            await update.message.reply_text("Usage: /track <wallet_address>")
            return
        
        wallet_address = context.args[0]
        label = " ".join(context.args[1:]) if len(context.args) > 1 else ""
        
        await update.message.reply_text(f"🔍 Analyzing wallet {wallet_address[:8]}...")
        
        self.wallet_tracker.add_wallet(wallet_address, label)
        analysis = await self.wallet_tracker.analyze_wallet(self.client, wallet_address)
        
        if analysis:
            message = f"""
📊 *Wallet Analysis*

Address: `{wallet_address[:8]}...`
Score: `{analysis['score']:.1f}/100`

Total Trades: `{analysis['total_trades']}`
Profitable: `{analysis['profitable_trades']}`
Win Rate: `{analysis['win_rate']:.1f}%`
Total PnL: `{analysis['total_pnl']:.4f}` SOL

✅ Wallet tracked successfully!
"""
            await update.message.reply_text(message, parse_mode='Markdown')
        else:
            await update.message.reply_text("❌ Failed to analyze wallet")
    
    async def analyze_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Analyze token safety"""
        if len(context.args) < 1:
            await update.message.reply_text("Usage: /analyze <token_address>")
            return
        
        token_mint = context.args[0]
        
        await update.message.reply_text(f"🔍 Analyzing token {token_mint[:8]}...")
        
        safety_report = await self.token_analyzer.check_token_safety(token_mint)
        
        status_emoji = "✅" if safety_report['is_safe'] else "⚠️"
        
        message = f"""
{status_emoji} *Token Safety Report*

Token: `{token_mint[:8]}...`
Safety Score: `{safety_report['score']}/100`
Status: {"SAFE" if safety_report['is_safe'] else "RISKY"}

"""
        
        if safety_report['warnings']:
            message += "*Warnings:*\n"
            for warning in safety_report['warnings']:
                message += f"• {warning}\n"
        else:
            message += "No warnings detected!"
        
        await update.message.reply_text(message, parse_mode='Markdown')
    
    async def buy_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Buy tokens"""
        if not self.trading_engine:
            await update.message.reply_text("❌ No wallet configured")
            return
        
        if len(context.args) < 2:
            await update.message.reply_text("Usage: /buy <token_address> <amount_sol>")
            return
        
        token_mint = context.args[0]
        try:
            amount_sol = float(context.args[1])
        except ValueError:
            await update.message.reply_text("❌ Invalid amount")
            return
        
        # Safety check
        safety_report = await self.token_analyzer.check_token_safety(token_mint)
        
        if not safety_report['is_safe']:
            keyboard = [
                [
                    InlineKeyboardButton("⚠️ Buy Anyway", callback_data=f"buy_force_{token_mint}_{amount_sol}"),
                    InlineKeyboardButton("❌ Cancel", callback_data="cancel")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            message = f"⚠️ *TOKEN WARNING*\n\nSafety Score: {safety_report['score']}/100\n\n"
            message += "\n".join(f"• {w}" for w in safety_report['warnings'])
            message += "\n\nAre you sure you want to buy?"
            
            await update.message.reply_text(message, parse_mode='Markdown', reply_markup=reply_markup)
            return
        
        # Confirm purchase
        if Config.REQUIRE_CONFIRMATION:
            keyboard = [
                [
                    InlineKeyboardButton("✅ Confirm Buy", callback_data=f"buy_confirm_{token_mint}_{amount_sol}"),
                    InlineKeyboardButton("❌ Cancel", callback_data="cancel")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            message = f"🔍 Ready to buy:\n\nToken: `{token_mint[:8]}...`\nAmount: `{amount_sol}` SOL\n\nConfirm?"
            await update.message.reply_text(message, parse_mode='Markdown', reply_markup=reply_markup)
        else:
            # Execute immediately
            result = await self.trading_engine.execute_buy(token_mint, amount_sol)
            await self._send_trade_result(update, result, "BUY")
    
    async def sell_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Sell tokens"""
        if not self.trading_engine:
            await update.message.reply_text("❌ No wallet configured")
            return
        
        if len(context.args) < 2:
            await update.message.reply_text("Usage: /sell <token_address> <amount>")
            return
        
        token_mint = context.args[0]
        try:
            amount = float(context.args[1])
        except ValueError:
            await update.message.reply_text("❌ Invalid amount")
            return
        
        # Confirm sale
        keyboard = [
            [
                InlineKeyboardButton("✅ Confirm Sell", callback_data=f"sell_confirm_{token_mint}_{amount}"),
                InlineKeyboardButton("❌ Cancel", callback_data="cancel")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        message = f"🔍 Ready to sell:\n\nToken: `{token_mint[:8]}...`\nAmount: `{amount}`\n\nConfirm?"
        await update.message.reply_text(message, parse_mode='Markdown', reply_markup=reply_markup)
    
    async def snipe_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Snipe token launch"""
        if not self.trading_engine:
            await update.message.reply_text("❌ No wallet configured")
            return
        
        if len(context.args) < 2:
            await update.message.reply_text("Usage: /snipe <token_address> <amount_sol>")
            return
        
        token_mint = context.args[0]
        try:
            amount_sol = float(context.args[1])
        except ValueError:
            await update.message.reply_text("❌ Invalid amount")
            return
        
        await update.message.reply_text(f"🎯 Setting up snipe for {token_mint[:8]}...\n\nWaiting for liquidity...")
        
        result = await self.trading_engine.snipe_token(token_mint, amount_sol)
        await self._send_trade_result(update, result, "SNIPE")
    
    async def leaderboard_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show top wallets"""
        top_wallets = self.wallet_tracker.get_top_wallets(10)
        
        if not top_wallets:
            await update.message.reply_text("No wallets tracked yet. Use /track to add wallets.")
            return
        
        message = "🏆 *Top Wallets Leaderboard*\n\n"
        
        for i, (address, score) in enumerate(top_wallets, 1):
            wallet_data = self.wallet_tracker.tracked_wallets.get(address, {})
            label = wallet_data.get('label', 'Unknown')
            message += f"{i}. `{address[:8]}...` - {label}\n"
            message += f"   Score: {score:.1f}/100\n\n"
        
        await update.message.reply_text(message, parse_mode='Markdown')
    
    async def settings_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Configure bot settings"""
        keyboard = [
            [
                InlineKeyboardButton("🤖 Auto Trading", callback_data="toggle_auto"),
                InlineKeyboardButton("🛡️ Safety Checks", callback_data="toggle_safety")
            ],
            [
                InlineKeyboardButton("📊 Slippage Settings", callback_data="set_slippage"),
                InlineKeyboardButton("💰 Trade Limits", callback_data="set_limits")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        auto_status = "✅ ON" if self.trading_engine and self.trading_engine.auto_trading_enabled else "❌ OFF"
        
        message = f"""
⚙️ *Bot Settings*

Auto Trading: {auto_status}
Require Confirmation: {Config.REQUIRE_CONFIRMATION}
Max Trade Size: {Config.MAX_TRADE_SIZE_SOL} SOL
Daily Loss Limit: {Config.DAILY_LOSS_LIMIT_SOL} SOL
Max Slippage: {Config.MAX_SLIPPAGE * 100}%

Select an option:
"""
        await update.message.reply_text(message, parse_mode='Markdown', reply_markup=reply_markup)
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle button callbacks"""
        query = update.callback_query
        await query.answer()
        
        data = query.data
        
        if data == "cancel":
            await query.edit_message_text("❌ Cancelled")
            return
        
        if data == "toggle_auto":
            if self.trading_engine:
                new_state = not self.trading_engine.auto_trading_enabled
                self.trading_engine.enable_auto_trading(new_state)
                status = "✅ ENABLED" if new_state else "❌ DISABLED"
                await query.edit_message_text(f"Auto Trading: {status}\n\n⚠️ Warning: Auto trading can lose money fast!")
            return
        
        if data.startswith("buy_confirm_"):
            parts = data.split("_")
            token_mint = parts[2]
            amount_sol = float(parts[3])
            
            await query.edit_message_text("⏳ Executing buy order...")
            result = await self.trading_engine.execute_buy(token_mint, amount_sol)
            
            if result['success']:
                message = f"✅ *BUY SUCCESSFUL*\n\n"
                message += f"Token: `{token_mint[:8]}...`\n"
                message += f"Spent: `{amount_sol}` SOL\n"
                message += f"Received: `{result.get('tokens_received', 0)}` tokens\n"
                message += f"Signature: `{result['signature'][:8]}...`"
            else:
                message = f"❌ Buy failed: {result.get('error', 'Unknown error')}"
            
            await query.edit_message_text(message, parse_mode='Markdown')
            return
        
        if data.startswith("sell_confirm_"):
            parts = data.split("_")
            token_mint = parts[2]
            amount = float(parts[3])
            
            await query.edit_message_text("⏳ Executing sell order...")
            result = await self.trading_engine.execute_sell(token_mint, amount)
            
            if result['success']:
                message = f"✅ *SELL SUCCESSFUL*\n\n"
                message += f"Token: `{token_mint[:8]}...`\n"
                message += f"Sold: `{amount}` tokens\n"
                message += f"Received: `{result.get('sol_received', 0)}` SOL\n"
                message += f"Signature: `{result['signature'][:8]}...`"
            else:
                message = f"❌ Sell failed: {result.get('error', 'Unknown error')}"
            
            await query.edit_message_text(message, parse_mode='Markdown')
            return
    
    async def _send_trade_result(self, update: Update, result: Dict, trade_type: str):
        """Send trade result message"""
        if result['success']:
            message = f"✅ *{trade_type} SUCCESSFUL*\n\n"
            message += f"Signature: `{result.get('signature', 'N/A')[:8]}...`"
        else:
            message = f"❌ {trade_type} failed: {result.get('error', 'Unknown error')}"
        
        await update.message.reply_text(message, parse_mode='Markdown')
    
    def run(self):
        """Start the bot"""
        app = Application.builder().token(Config.TELEGRAM_BOT_TOKEN).build()
        
        # Command handlers
        app.add_handler(CommandHandler("start", self.start_command))
        app.add_handler(CommandHandler("balance", self.balance_command))
        app.add_handler(CommandHandler("track", self.track_command))
        app.add_handler(CommandHandler("analyze", self.analyze_command))
        app.add_handler(CommandHandler("buy", self.buy_command))
        app.add_handler(CommandHandler("sell", self.sell_command))
        app.add_handler(CommandHandler("snipe", self.snipe_command))
        app.add_handler(CommandHandler("leaderboard", self.leaderboard_command))
        app.add_handler(CommandHandler("settings", self.settings_command))
        
        # Callback handler
        app.add_handler(CallbackQueryHandler(self.button_callback))
        
        logger.info("🚀 Solana Trading Bot started!")
        app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    bot = SolanaTradingBot()
    bot.run()
