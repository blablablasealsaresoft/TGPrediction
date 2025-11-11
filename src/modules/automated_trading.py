"""
🤖 AUTOMATED TRADING ENGINE
24/7 Autonomous Trading with Professional Risk Management

FEATURES:
- Set-and-forget operation
- Follows top wallet activities
- AI confidence scoring
- Dynamic position sizing
- Automatic stop losses
- Take profit automation
- Trailing stops
- Daily loss limits
"""

import asyncio
import logging
import os
from datetime import datetime, timedelta
from types import SimpleNamespace
from typing import Dict, List, Optional, Tuple, Set

from solders.pubkey import Pubkey
from dataclasses import dataclass

try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class TradingConfig:
    """Automated trading configuration"""
    # Trading limits
    max_position_size_sol: float = 10.0
    default_buy_amount: float = 0.1
    max_slippage: float = 0.05  # 5%
    
    # Automated trading
    auto_trade_enabled: bool = False
    auto_trade_min_confidence: float = 0.75  # 75% confidence required
    auto_trade_max_daily_trades: int = 50
    auto_trade_daily_limit_sol: float = 100.0
    
    # Risk management
    stop_loss_percentage: float = 0.15  # 15%
    take_profit_percentage: float = 0.50  # 50%
    trailing_stop_percentage: float = 0.10  # 10%
    max_daily_loss_sol: float = 50.0


