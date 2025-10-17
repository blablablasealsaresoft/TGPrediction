"""
Database module for tracking trades, profits, and wallet performance
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import select, func, and_, or_

logger = logging.getLogger(__name__)

Base = declarative_base()


class Trade(Base):
    """Trade record"""
    __tablename__ = 'trades'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, index=True)
    signature = Column(String, unique=True)
    trade_type = Column(String)  # 'buy' or 'sell'
    token_mint = Column(String, index=True)
    token_symbol = Column(String)
    amount_sol = Column(Float)
    amount_tokens = Column(Float)
    price = Column(Float)
    slippage = Column(Float)
    price_impact = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    success = Column(Boolean)
    error_message = Column(String, nullable=True)
    
    # PnL tracking
    pnl_sol = Column(Float, nullable=True)
    pnl_percentage = Column(Float, nullable=True)
    
    # Position tracking
    position_id = Column(String, nullable=True, index=True)
    is_position_open = Column(Boolean, default=True)


class UserWallet(Base):
    """Individual user trading wallet"""
    __tablename__ = 'user_wallets'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, unique=True, index=True)
    telegram_username = Column(String)
    
    # Wallet credentials (encrypted)
    public_key = Column(String, unique=True, index=True)
    encrypted_private_key = Column(String)  # Encrypted with master key
    
    # Balances (cached)
    sol_balance = Column(Float, default=0.0)
    last_balance_update = Column(DateTime, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    last_used = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)


class TrackedWallet(Base):
    """Tracked wallet for copy trading"""
    __tablename__ = 'tracked_wallets'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, index=True)
    wallet_address = Column(String, index=True)
    label = Column(String)
    added_at = Column(DateTime, default=datetime.utcnow)
    
    # Performance metrics
    total_trades = Column(Integer, default=0)
    profitable_trades = Column(Integer, default=0)
    win_rate = Column(Float, default=0.0)
    total_pnl = Column(Float, default=0.0)
    score = Column(Float, default=0.0)
    
    # Copy trading
    copy_enabled = Column(Boolean, default=False)
    copy_amount_sol = Column(Float, default=0.1)
    last_checked = Column(DateTime, nullable=True)


class Position(Base):
    """Open trading position"""
    __tablename__ = 'positions'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, index=True)
    position_id = Column(String, unique=True, index=True)
    token_mint = Column(String, index=True)
    token_symbol = Column(String)
    
    # Entry
    entry_price = Column(Float)
    entry_amount_sol = Column(Float)
    entry_amount_tokens = Column(Float)
    entry_signature = Column(String)
    entry_timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Exit
    exit_price = Column(Float, nullable=True)
    exit_amount_sol = Column(Float, nullable=True)
    exit_signature = Column(String, nullable=True)
    exit_timestamp = Column(DateTime, nullable=True)
    
    # Status
    is_open = Column(Boolean, default=True, index=True)
    pnl_sol = Column(Float, nullable=True)
    pnl_percentage = Column(Float, nullable=True)
    
    # Stop loss / Take profit
    stop_loss_percentage = Column(Float, nullable=True)
    take_profit_percentage = Column(Float, nullable=True)


class UserSettings(Base):
    """User configuration"""
    __tablename__ = 'user_settings'
    
    user_id = Column(Integer, primary_key=True)
    auto_trading_enabled = Column(Boolean, default=False)
    max_trade_size_sol = Column(Float, default=1.0)
    daily_loss_limit_sol = Column(Float, default=5.0)
    slippage_percentage = Column(Float, default=5.0)
    require_confirmation = Column(Boolean, default=True)
    
    # Risk management
    use_stop_loss = Column(Boolean, default=True)
    default_stop_loss_percentage = Column(Float, default=10.0)
    use_take_profit = Column(Boolean, default=True)
    default_take_profit_percentage = Column(Float, default=20.0)
    
    # Anti-scam
    check_honeypots = Column(Boolean, default=True)
    min_liquidity_usd = Column(Float, default=10000.0)
    
    # 🎯 Auto-Sniper Settings
    snipe_enabled = Column(Boolean, default=False)
    snipe_max_amount = Column(Float, default=0.1)
    snipe_min_liquidity = Column(Float, default=10000.0)
    snipe_min_confidence = Column(Float, default=0.65)
    snipe_max_daily = Column(Integer, default=10)
    snipe_only_strong_buy = Column(Boolean, default=True)
    snipe_daily_used = Column(Integer, default=0)
    snipe_last_reset = Column(DateTime, default=datetime.utcnow)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class DatabaseManager:
    """Async database manager"""
    
    def __init__(self, db_url: str = "sqlite+aiosqlite:///trading_bot.db"):
        self.engine = create_async_engine(db_url, echo=False)
        self.async_session = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
    
    async def init_db(self):
        """Initialize database tables"""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database initialized")
    
    async def add_trade(self, trade_data: Dict) -> Trade:
        """Add new trade record"""
        async with self.async_session() as session:
            trade = Trade(**trade_data)
            session.add(trade)
            await session.commit()
            await session.refresh(trade)
            return trade
    
    async def get_user_trades(
        self,
        user_id: int,
        limit: int = 50,
        token_mint: Optional[str] = None
    ) -> List[Trade]:
        """Get user's trade history"""
        async with self.async_session() as session:
            query = select(Trade).where(Trade.user_id == user_id)
            
            if token_mint:
                query = query.where(Trade.token_mint == token_mint)
            
            query = query.order_by(Trade.timestamp.desc()).limit(limit)
            result = await session.execute(query)
            return result.scalars().all()
    
    async def get_user_stats(self, user_id: int, days: int = 30) -> Dict:
        """Get user trading statistics"""
        async with self.async_session() as session:
            start_date = datetime.utcnow() - timedelta(days=days)
            
            # Total trades
            total_query = select(func.count(Trade.id)).where(
                and_(
                    Trade.user_id == user_id,
                    Trade.timestamp >= start_date,
                    Trade.success == True
                )
            )
            total_result = await session.execute(total_query)
            total_trades = total_result.scalar() or 0
            
            # Profitable trades
            profit_query = select(func.count(Trade.id)).where(
                and_(
                    Trade.user_id == user_id,
                    Trade.timestamp >= start_date,
                    Trade.success == True,
                    Trade.pnl_sol > 0
                )
            )
            profit_result = await session.execute(profit_query)
            profitable_trades = profit_result.scalar() or 0
            
            # Total PnL
            pnl_query = select(func.sum(Trade.pnl_sol)).where(
                and_(
                    Trade.user_id == user_id,
                    Trade.timestamp >= start_date,
                    Trade.success == True
                )
            )
            pnl_result = await session.execute(pnl_query)
            total_pnl = pnl_result.scalar() or 0.0
            
            # Win rate
            win_rate = (profitable_trades / total_trades * 100) if total_trades > 0 else 0
            
            return {
                'total_trades': total_trades,
                'profitable_trades': profitable_trades,
                'win_rate': win_rate,
                'total_pnl': total_pnl,
                'period_days': days
            }
    
    async def add_tracked_wallet(self, wallet_data: Dict) -> TrackedWallet:
        """Add wallet to track"""
        async with self.async_session() as session:
            wallet = TrackedWallet(**wallet_data)
            session.add(wallet)
            await session.commit()
            await session.refresh(wallet)
            return wallet
    
    async def get_tracked_wallets(self, user_id: int) -> List[TrackedWallet]:
        """Get user's tracked wallets"""
        async with self.async_session() as session:
            query = select(TrackedWallet).where(
                TrackedWallet.user_id == user_id
            ).order_by(TrackedWallet.score.desc())
            result = await session.execute(query)
            return result.scalars().all()
    
    async def update_wallet_metrics(
        self,
        wallet_id: int,
        metrics: Dict
    ):
        """Update wallet performance metrics"""
        async with self.async_session() as session:
            query = select(TrackedWallet).where(TrackedWallet.id == wallet_id)
            result = await session.execute(query)
            wallet = result.scalar_one_or_none()
            
            if wallet:
                for key, value in metrics.items():
                    setattr(wallet, key, value)
                wallet.last_checked = datetime.utcnow()
                await session.commit()
    
    async def open_position(self, position_data: Dict) -> Position:
        """Open new trading position"""
        async with self.async_session() as session:
            position = Position(**position_data)
            session.add(position)
            await session.commit()
            await session.refresh(position)
            return position
    
    async def close_position(
        self,
        position_id: str,
        exit_data: Dict
    ) -> Optional[Position]:
        """Close trading position"""
        async with self.async_session() as session:
            query = select(Position).where(Position.position_id == position_id)
            result = await session.execute(query)
            position = result.scalar_one_or_none()
            
            if position:
                position.is_open = False
                for key, value in exit_data.items():
                    setattr(position, key, value)
                
                # Calculate PnL
                if position.exit_amount_sol:
                    position.pnl_sol = position.exit_amount_sol - position.entry_amount_sol
                    position.pnl_percentage = (
                        (position.exit_amount_sol - position.entry_amount_sol) /
                        position.entry_amount_sol * 100
                    )
                
                await session.commit()
                await session.refresh(position)
                return position
            
            return None
    
    async def get_open_positions(self, user_id: int) -> List[Position]:
        """Get user's open positions"""
        async with self.async_session() as session:
            query = select(Position).where(
                and_(
                    Position.user_id == user_id,
                    Position.is_open == True
                )
            ).order_by(Position.entry_timestamp.desc())
            result = await session.execute(query)
            return result.scalars().all()
    
    async def get_position_by_token(
        self,
        user_id: int,
        token_mint: str
    ) -> Optional[Position]:
        """Get open position for specific token"""
        async with self.async_session() as session:
            query = select(Position).where(
                and_(
                    Position.user_id == user_id,
                    Position.token_mint == token_mint,
                    Position.is_open == True
                )
            )
            result = await session.execute(query)
            return result.scalar_one_or_none()
    
    async def get_user_settings(self, user_id: int) -> Optional[UserSettings]:
        """Get user settings"""
        async with self.async_session() as session:
            query = select(UserSettings).where(UserSettings.user_id == user_id)
            result = await session.execute(query)
            return result.scalar_one_or_none()
    
    async def update_user_settings(self, user_id: int, settings: Dict):
        """Update user settings"""
        async with self.async_session() as session:
            query = select(UserSettings).where(UserSettings.user_id == user_id)
            result = await session.execute(query)
            user_settings = result.scalar_one_or_none()
            
            if not user_settings:
                user_settings = UserSettings(user_id=user_id, **settings)
                session.add(user_settings)
            else:
                for key, value in settings.items():
                    setattr(user_settings, key, value)
                user_settings.updated_at = datetime.utcnow()
            
            await session.commit()
    
    async def get_daily_pnl(self, user_id: int) -> float:
        """Get today's PnL"""
        async with self.async_session() as session:
            today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            
            query = select(func.sum(Trade.pnl_sol)).where(
                and_(
                    Trade.user_id == user_id,
                    Trade.timestamp >= today,
                    Trade.success == True
                )
            )
            result = await session.execute(query)
            return result.scalar() or 0.0
    
    async def cleanup_old_data(self, days: int = 90):
        """Clean up old trade data"""
        async with self.async_session() as session:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            query = select(Trade).where(Trade.timestamp < cutoff_date)
            result = await session.execute(query)
            old_trades = result.scalars().all()
            
            for trade in old_trades:
                await session.delete(trade)
            
            await session.commit()
            logger.info(f"Cleaned up {len(old_trades)} old trades")
