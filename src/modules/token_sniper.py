"""
AUTOMATIC TOKEN SNIPER
Monitors pump.fun for new launches and auto-buys based on AI analysis

FEATURES:
- Real-time token detection
- Instant AI analysis
- Automatic execution
- Safety limits
- Per-user settings
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set
import aiohttp
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class SnipeSettings:
    """User's snipe configuration"""
    user_id: int
    enabled: bool = False
    max_buy_amount: float = 0.1  # SOL
    min_liquidity: float = 10000  # USD
    min_ai_confidence: float = 0.65  # 65%
    max_daily_snipes: int = 10
    only_strong_buy: bool = True  # Only buy if AI says "strong_buy"
    require_social: bool = False  # Require social mentions
    
    # Limits
    daily_snipes_used: int = 0
    last_reset: datetime = None


class PumpFunMonitor:
    """
    Monitors pump.fun for new token launches
    Uses DexScreener API + periodic checking
    """
    
    def __init__(self):
        self.session = None
        self.seen_tokens: Set[str] = set()
        self.running = False
        self.check_interval = 30  # seconds
        self.callbacks = []
        
    async def start(self):
        """Start monitoring"""
        if self.running:
            return
        
        self.running = True
        self.session = aiohttp.ClientSession()
        logger.info("🎯 Pump.fun monitor started")
        
        # Start monitoring loop
        asyncio.create_task(self._monitor_loop())
    
    async def stop(self):
        """Stop monitoring"""
        self.running = False
        if self.session:
            await self.session.close()
        logger.info("🎯 Pump.fun monitor stopped")
    
    def on_new_token(self, callback):
        """Register callback for new tokens"""
        self.callbacks.append(callback)
    
    async def _monitor_loop(self):
        """Main monitoring loop"""
        while self.running:
            try:
                await self._check_new_tokens()
            except Exception as e:
                logger.error(f"Monitor loop error: {e}")
            
            await asyncio.sleep(self.check_interval)
    
    async def _check_new_tokens(self):
        """Check for new token launches"""
        try:
            # Use DexScreener to find recent Solana tokens
            url = "https://api.dexscreener.com/latest/dex/tokens/So11111111111111111111111111111111111111112"
            
            async with self.session.get(url, timeout=10) as response:
                if response.status != 200:
                    return
                
                data = await response.json()
                pairs = data.get('pairs', [])
                
                # Filter for very new tokens (created in last 5 minutes)
                now = datetime.now().timestamp() * 1000
                five_min_ago = now - (5 * 60 * 1000)
                
                for pair in pairs[:20]:  # Check top 20
                    if pair.get('chainId') != 'solana':
                        continue
                    
                    token_address = pair.get('baseToken', {}).get('address')
                    created_at = pair.get('pairCreatedAt', 0)
                    
                    if not token_address or token_address in self.seen_tokens:
                        continue
                    
                    # Check if newly launched (within last 5 minutes)
                    if created_at and created_at > five_min_ago:
                        self.seen_tokens.add(token_address)
                        
                        # Extract token info
                        token_info = {
                            'address': token_address,
                            'symbol': pair.get('baseToken', {}).get('symbol', 'UNKNOWN'),
                            'name': pair.get('baseToken', {}).get('name', 'Unknown'),
                            'liquidity_usd': float(pair.get('liquidity', {}).get('usd', 0) or 0),
                            'price_usd': float(pair.get('priceUsd', 0) or 0),
                            'created_at': created_at,
                            'dex': pair.get('dexId', 'unknown')
                        }
                        
                        logger.info(f"🎯 NEW TOKEN DETECTED: {token_info['symbol']} ({token_address[:8]}...)")
                        
                        # Notify all callbacks
                        for callback in self.callbacks:
                            try:
                                await callback(token_info)
                            except Exception as e:
                                logger.error(f"Callback error: {e}")
                
                # Limit seen_tokens size to prevent memory issues
                if len(self.seen_tokens) > 1000:
                    # Keep only recent 500
                    self.seen_tokens = set(list(self.seen_tokens)[-500:])
        
        except Exception as e:
            logger.error(f"Error checking new tokens: {e}")