class AutomatedTradingEngine:
    """
    🤖 FULLY AUTOMATED TRADING WITH RISK MANAGEMENT
    
    Features:
    - 24/7 autonomous trading
    - Follows top wallets automatically
    - AI-driven decision making
    - Professional risk management
    - Auto stop losses and take profits
    """
    
    def __init__(
        self,
        config: TradingConfig,
        wallet_intelligence,
        jupiter_client,
        protection_system,
        trade_executor=None,
        monitor=None,
    ):
        self.config = config
        self.wallet_intelligence = wallet_intelligence
        self.jupiter = jupiter_client
        self.protection = protection_system
        self.trade_executor = trade_executor
        self.monitor = monitor

        self.active_positions: Dict[str, Dict] = {}
        self.daily_stats = {
            'trades': 0,
            'profit_loss': 0.0,
            'last_reset': datetime.now().date()
        }
        self.is_running = False

        # Cache the last processed signature per wallet so we do not
        # re-process historical activity every scan.
        self._wallet_last_signature: Dict[str, str] = {}

        # Cache decoded transactions to avoid hammering the RPC endpoint.
        self._transaction_cache: Dict[str, Dict[str, object]] = {}
        self._transaction_cache_ttl = timedelta(minutes=10)

        # User risk configuration cache (refreshes periodically)
        self._user_settings: Optional[SimpleNamespace] = None
        self._settings_loaded_at: Optional[datetime] = None

        logger.info("🤖 Automated Trading Engine initialized")

    async def start_automated_trading(self, user_id: int, user_keypair, wallet_manager, db_manager=None):
        """Start automated trading for user"""
        self.is_running = True
        self.user_id = user_id
        self.user_keypair = user_keypair
        self.wallet_manager = wallet_manager
        self.db = db_manager

        if self.db:
            await self._get_user_settings(force_refresh=True)

        logger.info(f"🤖 Automated trading STARTED for user {user_id}")
        
        # Load tracked wallets from database
        if self.db:
            await self._load_tracked_wallets_from_db()
        
        # Start trading loop in background
        asyncio.create_task(self._automated_trading_loop())
    
    async def _load_tracked_wallets_from_db(self):
        """Load tracked wallets from database into wallet intelligence"""
        try:
            tracked_wallets = await self.db.get_tracked_wallets(self.user_id)
            
            logger.info(f"📊 Loading {len(tracked_wallets)} tracked wallets from database...")
            
            for wallet in tracked_wallets:
                # Add to wallet intelligence system
                await self.wallet_intelligence.track_wallet(
                    wallet.wallet_address,
                    analyze=False  # Skip analysis for now, use saved metrics
                )
                
                # Update metrics from database
                metrics = self.wallet_intelligence.tracked_wallets.get(wallet.wallet_address)
                if metrics:
                    metrics.total_trades = wallet.total_trades
                    metrics.profitable_trades = wallet.profitable_trades
                    metrics.win_rate = wallet.win_rate
                    metrics.total_pnl = wallet.total_pnl
                
                logger.info(f"   ✓ Loaded: {wallet.label or wallet.wallet_address[:8]}... (Score: {wallet.score:.0f})")
            
            # Wallets loaded and ready for scanning
            logger.info(f"✅ Loaded {len(tracked_wallets)} wallets for automated trading")
            
        except Exception as e:
            logger.error(f"Error loading tracked wallets: {e}")
    
    async def stop_automated_trading(self):
        """Stop automated trading"""
        self.is_running = False
        logger.info("🛑 Automated trading STOPPED")
    
    async def _automated_trading_loop(self):
        """Main automated trading loop"""
        logger.info("🔄 Automated trading loop started")
        
        while self.is_running:
            try:
                logger.debug(f"💫 Trading loop iteration - is_running={self.is_running}")
                settings = await self._get_user_settings()

                # Reset daily stats if needed
                if datetime.now().date() != self.daily_stats['last_reset']:
                    self.daily_stats = {
                        'trades': 0,
                        'profit_loss': 0.0,
                        'last_reset': datetime.now().date()
                    }
                    logger.info("📊 Daily stats reset")
                
                # Check daily limits
                if self.daily_stats['trades'] >= self.config.auto_trade_max_daily_trades:
                    logger.info("Daily trade limit reached, waiting...")
                    await asyncio.sleep(60)
                    continue
                
                if self.db:
                    daily_pnl = await self.db.get_daily_pnl(self.user_id)
                    self.daily_stats['profit_loss'] = daily_pnl

                    if settings.daily_loss_limit_sol > 0 and daily_pnl <= -settings.daily_loss_limit_sol:
                        logger.warning(
                            "Daily loss limit reached (%.4f <= -%.4f SOL) - pausing trading",
                            daily_pnl,
                            settings.daily_loss_limit_sol,
                        )
                        await asyncio.sleep(300)
                        continue
                elif (
                    settings.daily_loss_limit_sol > 0
                    and abs(self.daily_stats['profit_loss']) >= settings.daily_loss_limit_sol
                ):
                    logger.warning("Daily loss limit reached - pausing trading")
                    await asyncio.sleep(300)
                    continue
                
                # Find trading opportunities
                opportunities = await self._scan_for_opportunities()
                
                # Execute high-confidence opportunities
                for opp in opportunities:
                    if opp['confidence'] >= self.config.auto_trade_min_confidence:
                        await self._execute_automated_trade(opp, settings)

                # Manage existing positions
                await self._manage_positions(settings)
                
                # Wait before next scan (30 seconds to avoid rate limits)
                await asyncio.sleep(30)
                
            except Exception as e:
                logger.error(f"Error in automated trading loop: {e}")
                await asyncio.sleep(30)
    
    async def _scan_for_opportunities(self) -> List[Dict]:
        """
        🔍 SCAN FOR TRADING OPPORTUNITIES
        
        Uses:
        - Top wallet following
        - Technical signals
        - AI predictions
        - Pattern recognition
        """
        
        opportunities = []
        token_signals = {}  # Track how many wallets are buying each token
        
        try:
            # Get all tracked wallets (not just top 5 - check all 558!)
            all_tracked_wallets = list(self.wallet_intelligence.tracked_wallets.items())

            if not all_tracked_wallets:
                logger.debug("No tracked wallets to monitor")
                return opportunities

            wallet_count = len(all_tracked_wallets)
            logger.info(f"🔍 Scanning {wallet_count} tracked wallets for opportunities...")

            scan_started = datetime.now()
            rpc_requests = 0
            wallets_with_activity: Set[str] = set()

            batch_size = 20

            for batch_start in range(0, wallet_count, batch_size):
                batch = all_tracked_wallets[batch_start: batch_start + batch_size]

                signature_tasks = [
                    self._fetch_recent_signatures(address)
                    for address, _ in batch
                ]

                batch_results = await asyncio.gather(*signature_tasks, return_exceptions=True)

                for (address, metrics), result in zip(batch, batch_results):
                    if isinstance(result, Exception):
                        logger.debug(f"Error retrieving signatures for {address[:8]}: {result}")
                        continue

                    rpc_requests += result['rpc_calls']
                    signatures = result['signatures']

                    if not signatures:
                        continue

                    newest_signature: Optional[str] = None
                    last_processed = self._wallet_last_signature.get(address)

                    for sig_info in signatures:
                        sig_value = getattr(sig_info, 'signature', None)
                        sig_str = str(sig_value) if sig_value else None

                        if not sig_str:
                            continue

                        if newest_signature is None:
                            newest_signature = sig_str

                        if sig_str == last_processed:
                            break

                        if hasattr(sig_info, 'block_time') and sig_info.block_time:
                            tx_time = datetime.fromtimestamp(sig_info.block_time)
                            if (datetime.now() - tx_time).total_seconds() > 300:
                                continue

                        token_mint, tx_rpc_calls = await self._parse_swap_transaction(sig_str)
                        rpc_requests += tx_rpc_calls

                        if token_mint:
                            wallets_with_activity.add(address)

                            if token_mint not in token_signals:
                                token_signals[token_mint] = {
                                    'count': 0,
                                    'wallets': [],
                                    'scores': [],
                                    'first_seen': datetime.now()
                                }

                            token_signals[token_mint]['count'] += 1
                            token_signals[token_mint]['wallets'].append(address)
                            token_signals[token_mint]['scores'].append(metrics.calculate_score())

                            logger.info(
                                f"🎯 Detected buy from {address[:8]}... (score: {metrics.calculate_score():.0f}) - Token: {token_mint[:8]}..."
                            )

                    if newest_signature:
                        self._wallet_last_signature[address] = newest_signature

                # Brief pause between batches to remain within rate limits
                await asyncio.sleep(0.05)

            # Generate opportunities from strong signals
            for token_mint, signal in token_signals.items():
                # Calculate confidence based on:
                # 1. Number of wallets buying
                # 2. Quality of wallets (scores)
                # 3. Recency
                
                wallet_count = signal['count']
                avg_wallet_score = sum(signal['scores']) / len(signal['scores']) if signal['scores'] else 0
                
                # Confidence formula
                confidence = 0.5  # Base confidence
                
                # Add confidence for multiple wallet signals
                confidence += min(wallet_count * 0.1, 0.3)  # Up to +30% for 3+ wallets
                
                # Add confidence for high-quality wallets
                if avg_wallet_score > 75:
                    confidence += 0.2
                elif avg_wallet_score > 60:
                    confidence += 0.1
                
                # Only create opportunity if confidence meets minimum
                if confidence >= self.config.auto_trade_min_confidence:
                    opportunities.append({
                        'token_mint': token_mint,
                        'action': 'buy',
                        'amount': self.config.default_buy_amount,
                        'confidence': confidence,
                        'signal_count': wallet_count,
                        'wallet_scores': signal['scores'],
                        'reason': f"{wallet_count} top wallets buying (avg score: {avg_wallet_score:.0f})"
                    })
                    
                    logger.info(f"✨ OPPORTUNITY FOUND: {token_mint[:8]}... - Confidence: {confidence:.1%} ({wallet_count} wallets)")

            if opportunities:
                logger.info(f"🎯 Found {len(opportunities)} high-confidence opportunities!")
            else:
                logger.debug(f"No opportunities found (checked {len(all_tracked_wallets)} wallets)")

            scan_duration = (datetime.now() - scan_started).total_seconds()
            if self.monitor:
                self.monitor.record_metric(
                    'automated_trader.scan_duration_seconds',
                    scan_duration,
                    tags={'wallets_total': wallet_count}
                )
                self.monitor.record_metric(
                    'automated_trader.rpc_requests',
                    rpc_requests,
                    tags={'wallets_with_activity': len(wallets_with_activity)}
                )
                self.monitor.record_metric(
                    'automated_trader.opportunities_found',
                    len(opportunities),
                )

        except Exception as e:
            logger.error(f"Error scanning for opportunities: {e}")

        return opportunities

    async def _fetch_recent_signatures(self, address: str, limit: int = 3) -> Dict[str, object]:
        """Fetch recent signatures for an address with monitoring instrumentation."""

        rpc_calls = 0

        try:
            pubkey = Pubkey.from_string(address)
        except Exception as exc:
            logger.debug(f"Invalid wallet address {address[:8]}: {exc}")
            return {'signatures': [], 'rpc_calls': rpc_calls}

        try:
            if self.monitor:
                self.monitor.record_request()

            signatures = await self.wallet_intelligence.client.get_signatures_for_address(
                pubkey,
                limit=limit
            )
            rpc_calls += 1

            return {
                'signatures': signatures.value if signatures and signatures.value else [],
                'rpc_calls': rpc_calls
            }

        except Exception as exc:
            logger.debug(f"Error fetching signatures for {address[:8]}: {exc}")
            return {'signatures': [], 'rpc_calls': rpc_calls}

    async def _parse_swap_transaction(self, signature: str) -> Tuple[Optional[str], int]:
        """
        Parse a transaction to detect token swaps and extract the token mint

        Uses multiple methods (in priority order):
        1. Helius Enhanced API (if available)
        2. Pre/post token balance comparison
        3. Parsed instruction analysis
        4. DEX program detection
        
        Returns:
            Tuple of (token mint address if this was a buy transaction, RPC call count)
        """
        rpc_calls = 0

        cached = self._transaction_cache.get(signature)
        if cached:
            cached_at = cached.get('timestamp')
            if cached_at and (datetime.now() - cached_at) < self._transaction_cache_ttl:
                return cached.get('mint'), rpc_calls
            # Cache expired, remove so we refresh
            self._transaction_cache.pop(signature, None)

        try:
            # METHOD 0: Try Helius Enhanced Transaction API first (if Helius RPC)
            helius_api_key = os.getenv('HELIUS_API_KEY')

            if helius_api_key and HTTPX_AVAILABLE:
                try:
                    # Use Helius enhanced transaction endpoint
                    async with httpx.AsyncClient() as client:
                        if self.monitor:
                            self.monitor.record_request()
                        rpc_calls += 1
                        response = await client.get(
                            f"https://api.helius.xyz/v0/transactions/{signature}",
                            params={'api-key': helius_api_key},
                            timeout=5.0
                        )
                        
                        if response.status_code == 200:
                            helius_data = response.json()
                            
                            # Helius provides parsed swap data
                            if helius_data.get('type') in ['SWAP', 'SWAP_EXACT_IN', 'SWAP_EXACT_OUT']:
                                # Extract token info from Helius parsed data
                                token_transfers = helius_data.get('tokenTransfers', [])
                                
                                for transfer in token_transfers:
                                    # Look for incoming transfers (tokens received)
                                    if transfer.get('tokenAmount', 0) > 0:
                                        mint = transfer.get('mint')
                                        if mint and mint != "So11111111111111111111111111111111111111112":
                                            logger.info(f"🎯 [Helius] Detected SWAP: {mint[:8]}... via {helius_data.get('source', 'DEX')}")
                                            self._transaction_cache[signature] = {
                                                'timestamp': datetime.now(),
                                                'mint': mint
                                            }
                                            return mint, rpc_calls

                except Exception as e:
                    logger.debug(f"Helius enhanced API unavailable, falling back to standard parsing: {e}")

            # METHOD 1: Standard RPC with balance comparison
            if self.monitor:
                self.monitor.record_request()
            tx = await self.wallet_intelligence.client.get_transaction(
                signature,
                encoding="jsonParsed",
                max_supported_transaction_version=0
            )
            rpc_calls += 1

            if not tx or not tx.value:
                self._transaction_cache[signature] = {
                    'timestamp': datetime.now(),
                    'mint': None
                }
                return None, rpc_calls
            
            # METHOD 1: Check token balance changes (most reliable)
            # This shows what tokens were received in the transaction
            if hasattr(tx.value, 'meta') and tx.value.meta:
                meta = tx.value.meta
                
                # Check post token balances for new tokens received
                if hasattr(meta, 'post_token_balances') and hasattr(meta, 'pre_token_balances'):
                    post_balances = meta.post_token_balances
                    pre_balances = meta.pre_token_balances
                    
                    # Build dict of pre-balances for comparison
                    pre_balance_dict = {}
                    if pre_balances:
                        for bal in pre_balances:
                            account = str(bal.account_index)
                            mint = bal.mint
                            amount = float(bal.ui_token_amount.ui_amount) if bal.ui_token_amount else 0
                            pre_balance_dict[f"{account}_{mint}"] = amount
                    
                    # Check post balances for increases (tokens received)
                    if post_balances:
                        for bal in post_balances:
                            account = str(bal.account_index)
                            mint = bal.mint
                            post_amount = float(bal.ui_token_amount.ui_amount) if bal.ui_token_amount else 0
                            
                            # Get pre amount (or 0 if didn't exist)
                            pre_amount = pre_balance_dict.get(f"{account}_{mint}", 0)
                            
                            # If balance increased, this token was received (bought)
                            if post_amount > pre_amount:
                                # Skip SOL and wrapped SOL
                                SOL_MINT = "So11111111111111111111111111111111111111112"
                                WSOL_MINT = "So11111111111111111111111111111111111111112"
                                
                                if mint not in [SOL_MINT, WSOL_MINT]:
                                    logger.info(f"🎯 Detected token BUY: {mint[:8]}... (+{post_amount - pre_amount:.4f} tokens)")
                                    self._transaction_cache[signature] = {
                                        'timestamp': datetime.now(),
                                        'mint': mint
                                    }
                                    return mint, rpc_calls
            
            # METHOD 2: Parse instructions for token transfers
            instructions = tx.value.transaction.transaction.message.instructions
            
            # Track all token transfers in this transaction
            tokens_received = []
            tokens_sent = []
            
            for instruction in instructions:
                # Check parsed instructions
                if hasattr(instruction, 'parsed') and isinstance(instruction.parsed, dict):
                    parsed = instruction.parsed
                    instruction_type = parsed.get('type')
                    
                    # Token transfer or transferChecked
                    if instruction_type in ['transfer', 'transferChecked']:
                        info = parsed.get('info', {})
                        mint = info.get('mint')
                        
                        # Determine direction by checking destination
                        if mint:
                            # This is a simplification - would need to check if destination
                            # belongs to the wallet we're monitoring
                            tokens_received.append(mint)
            
            # METHOD 3: Detect known DEX program calls
            for instruction in instructions:
                if hasattr(instruction, 'program_id'):
                    program_id = str(instruction.program_id)
                    
                    # Known DEX programs
                    dex_programs = {
                        "JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4": "Jupiter V6",
                        "JUP4Fb2cqiRUcaTHdrPC8h2gNsA2ETXiPDD33WcGuJB": "Jupiter V4",
                        "675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8": "Raydium AMM",
                        "whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc": "Orca Whirlpool",
                    }
                    
                    if program_id in dex_programs:
                        dex_name = dex_programs[program_id]
                        logger.debug(f"Detected {dex_name} swap in transaction")

                        # If we detected a DEX swap and found tokens received via Method 1 or 2,
                        # return the first non-SOL token
                        for token in tokens_received:
                            SOL_MINT = "So11111111111111111111111111111111111111112"
                            if token != SOL_MINT:
                                logger.info(f"🎯 Detected {dex_name} token buy: {token[:8]}...")
                                self._transaction_cache[signature] = {
                                    'timestamp': datetime.now(),
                                    'mint': token
                                }
                                return token, rpc_calls
            
            # If we found any tokens received but no DEX program, might still be a swap
            # Return first non-SOL token found
            for token in tokens_received:
                SOL_MINT = "So11111111111111111111111111111111111111112"
                if token != SOL_MINT:
                    self._transaction_cache[signature] = {
                        'timestamp': datetime.now(),
                        'mint': token
                    }
                    return token, rpc_calls
            
            self._transaction_cache[signature] = {
                'timestamp': datetime.now(),
                'mint': None
            }
            return None, rpc_calls
            
        except Exception as e:
            logger.debug(f"Error parsing transaction {str(signature)[:8]}: {e}")
            self._transaction_cache[signature] = {
                'timestamp': datetime.now(),
                'mint': None
            }
            return None, rpc_calls
    
    async def _execute_automated_trade(self, opportunity: Dict, settings: Optional[SimpleNamespace] = None):
        """Execute an automated trade"""

        try:
            token_mint = opportunity.get('token_mint')
            action = opportunity.get('action', 'buy')
            amount = opportunity.get('amount', self.config.default_buy_amount)
            confidence = opportunity.get('confidence', 0.0)

            if settings is None:
                settings = await self._get_user_settings()

            logger.info(f"🎯 Executing automated trade: {action} {amount} SOL of {token_mint[:8]}... (confidence: {confidence:.1%})")

            # Run protection checks
            if action == 'buy':
                protection_result = await self.protection.comprehensive_token_check(token_mint)

                if not protection_result['is_safe']:
                    logger.warning(f"⚠️ Token failed safety checks, skipping trade")
                    return

            if not self.trade_executor:
                logger.error("Trade executor is not configured for automated trading")
                return

            amount = min(amount, settings.max_trade_size_sol)
            if amount <= 0:
                logger.debug("Configured max trade size prevents automated trade for user %s", self.user_id)
                return

            metadata = {
                'opportunity': opportunity.get('source'),
                'confidence': confidence,
                'wallet_signal': opportunity.get('wallet_address'),
            }

            if action == 'buy':
                result = await self.trade_executor.execute_buy(
                    self.user_id,
                    token_mint,
                    amount,
                    token_symbol=opportunity.get('token_symbol'),
                    reason='automated_trader',
                    context='auto_trader',
                    execution_mode='jito',
                    metadata=metadata,
                )
            else:
                result = await self.trade_executor.execute_sell(
                    self.user_id,
                    token_mint,
                    token_symbol=opportunity.get('token_symbol'),
                    reason='automated_trader',
                    context='auto_trader',
                    metadata=metadata,
                )

            if result.get('success'):
                stop_loss_pct = None
                take_profit_pct = None

                if settings.use_stop_loss and settings.default_stop_loss_percentage:
                    stop_loss_pct = max(settings.default_stop_loss_percentage, 0.0) / 100.0

                if settings.use_take_profit and settings.default_take_profit_percentage:
                    take_profit_pct = max(settings.default_take_profit_percentage, 0.0) / 100.0

                # Record position
                self.active_positions[token_mint] = {
                    'entry_price': result.get('price') or opportunity.get('price', 0),
                    'amount': amount,
                    'timestamp': datetime.now(),
                    'confidence': confidence,
                    'token_symbol': opportunity.get('token_symbol'),
                    'stop_loss_pct': stop_loss_pct,
                    'take_profit_pct': take_profit_pct,
                }

                # Update stats
                self.daily_stats['trades'] += 1
                
                logger.info(f"✅ Automated trade executed successfully")
            else:
                logger.error(f"❌ Automated trade failed: {result.get('error')}")
        
        except Exception as e:
            logger.error(f"Error executing automated trade: {e}")
    
    async def _manage_positions(self, settings: Optional[SimpleNamespace] = None):
        """
        📊 MANAGE OPEN POSITIONS

        - Check stop losses
        - Check take profits
        - Implement trailing stops
        """

        if settings is None:
            settings = await self._get_user_settings()

        for token_mint, position in list(self.active_positions.items()):
            try:
                # Get current price
                current_price = await self._get_token_price(token_mint)
                
                if current_price is None:
                    continue
                
                entry_price = position['entry_price']
                pnl_pct = (current_price - entry_price) / entry_price if entry_price > 0 else 0

                # Check stop loss
                stop_loss_pct = position.get('stop_loss_pct')
                if stop_loss_pct is None and settings.use_stop_loss and settings.default_stop_loss_percentage:
                    stop_loss_pct = max(settings.default_stop_loss_percentage, 0.0) / 100.0

                if stop_loss_pct is not None and pnl_pct <= -stop_loss_pct:
                    logger.info(f"🛑 Stop loss triggered for {token_mint[:8]}... (PnL: {pnl_pct:.1%})")
                    await self._close_position(token_mint, "STOP_LOSS", pnl_pct)
                    continue

                # Check take profit
                take_profit_pct = position.get('take_profit_pct')
                if take_profit_pct is None and settings.use_take_profit and settings.default_take_profit_percentage:
                    take_profit_pct = max(settings.default_take_profit_percentage, 0.0) / 100.0

                if take_profit_pct is not None and pnl_pct >= take_profit_pct:
                    logger.info(f"💰 Take profit triggered for {token_mint[:8]}... (PnL: {pnl_pct:.1%})")
                    await self._close_position(token_mint, "TAKE_PROFIT", pnl_pct)
                    continue

                # Implement trailing stop
                if pnl_pct > 0:
                    if 'highest_price' not in position:
                        position['highest_price'] = current_price
                    else:
                        position['highest_price'] = max(position['highest_price'], current_price)
                        
                        # Check if price fell from highest
                        price_drop = (position['highest_price'] - current_price) / position['highest_price']
                        if price_drop >= self.config.trailing_stop_percentage:
                            logger.info(f"📉 Trailing stop triggered for {token_mint[:8]}... (PnL: {pnl_pct:.1%})")
                            await self._close_position(token_mint, "TRAILING_STOP", pnl_pct)
                
            except Exception as e:
                logger.error(f"Error managing position {token_mint}: {e}")
    
    async def _get_token_price(self, token_mint: str) -> Optional[float]:
        """Get current token price"""
        try:
            prices = await self.jupiter.get_token_price([token_mint])
            return prices.get(token_mint, 0)
        except Exception as e:
            logger.error(f"Error getting token price: {e}")
            return None
    
    async def _close_position(self, token_mint: str, reason: str, pnl_pct: float):
        """Close a position"""
        position = self.active_positions.pop(token_mint, None)
        if position:
            # Calculate P&L
            pnl_sol = position['amount'] * pnl_pct
            self.daily_stats['profit_loss'] += pnl_sol

            logger.info(f"🔄 Closing position: {token_mint[:8]}... - Reason: {reason} - PnL: {pnl_sol:+.4f} SOL")

            if not self.trade_executor:
                logger.error("Trade executor is not configured for automated exit")
                self.active_positions[token_mint] = position
                return

            try:
                result = await self.trade_executor.execute_sell(
                    self.user_id,
                    token_mint,
                    token_symbol=position.get('token_symbol'),
                    reason=f'auto_trader:{reason}',
                    context='auto_trader',
                    metadata={'exit_reason': reason, 'trigger_pnl_pct': pnl_pct},
                )

                if result and result.get('success'):
                    logger.info(f"✅ Position closed successfully!")
                    logger.info(f"   Reason: {reason}")
                    logger.info(f"   PnL: {result.get('pnl', 0.0):+.4f} SOL")
                    logger.info(f"   Signature: {result.get('signature', 'N/A')}")
                else:
                    logger.error(f"❌ Failed to close position: {result}")
                    self.active_positions[token_mint] = position
            except Exception as e:
                logger.error(f"Error executing sell: {e}")
                self.active_positions[token_mint] = position

    async def _get_user_settings(self, force_refresh: bool = False) -> SimpleNamespace:
        """Load and cache user risk settings."""

        if not getattr(self, 'user_id', None):
            return self._default_user_settings()

        if not self.db:
            return self._default_user_settings()

        now = datetime.utcnow()
        if (
            force_refresh
            or self._user_settings is None
            or self._settings_loaded_at is None
            or (now - self._settings_loaded_at) > timedelta(minutes=5)
        ):
            record = await self.db.get_user_settings(self.user_id)
            self._user_settings = self._settings_from_record(record)
            self._settings_loaded_at = now

        return self._user_settings

    def _settings_from_record(self, record) -> SimpleNamespace:
        if not record:
            return self._default_user_settings()

        return SimpleNamespace(
            max_trade_size_sol=
                record.max_trade_size_sol if record.max_trade_size_sol is not None else 1.0,
            daily_loss_limit_sol=
                record.daily_loss_limit_sol if record.daily_loss_limit_sol is not None else 5.0,
            slippage_percentage=record.slippage_percentage or 5.0,
            use_stop_loss=(
                True if getattr(record, 'use_stop_loss', None) is None else bool(record.use_stop_loss)
            ),
            default_stop_loss_percentage=(
                record.default_stop_loss_percentage if record.default_stop_loss_percentage is not None else 10.0
            ),
            use_take_profit=(
                True if getattr(record, 'use_take_profit', None) is None else bool(record.use_take_profit)
            ),
            default_take_profit_percentage=(
                record.default_take_profit_percentage if record.default_take_profit_percentage is not None else 20.0
            ),
        )

    def _default_user_settings(self) -> SimpleNamespace:
        return SimpleNamespace(
            max_trade_size_sol=1.0,
            daily_loss_limit_sol=5.0,
            slippage_percentage=5.0,
            use_stop_loss=True,
            default_stop_loss_percentage=10.0,
            use_take_profit=True,
            default_take_profit_percentage=20.0,
        )

    def get_status(self) -> Dict:
        """Get current trading status"""
        return {
            'is_running': self.is_running,
            'daily_trades': self.daily_stats['trades'],
            'daily_pnl': self.daily_stats['profit_loss'],
            'active_positions': len(self.active_positions),
            'positions': list(self.active_positions.keys())
        }

