"""
SOCIAL TRADING MARKETPLACE
Revolutionary copy trading and community intelligence system

UNIQUE DIFFERENTIATORS:
1. Copy top traders automatically
2. Community-driven token intelligence
3. Trader reputation system
4. Strategy marketplace
5. Profit sharing for shared strategies
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional, Set
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class TraderTier(Enum):
    """Trader reputation tiers"""
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"
    DIAMOND = "diamond"


@dataclass
class TraderProfile:
    """Public trader profile"""
    user_id: int
    username: str
    tier: TraderTier
    total_trades: int
    win_rate: float
    total_pnl: float
    followers: int
    reputation_score: float
    verified: bool
    strategies_shared: int
    total_profit_shared: float


class SocialTradingMarketplace:
    """
    Marketplace for copy trading and strategy sharing
    """
    
    def __init__(self, database_manager):
        self.db = database_manager
        self.traders: Dict[int, TraderProfile] = {}
        self.copy_relationships: Dict[int, Set[int]] = {}  # follower_id -> trader_ids
        self.active_copies: Dict[int, Dict[int, Dict]] = {}  # follower_id -> trader_id -> settings
        self.leaderboard_cache: List[TraderProfile] = []
        self.last_leaderboard_update = datetime.utcnow()
        self._initialized = False
        self._init_lock = asyncio.Lock()
        self.trade_executor = None

    async def initialize(self):
        """Load trader and copy trading state from the database"""
        async with self._init_lock:
            if self._initialized:
                return

            await self._load_traders_from_db()
            await self._load_copy_relationships()
            await self._update_leaderboard()

            self._initialized = True

    async def _ensure_initialized(self):
        if not self._initialized:
            await self.initialize()

    def attach_trade_executor(self, trade_executor) -> None:
        """Attach the shared trade execution service for follower trades."""
        self.trade_executor = trade_executor

    async def _load_traders_from_db(self):
        self.traders.clear()
        trader_records = await self.db.get_trader_profiles()

        for record in trader_records:
            profile = self._record_to_profile(record)
            self.traders[profile.user_id] = profile

    async def _load_copy_relationships(self):
        self.copy_relationships.clear()
        self.active_copies.clear()

        relationships = await self.db.get_copy_relationships(only_enabled=False)

        for rel in relationships:
            trader_id = rel.copy_trader_id
            if trader_id is None:
                continue

            follower_id = rel.user_id
            self.active_copies.setdefault(follower_id, {})[trader_id] = {
                'copy_percentage': rel.copy_percentage or 100.0,
                'max_copy_amount': rel.copy_amount_sol or 0.1,
                'max_daily_trades': rel.copy_max_daily_trades or 10,
                'enabled': bool(rel.copy_enabled),
                'started_at': rel.copy_started_at or datetime.utcnow(),
                'total_copied': rel.copy_total_trades or 0,
                'total_profit': rel.copy_total_profit or 0.0
            }

            if rel.copy_enabled:
                self.copy_relationships.setdefault(follower_id, set()).add(trader_id)

    def _record_to_profile(self, record) -> TraderProfile:
        """Convert a tracked wallet record into a trader profile"""
        tier_key = (record.trader_tier or 'bronze').upper()
        tier = TraderTier.__members__.get(tier_key, TraderTier.BRONZE)

        return TraderProfile(
            user_id=record.user_id,
            username=record.label or f"trader_{record.user_id}",
            tier=tier,
            total_trades=record.total_trades or 0,
            win_rate=record.win_rate or 0.0,
            total_pnl=record.total_pnl or 0.0,
            followers=record.followers or 0,
            reputation_score=record.reputation_score or 0.0,
            verified=bool(record.is_verified),
            strategies_shared=record.strategies_shared or 0,
            total_profit_shared=record.total_profit_shared or 0.0
        )

    async def register_trader(
        self,
        user_id: int,
        username: str
    ) -> TraderProfile:
        """Register a new trader in the marketplace"""

        await self._ensure_initialized()

        # Check if already registered
        if user_id in self.traders:
            profile = self.traders[user_id]
            if profile.username != username:
                await self.db.update_trader_profile(user_id, {'label': username})
                profile.username = username
            return profile

        record = await self.db.upsert_trader_profile(user_id, username)
        profile = self._record_to_profile(record)
        self.traders[user_id] = profile

        await self._update_leaderboard()
        logger.info(f"Trader registered: {username}")

        return profile
    
    async def update_trader_stats(
        self,
        user_id: int,
        trade_result: Dict
    ):
        """Update trader statistics after a trade"""

        await self._ensure_initialized()

        if user_id not in self.traders:
            return

        profile = self.traders[user_id]

        # Update stats
        profile.total_trades += 1
        profile.total_pnl += trade_result.get('pnl', 0)
        
        # Recalculate win rate
        stats = await self.db.get_user_stats(user_id, days=30)
        profile.win_rate = stats.get('win_rate', 0)
        
        # Update reputation score
        profile.reputation_score = self._calculate_reputation_score(profile)

        # Update tier
        profile.tier = self._calculate_tier(profile)

        # Persist to database
        await self.db.update_trader_profile(user_id, {
            'total_trades': profile.total_trades,
            'total_pnl': profile.total_pnl,
            'win_rate': profile.win_rate,
            'reputation_score': profile.reputation_score,
            'trader_tier': profile.tier.value,
            'followers': profile.followers,
            'strategies_shared': profile.strategies_shared,
            'total_profit_shared': profile.total_profit_shared,
        })

        # Update leaderboard
        await self._update_leaderboard()
    
    def _calculate_reputation_score(self, profile: TraderProfile) -> float:
        """
        Calculate trader reputation score (0-100)
        
        Based on:
        - Win rate (40%)
        - Total PnL (30%)
        - Consistency (20%)
        - Community engagement (10%)
        """
        # Win rate component (0-40 points)
        win_rate_score = min(profile.win_rate, 100) * 0.4
        
        # PnL component (0-30 points)
        pnl_score = min(max(profile.total_pnl / 10, 0), 30)
        
        # Consistency component (0-20 points)
        # More trades = more consistent
        consistency_score = min(profile.total_trades / 100 * 20, 20)
        
        # Community component (0-10 points)
        community_score = min(
            (profile.followers * 0.1) + (profile.strategies_shared * 2),
            10
        )
        
        return win_rate_score + pnl_score + consistency_score + community_score
    
    def _calculate_tier(self, profile: TraderProfile) -> TraderTier:
        """Calculate trader tier based on reputation"""
        score = profile.reputation_score
        
        if score >= 90:
            return TraderTier.DIAMOND
        elif score >= 75:
            return TraderTier.PLATINUM
        elif score >= 60:
            return TraderTier.GOLD
        elif score >= 40:
            return TraderTier.SILVER
        else:
            return TraderTier.BRONZE
    
    async def start_copying(
        self,
        follower_id: int,
        trader_id: int,
        copy_percentage: float = 100.0,
        max_copy_amount: float = 1.0
    ) -> bool:
        """
        Start copying a trader
        
        Args:
            follower_id: User who wants to copy
            trader_id: Trader to copy
            copy_percentage: Percentage of trader's position size to copy
            max_copy_amount: Maximum amount to copy per trade
        
        Returns:
            Success status
        """
        settings = {
            'copy_percentage': copy_percentage,
            'max_copy_amount': max_copy_amount,
            'max_daily_trades': 10
        }
        return await self.start_copying_trader(follower_id, trader_id, settings)
    
    async def is_copying(self, follower_id: int, trader_id: int) -> bool:
        """Check if follower is copying a trader"""
        await self._ensure_initialized()
        if follower_id not in self.copy_relationships:
            return False
        return trader_id in self.copy_relationships[follower_id]
    
    async def should_copy_trade(
        self,
        follower_id: int,
        trader_id: int,
        trade_data: Dict
    ) -> bool:
        """
        Determine if a follower should copy a trader's trade

        Args:
            follower_id: User who is copying
            trader_id: Trader being copied
            trade_data: Trade information

        Returns:
            True if should copy
        """
        await self._ensure_initialized()

        # Check if actively copying
        if not await self.is_copying(follower_id, trader_id):
            return False

        # Check copy settings
        settings = self.active_copies.get(follower_id, {}).get(trader_id)

        if not settings or not settings.get('enabled', False):
            return False

        # Check if copy amount exceeds max
        copy_percentage = settings.get('copy_percentage', 100) / 100
        copy_amount = trade_data.get('amount_sol', 0) * copy_percentage

        if copy_amount > settings.get('max_copy_amount', 1.0):
            return False

        return True
    
    async def start_copying_trader(
        self,
        follower_id: int,
        trader_id: int,
        settings: Dict
    ) -> bool:
        """
        Start copying a trader's trades

        Args:
            follower_id: User who wants to copy
            trader_id: Trader to copy
            settings: Copy settings (amount per trade, etc.)
        """
        await self._ensure_initialized()

        # Validation
        if trader_id not in self.traders:
            logger.error(f"Trader {trader_id} not found")
            return False

        if follower_id == trader_id:
            logger.error("Cannot copy yourself")
            return False

        max_copy_amount = settings.get('max_copy_amount', settings.get('amount_per_trade', 0.1))
        copy_percentage = settings.get('copy_percentage', 100.0)
        max_daily_trades = settings.get('max_daily_trades', 10)

        relationship, activated = await self.db.set_copy_relationship(
            follower_id,
            trader_id,
            {
                'max_copy_amount': max_copy_amount,
                'copy_percentage': copy_percentage,
                'max_daily_trades': max_daily_trades,
                'label': settings.get('label', f'Copy {trader_id}')
            }
        )

        self.copy_relationships.setdefault(follower_id, set()).add(trader_id)
        self.active_copies.setdefault(follower_id, {})[trader_id] = {
            'copy_percentage': relationship.copy_percentage or copy_percentage,
            'max_copy_amount': relationship.copy_amount_sol or max_copy_amount,
            'max_daily_trades': relationship.copy_max_daily_trades or max_daily_trades,
            'enabled': True,
            'started_at': relationship.copy_started_at or datetime.utcnow(),
            'total_copied': relationship.copy_total_trades or 0,
            'total_profit': relationship.copy_total_profit or 0.0
        }

        # Update follower count if this is a new active relationship
        if activated and trader_id in self.traders:
            self.traders[trader_id].followers += 1
            await self.db.increment_trader_followers(trader_id, 1)

        logger.info(f"User {follower_id} started copying trader {trader_id}")
        return True
    
    async def stop_copying_trader(
        self,
        follower_id: int,
        trader_id: int
    ) -> bool:
        """Stop copying a trader"""

        await self._ensure_initialized()

        was_enabled = await self.db.disable_copy_relationship(follower_id, trader_id)

        if follower_id in self.copy_relationships:
            self.copy_relationships[follower_id].discard(trader_id)
            if not self.copy_relationships[follower_id]:
                del self.copy_relationships[follower_id]

        if follower_id in self.active_copies and trader_id in self.active_copies[follower_id]:
            self.active_copies[follower_id][trader_id]['enabled'] = False

        if was_enabled and trader_id in self.traders:
            self.traders[trader_id].followers = max(0, self.traders[trader_id].followers - 1)
            await self.db.increment_trader_followers(trader_id, -1)

        logger.info(f"User {follower_id} stopped copying trader {trader_id}")
        return True
    
    async def execute_copy_trade(
        self,
        trader_id: int,
        trade_data: Dict
    ) -> List[Dict]:
        """Backward-compatible wrapper for copy trade execution."""

        return await self.handle_trader_execution(trader_id, trade_data)

    async def handle_trader_execution(
        self,
        trader_id: int,
        trade_data: Dict[str, Any]
    ) -> List[Dict]:
        """Propagate trader executions to eligible followers."""

        await self._ensure_initialized()

        trade_type = (trade_data or {}).get('trade_type') or trade_data.get('action') or 'buy'
        trade_type = trade_type.lower()

        if trade_type == 'buy':
            return await self._execute_copy_buys(trader_id, trade_data)
        if trade_type == 'sell':
            return await self._execute_copy_sells(trader_id, trade_data)

        logger.debug('Unsupported trade type for copy trading: %s', trade_type)
        return []

    async def _execute_copy_buys(
        self,
        trader_id: int,
        trade_data: Dict[str, Any]
    ) -> List[Dict]:
        token_mint = trade_data.get('token_mint')
        amount_sol = trade_data.get('amount_sol', 0.0)

        if not token_mint or amount_sol <= 0:
            return []

        results: List[Dict] = []

        for follower_id, traders in list(self.copy_relationships.items()):
            if trader_id not in traders:
                continue

            copy_settings = self.active_copies.get(follower_id, {}).get(trader_id)
            if not copy_settings or not copy_settings.get('enabled', False):
                continue

            if copy_settings.get('total_copied', 0) >= copy_settings.get('max_daily_trades', 10):
                continue

            percentage = (copy_settings.get('copy_percentage', 100.0) or 0.0) / 100.0
            base_amount = amount_sol * percentage
            max_amount = copy_settings.get('max_copy_amount', base_amount)
            copy_amount = min(base_amount, max_amount)

            if copy_amount <= 0:
                continue

            entry = {
                'follower_id': follower_id,
                'trader_id': trader_id,
                'token_mint': token_mint,
                'token_symbol': trade_data.get('token_symbol'),
                'amount_sol': copy_amount,
                'timestamp': datetime.utcnow(),
                'context': trade_data.get('context'),
            }

            if not self.trade_executor:
                entry['status'] = 'pending_executor'
                results.append(entry)
                continue

            try:
                execution = await self.trade_executor.execute_buy(
                    follower_id,
                    token_mint,
                    copy_amount,
                    token_symbol=trade_data.get('token_symbol'),
                    reason='copy_trade',
                    context='copy_trade',
                    metadata={
                        'copied_from': trader_id,
                        'source_position': trade_data.get('position_id'),
                        'origin_signature': trade_data.get('signature'),
                    },
                )
            except Exception as exc:  # pragma: no cover - defensive
                execution = {'success': False, 'error': str(exc)}

            entry['execution'] = execution
            results.append(entry)

            if execution.get('success'):
                copy_settings['total_copied'] = copy_settings.get('total_copied', 0) + 1
                await self.db.update_copy_relationship(
                    follower_id,
                    trader_id,
                    {
                        'copy_total_trades': copy_settings['total_copied']
                    }
                )

        if results:
            logger.info("Executed %d copy buys for trader %s", len(results), trader_id)

        return results

    async def _execute_copy_sells(
        self,
        trader_id: int,
        trade_data: Dict[str, Any]
    ) -> List[Dict]:
        token_mint = trade_data.get('token_mint')
        if not token_mint:
            return []

        results: List[Dict] = []

        for follower_id, traders in list(self.copy_relationships.items()):
            if trader_id not in traders:
                continue

            copy_settings = self.active_copies.get(follower_id, {}).get(trader_id)
            if not copy_settings or not copy_settings.get('enabled', False):
                continue

            entry = {
                'follower_id': follower_id,
                'trader_id': trader_id,
                'token_mint': token_mint,
                'token_symbol': trade_data.get('token_symbol'),
                'timestamp': datetime.utcnow(),
                'context': trade_data.get('context'),
            }

            if not self.trade_executor:
                entry['status'] = 'pending_executor'
                results.append(entry)
                continue

            try:
                execution = await self.trade_executor.execute_sell(
                    follower_id,
                    token_mint,
                    token_symbol=trade_data.get('token_symbol'),
                    reason='copy_trade',
                    context='copy_trade',
                    metadata={
                        'copied_from': trader_id,
                        'source_position': trade_data.get('position_id'),
                        'origin_signature': trade_data.get('signature'),
                    },
                )
            except Exception as exc:  # pragma: no cover - defensive
                execution = {'success': False, 'error': str(exc)}

            entry['execution'] = execution
            results.append(entry)

            if execution.get('success'):
                pnl = execution.get('pnl') or 0.0
                copy_settings['total_copied'] = copy_settings.get('total_copied', 0) + 1
                copy_settings['total_profit'] = copy_settings.get('total_profit', 0.0) + pnl
                await self.db.update_copy_relationship(
                    follower_id,
                    trader_id,
                    {
                        'copy_total_trades': copy_settings['total_copied'],
                        'copy_total_profit': copy_settings['total_profit'],
                    }
                )

        if results:
            logger.info("Executed %d copy sells for trader %s", len(results), trader_id)

        return results
    
    async def get_leaderboard(
        self,
        tier: Optional[TraderTier] = None,
        limit: int = 50
    ) -> List[TraderProfile]:
        """
        Get trader leaderboard

        Args:
            tier: Filter by tier
            limit: Number of traders to return
        """
        await self._ensure_initialized()
        # Update cache if stale
        if (datetime.utcnow() - self.last_leaderboard_update).seconds > 300:
            await self._update_leaderboard()
        
        leaderboard = self.leaderboard_cache
        
        # Filter by tier if specified
        if tier:
            leaderboard = [t for t in leaderboard if t.tier == tier]
        
        return leaderboard[:limit]
    
    async def _update_leaderboard(self):
        """Update leaderboard cache"""
        sorted_traders = sorted(
            self.traders.values(),
            key=lambda t: t.reputation_score,
            reverse=True
        )
        
        self.leaderboard_cache = sorted_traders
        self.last_leaderboard_update = datetime.utcnow()
    
    async def get_trader_profile(self, trader_id: int) -> Optional[TraderProfile]:
        """Get detailed trader profile"""
        await self._ensure_initialized()
        return self.traders.get(trader_id)
    
    async def search_traders(
        self,
        min_win_rate: float = 0.0,
        min_trades: int = 0,
        tier: Optional[TraderTier] = None
    ) -> List[TraderProfile]:
        """Search for traders matching criteria"""

        await self._ensure_initialized()
        results = []
        for trader in self.traders.values():
            if trader.win_rate < min_win_rate:
                continue
            if trader.total_trades < min_trades:
                continue
            if tier and trader.tier != tier:
                continue
            
            results.append(trader)
        
        # Sort by reputation
        results.sort(key=lambda t: t.reputation_score, reverse=True)
        
        return results


class StrategyMarketplace:
    """
    Marketplace for buying/selling trading strategies
    """
    
    def __init__(self, database_manager):
        self.db = database_manager
        self.strategies: Dict[str, Dict] = {}
        self.strategy_purchases: Dict[int, Set[str]] = {}
    
    async def publish_strategy(
        self,
        creator_id: int,
        strategy_data: Dict
    ) -> str:
        """
        Publish a trading strategy to marketplace
        
        Args:
            creator_id: Strategy creator
            strategy_data: Strategy details
        
        Returns:
            Strategy ID
        """
        import uuid
        strategy_id = str(uuid.uuid4())
        
        self.strategies[strategy_id] = {
            'id': strategy_id,
            'creator_id': creator_id,
            'name': strategy_data['name'],
            'description': strategy_data['description'],
            'price': strategy_data.get('price', 0.0),  # SOL
            'category': strategy_data.get('category', 'general'),
            'performance': {
                'win_rate': strategy_data.get('win_rate', 0),
                'avg_profit': strategy_data.get('avg_profit', 0),
                'total_trades': strategy_data.get('total_trades', 0)
            },
            'purchases': 0,
            'rating': 0.0,
            'reviews': [],
            'created_at': datetime.utcnow(),
            'code': strategy_data.get('code', ''),  # Strategy logic
            'parameters': strategy_data.get('parameters', {})
        }
        
        logger.info(f"Strategy published: {strategy_data['name']} by user {creator_id}")
        return strategy_id
    
    async def list_strategy(
        self,
        creator_id: int,
        name: str,
        description: str,
        strategy_data: Dict,
        price_sol: float
    ) -> str:
        """
        List a strategy in the marketplace (alias for publish_strategy)
        
        Args:
            creator_id: Strategy creator
            name: Strategy name
            description: Strategy description
            strategy_data: Strategy configuration
            price_sol: Price in SOL
        
        Returns:
            Strategy ID
        """
        full_strategy_data = {
            'name': name,
            'description': description,
            'price': price_sol,
            **strategy_data
        }
        return await self.publish_strategy(creator_id, full_strategy_data)
    
    async def browse_strategies(
        self,
        min_win_rate: float = 0.0,
        sort_by: str = 'popularity'
    ) -> List[Dict]:
        """
        Browse available strategies
        
        Args:
            min_win_rate: Minimum win rate filter
            sort_by: Sort order (popularity, rating, price)
        
        Returns:
            List of strategies
        """
        strategies = list(self.strategies.values())
        
        # Filter by win rate
        strategies = [
            s for s in strategies
            if s['performance'].get('win_rate', 0) >= min_win_rate * 100
        ]
        
        # Sort
        if sort_by == 'popularity':
            strategies.sort(key=lambda x: x['purchases'], reverse=True)
        elif sort_by == 'rating':
            strategies.sort(key=lambda x: x['rating'], reverse=True)
        elif sort_by == 'price':
            strategies.sort(key=lambda x: x['price'])
        
        return strategies
    
    async def purchase_strategy(
        self,
        buyer_id: int,
        strategy_id: str
    ) -> bool:
        """Purchase a strategy"""
        
        if strategy_id not in self.strategies:
            return False
        
        strategy = self.strategies[strategy_id]
        
        # Initialize purchases set
        if buyer_id not in self.strategy_purchases:
            self.strategy_purchases[buyer_id] = set()
        
        # Check if already purchased
        if strategy_id in self.strategy_purchases[buyer_id]:
            logger.info("Strategy already purchased")
            return True
        
        # Add to purchases
        self.strategy_purchases[buyer_id].add(strategy_id)
        strategy['purchases'] += 1
        
        # Process payment (implement payment logic)
        # Transfer SOL from buyer to creator
        
        logger.info(f"User {buyer_id} purchased strategy {strategy_id}")
        return True
    
    async def rate_strategy(
        self,
        user_id: int,
        strategy_id: str,
        rating: float,
        review: str
    ):
        """Rate a purchased strategy"""
        
        if strategy_id not in self.strategies:
            return False
        
        # Check if purchased
        if user_id not in self.strategy_purchases or \
           strategy_id not in self.strategy_purchases[user_id]:
            return False
        
        strategy = self.strategies[strategy_id]
        
        # Add review
        strategy['reviews'].append({
            'user_id': user_id,
            'rating': rating,
            'review': review,
            'timestamp': datetime.utcnow()
        })
        
        # Update average rating
        ratings = [r['rating'] for r in strategy['reviews']]
        strategy['rating'] = sum(ratings) / len(ratings)
        
        logger.info(f"Strategy {strategy_id} rated: {rating}/5")
        return True
    
    async def get_strategy_marketplace(
        self,
        category: Optional[str] = None,
        min_rating: float = 0.0,
        sort_by: str = 'rating'
    ) -> List[Dict]:
        """Get strategies from marketplace"""
        
        strategies = list(self.strategies.values())
        
        # Filter by category
        if category:
            strategies = [s for s in strategies if s['category'] == category]
        
        # Filter by rating
        strategies = [s for s in strategies if s['rating'] >= min_rating]
        
        # Sort
        if sort_by == 'rating':
            strategies.sort(key=lambda s: s['rating'], reverse=True)
        elif sort_by == 'purchases':
            strategies.sort(key=lambda s: s['purchases'], reverse=True)
        elif sort_by == 'performance':
            strategies.sort(
                key=lambda s: s['performance']['win_rate'],
                reverse=True
            )
        
        return strategies


class CommunityIntelligence:
    """
    Crowdsourced token intelligence and sentiment
    """
    
    def __init__(self):
        self.token_ratings: Dict[str, List[Dict]] = {}
        self.token_flags: Dict[str, List[Dict]] = {}
        self.community_signals: Dict[str, Dict] = {}
    
    async def submit_token_rating(
        self,
        user_id: int,
        token_mint: str,
        rating: float,
        notes: str = ""
    ):
        """Submit a token rating"""
        
        if token_mint not in self.token_ratings:
            self.token_ratings[token_mint] = []
        
        self.token_ratings[token_mint].append({
            'user_id': user_id,
            'rating': rating,
            'notes': notes,
            'timestamp': datetime.utcnow()
        })
        
        # Update community signal
        await self._update_community_signal(token_mint)
    
    async def submit_rating(
        self,
        user_id: int,
        token_address: str,
        rating: float,
        comment: str = ""
    ):
        """
        Submit a rating for a token (alias for submit_token_rating)
        
        Args:
            user_id: User submitting rating
            token_address: Token address
            rating: Rating (0-10)
            comment: Optional comment
        """
        return await self.submit_token_rating(user_id, token_address, rating, comment)
    
    async def get_token_rating(self, token_address: str) -> Dict:
        """
        Get community rating for a token
        
        Args:
            token_address: Token to rate
        
        Returns:
            Rating data with consensus
        """
        if token_address not in self.token_ratings:
            return {
                'avg_rating': 0.0,
                'rating_count': 0,
                'confidence': 0.0,
                'recommendation': 'neutral'
            }
        
        ratings = self.token_ratings[token_address]
        
        if not ratings:
            return {
                'avg_rating': 0.0,
                'rating_count': 0,
                'confidence': 0.0,
                'recommendation': 'neutral'
            }
        
        # Calculate average
        avg_rating = sum(r['rating'] for r in ratings) / len(ratings)
        
        # Calculate confidence (based on number of ratings)
        confidence = min(len(ratings) / 10 * 100, 100)  # 10 ratings = 100% confidence
        
        # Determine recommendation
        if avg_rating >= 7.5:
            recommendation = 'strong_buy'
        elif avg_rating >= 6.0:
            recommendation = 'buy'
        elif avg_rating >= 4.0:
            recommendation = 'hold'
        elif avg_rating >= 2.5:
            recommendation = 'sell'
        else:
            recommendation = 'strong_sell'
        
        return {
            'avg_rating': avg_rating,
            'rating_count': len(ratings),
            'confidence': confidence,
            'recommendation': recommendation,
            'ratings': ratings
        }
    
    async def flag_token(
        self,
        user_id: int,
        token_mint: str,
        reason: str,
        evidence: Optional[str] = None
    ):
        """Flag a token as suspicious"""
        
        if token_mint not in self.token_flags:
            self.token_flags[token_mint] = []
        
        self.token_flags[token_mint].append({
            'user_id': user_id,
            'reason': reason,
            'evidence': evidence,
            'timestamp': datetime.utcnow()
        })
        
        # Update community signal
        await self._update_community_signal(token_mint)
    
    async def _update_community_signal(self, token_mint: str):
        """Update aggregated community signal"""
        
        # Calculate average rating
        ratings = self.token_ratings.get(token_mint, [])
        avg_rating = sum(r['rating'] for r in ratings) / len(ratings) if ratings else 0
        
        # Count flags
        flags = self.token_flags.get(token_mint, [])
        flag_count = len(flags)
        
        # Calculate community score
        # High ratings = good, flags = bad
        community_score = max(0, (avg_rating / 5 * 100) - (flag_count * 10))
        
        self.community_signals[token_mint] = {
            'avg_rating': avg_rating,
            'total_ratings': len(ratings),
            'flag_count': flag_count,
            'community_score': community_score,
            'sentiment': 'positive' if community_score > 60 else 'negative' if community_score < 40 else 'neutral'
        }
    
    async def get_community_signal(self, token_mint: str) -> Optional[Dict]:
        """Get community signal for a token"""
        return self.community_signals.get(token_mint)
    
    async def get_trending_tokens(self, limit: int = 10) -> List[Dict]:
        """Get tokens with most community activity"""
        
        tokens = []
        for token_mint, signal in self.community_signals.items():
            if signal['community_score'] > 50:
                tokens.append({
                    'token_mint': token_mint,
                    **signal
                })
        
        # Sort by activity
        tokens.sort(
            key=lambda t: t['total_ratings'] + t['flag_count'],
            reverse=True
        )
        
        return tokens[:limit]


class RewardSystem:
    """
    Reward users for contributing to community
    """
    
    def __init__(self):
        self.user_points: Dict[int, int] = {}
        self.reward_tiers = {
            100: "Bronze Contributor",
            500: "Silver Contributor",
            1000: "Gold Contributor",
            5000: "Platinum Contributor",
            10000: "Diamond Contributor"
        }
    
    async def award_points(
        self,
        user_id: int,
        points: int,
        reason: str
    ):
        """Award points to user"""
        
        if user_id not in self.user_points:
            self.user_points[user_id] = 0
        
        self.user_points[user_id] += points
        
        # Check for tier upgrade
        tier = self._get_user_tier(user_id)
        
        logger.info(f"User {user_id} awarded {points} points for {reason}. Total: {self.user_points[user_id]}")
    
    def _get_user_tier(self, user_id: int) -> str:
        """Get user's contributor tier"""
        points = self.user_points.get(user_id, 0)
        
        tier = "Novice"
        for threshold, tier_name in sorted(self.reward_tiers.items()):
            if points >= threshold:
                tier = tier_name
        
        return tier
    
    async def get_user_rewards(self, user_id: int) -> Dict:
        """Get user's reward status"""
        
        points = self.user_points.get(user_id, 0)
        tier = self._get_user_tier(user_id)
        
        # Calculate next tier
        next_tier_points = None
        for threshold in sorted(self.reward_tiers.keys()):
            if threshold > points:
                next_tier_points = threshold
                break
        
        return {
            'points': points,
            'tier': tier,
            'next_tier_points': next_tier_points,
            'progress': (points / next_tier_points * 100) if next_tier_points else 100
        }


# Point rewards for various actions
REWARD_POINTS = {
    'successful_trade': 10,
    'rate_token': 5,
    'flag_scam': 20,
    'share_strategy': 50,
    'strategy_purchase': 25,
    'help_user': 15,
    'daily_login': 1
}