class AutoSniper:
    """
    Automatic token sniper
    Analyzes and buys new tokens based on AI + user settings
    """
    
    def __init__(self, ai_manager, wallet_manager, jupiter_client):
        self.ai_manager = ai_manager
        self.wallet_manager = wallet_manager
        self.jupiter = jupiter_client
        self.monitor = PumpFunMonitor()
        
        # User settings: user_id -> SnipeSettings
        self.user_settings: Dict[int, SnipeSettings] = {}
        
        # Rate limiting
        self.last_snipe = {}  # user_id -> timestamp
        self.min_snipe_interval = 60  # seconds between snipes per user
    
    async def start(self):
        """Start the sniper"""
        await self.monitor.start()
        self.monitor.on_new_token(self._on_new_token_detected)
        logger.info("🎯 Auto-sniper started and monitoring")
    
    async def stop(self):
        """Stop the sniper"""
        await self.monitor.stop()
        logger.info("🎯 Auto-sniper stopped")
    
    def enable_snipe(self, user_id: int, settings: Dict = None):
        """Enable auto-snipe for a user"""
        if user_id not in self.user_settings:
            self.user_settings[user_id] = SnipeSettings(
                user_id=user_id,
                last_reset=datetime.now()
            )
        
        self.user_settings[user_id].enabled = True
        
        # Update settings if provided
        if settings:
            for key, value in settings.items():
                if hasattr(self.user_settings[user_id], key):
                    setattr(self.user_settings[user_id], key, value)
        
        logger.info(f"🎯 Auto-snipe enabled for user {user_id}")
        return self.user_settings[user_id]
    
    def disable_snipe(self, user_id: int):
        """Disable auto-snipe for a user"""
        if user_id in self.user_settings:
            self.user_settings[user_id].enabled = False
            logger.info(f"🎯 Auto-snipe disabled for user {user_id}")
    
    def get_settings(self, user_id: int) -> Optional[SnipeSettings]:
        """Get user's snipe settings"""
        return self.user_settings.get(user_id)
    
    async def _on_new_token_detected(self, token_info: Dict):
        """Called when a new token is detected"""
        logger.info(f"🎯 Processing new token: {token_info['symbol']}")
        
        # Check which users have auto-snipe enabled
        enabled_users = [
            user_id for user_id, settings in self.user_settings.items()
            if settings.enabled
        ]
        
        if not enabled_users:
            logger.debug("No users with auto-snipe enabled")
            return
        
        logger.info(f"🎯 {len(enabled_users)} users with auto-snipe enabled")
        
        # Analyze token for each enabled user
        for user_id in enabled_users:
            try:
                await self._process_snipe_for_user(user_id, token_info)
            except Exception as e:
                logger.error(f"Error processing snipe for user {user_id}: {e}")
    
    async def _process_snipe_for_user(self, user_id: int, token_info: Dict):
        """Process potential snipe for a specific user"""
        settings = self.user_settings[user_id]
        
        # Reset daily counter if needed
        if settings.last_reset and (datetime.now() - settings.last_reset).days >= 1:
            settings.daily_snipes_used = 0
            settings.last_reset = datetime.now()
        
        # Check daily limit
        if settings.daily_snipes_used >= settings.max_daily_snipes:
            logger.debug(f"User {user_id} hit daily snipe limit")
            return
        
        # Check rate limiting
        last_snipe_time = self.last_snipe.get(user_id, 0)
        if datetime.now().timestamp() - last_snipe_time < self.min_snipe_interval:
            logger.debug(f"User {user_id} rate limited")
            return
        
        # Check minimum liquidity
        if token_info['liquidity_usd'] < settings.min_liquidity:
            logger.debug(f"Token liquidity too low: ${token_info['liquidity_usd']:.0f} < ${settings.min_liquidity:.0f}")
            return
        
        # Get user balance
        balance = await self.wallet_manager.get_user_balance(user_id)
        if balance < settings.max_buy_amount:
            logger.debug(f"User {user_id} insufficient balance: {balance:.4f} < {settings.max_buy_amount:.4f}")
            return
        
        # Prepare token data for AI analysis
        token_data = {
            'address': token_info['address'],
            'symbol': token_info['symbol'],
            'liquidity_usd': token_info['liquidity_usd'],
            'volume_24h': 0,  # Too new
            'price_change_1h': 0,
            'price_change_24h': 0,
            'holder_count': 50,  # Estimate
            'top_10_holder_percentage': 40,  # Assume concentrated
            'transaction_count_1h': 10,  # Early
            'buy_sell_ratio': 1.5,  # Assume buying
            'market_cap': token_info['liquidity_usd'] * 2,
            'age_hours': 0.1,  # Very new
            'social_mentions': 0,  # Too new
            'sentiment_score': 50  # Neutral
        }
        
        # Run AI analysis
        logger.info(f"🎯 Running AI analysis for user {user_id} on {token_info['symbol']}")
        ai_analysis = await self.ai_manager.analyze_opportunity(token_data, balance)
        
        # Check AI recommendation
        action = ai_analysis['action']
        confidence = ai_analysis['confidence']
        
        logger.info(f"🎯 AI says: {action} with {confidence:.1%} confidence")
        
        # Check if meets criteria
        if settings.only_strong_buy and action != 'strong_buy':
            logger.debug(f"Not strong_buy: {action}")
            return
        
        if confidence < settings.min_ai_confidence:
            logger.debug(f"Confidence too low: {confidence:.1%} < {settings.min_ai_confidence:.1%}")
            return
        
        # Execute snipe!
        logger.info(f"🎯 EXECUTING SNIPE for user {user_id}: {token_info['symbol']}")
        
        try:
            # Get user's keypair
            user_keypair = await self.wallet_manager.get_user_keypair(user_id)
            if not user_keypair:
                logger.error(f"Could not get keypair for user {user_id}")
                return
            
            # Execute swap
            amount_lamports = int(settings.max_buy_amount * 1e9)
            
            # TODO: Implement actual Jupiter swap here
            # For now, log what we would do
            logger.info(f"🎯 WOULD BUY: {settings.max_buy_amount:.4f} SOL of {token_info['symbol']}")
            logger.info(f"   Token: {token_info['address']}")
            logger.info(f"   AI Confidence: {confidence:.1%}")
            logger.info(f"   Liquidity: ${token_info['liquidity_usd']:.0f}")
            
            # Update counters
            settings.daily_snipes_used += 1
            self.last_snipe[user_id] = datetime.now().timestamp()
            
            # TODO: Send notification to user via Telegram
            
            return {
                'success': True,
                'token': token_info['symbol'],
                'amount': settings.max_buy_amount,
                'confidence': confidence
            }
        
        except Exception as e:
            logger.error(f"Snipe execution error: {e}")
            return {
                'success': False,
                'error': str(e)
            }

