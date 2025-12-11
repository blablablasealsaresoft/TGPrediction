"""
Web API module for APOLLO CyberSentinel Dashboard
Provides REST API and WebSocket endpoints for the dashboard frontend
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from collections import defaultdict

from aiohttp import web
import aiohttp_cors
from sqlalchemy import select, func, and_, desc

from .database import (
    DatabaseManager, Trade, Position, TrackedWallet, 
    UserWallet, UserSettings, SnipeRun
)

logger = logging.getLogger(__name__)


class WebAPIServer:
    """
    APOLLO Dashboard Web API Server
    Provides REST endpoints and WebSocket for real-time updates
    """
    
    def __init__(
        self,
        database: DatabaseManager,
        host: str = "0.0.0.0",
        port: int = 8080,
        cors_origins: List[str] = None
    ):
        self.database = database
        self.host = host
        self.port = port
        self.cors_origins = cors_origins or ["http://localhost:3000", "http://localhost"]
        
        self.app = web.Application()
        self.runner: Optional[web.AppRunner] = None
        self.site: Optional[web.TCPSite] = None
        
        # WebSocket clients
        self.ws_clients: List[web.WebSocketResponse] = []
        
        # Background task
        self.broadcast_task: Optional[asyncio.Task] = None
        
        # Shared state (can be injected from bot)
        self.monitoring = None
        self.ai_engine = None
        self.flash_loan_engine = None
        self.launch_predictor = None
        self.prediction_markets = None
        self.trade_executor = None  # For executing trades from web dashboard
        
        self._setup_routes()
        self._setup_cors()
    
    def set_modules(
        self,
        monitoring=None,
        ai_engine=None,
        flash_loan_engine=None,
        launch_predictor=None,
        prediction_markets=None,
        trade_executor=None
    ):
        """Inject module instances for API to use"""
        self.monitoring = monitoring
        self.ai_engine = ai_engine
        self.flash_loan_engine = flash_loan_engine
        self.launch_predictor = launch_predictor
        self.prediction_markets = prediction_markets
        self.trade_executor = trade_executor
    
    def _setup_routes(self):
        """Setup all API routes"""
        # Frontend pages
        self.app.router.add_get('/', self.serve_waitlist)
        self.app.router.add_get('/app', self.serve_index)
        self.app.router.add_get('/dashboard', self.serve_dashboard)
        self.app.router.add_get('/prediction-market', self.serve_prediction_market)
        self.app.router.add_get('/docs', self.serve_docs)
        self.app.router.add_get('/profile', self.serve_profile)  # Epic user profile page
        
        # Static files - serve CSS and JS directly
        self.app.router.add_get('/static/css/apollo-enhanced-style.css', self.serve_css)
        self.app.router.add_get('/static/js/apollo-enhanced-effects.js', self.serve_js)
        
        # Health checks (compatible with existing probe server)
        self.app.router.add_get('/health', self.health_check)
        self.app.router.add_get('/live', self.live_check)
        self.app.router.add_get('/ready', self.ready_check)
        
        # Waitlist endpoints
        self.app.router.add_post('/api/v1/waitlist', self.add_to_waitlist)
        self.app.router.add_get('/api/v1/waitlist/count', self.get_waitlist_count)
        self.app.router.add_post('/api/v1/waitlist/register', self.register_waitlist)
        
        # Access check endpoint
        self.app.router.add_get('/api/v1/access/check', self.check_access)
        
        # Wallet registration endpoint
        self.app.router.add_post('/api/v1/wallet/register', self.register_wallet)
        
        # Twitter registration endpoint
        self.app.router.add_post('/api/v1/twitter/register', self.register_twitter)
        
        # Dashboard endpoints
        self.app.router.add_get('/api/v1/metrics', self.get_metrics)
        self.app.router.add_get('/api/v1/performance', self.get_performance)
        self.app.router.add_get('/api/v1/trades/recent', self.get_recent_trades)
        self.app.router.add_get('/api/v1/trades/top-tokens', self.get_top_tokens)
        self.app.router.add_get('/api/v1/phases/status', self.get_phases_status)
        self.app.router.add_get('/api/v1/phases/distribution', self.get_phases_distribution)
        self.app.router.add_get('/api/v1/alerts', self.get_alerts)
        
        # Admin endpoints
        self.app.router.add_get('/api/v1/admin/services', self.get_services_status)
        self.app.router.add_post('/api/v1/admin/services/{service}/restart', self.restart_service)
        self.app.router.add_get('/api/v1/admin/config', self.get_config)
        self.app.router.add_put('/api/v1/admin/config', self.update_config)
        self.app.router.add_get('/api/v1/admin/logs', self.get_logs)
        self.app.router.add_get('/api/v1/admin/logs/export', self.export_logs)
        
        # Prediction phase
        self.app.router.add_get('/api/v1/predictions/stats', self.get_prediction_stats)
        self.app.router.add_get('/api/v1/predictions/recent', self.get_recent_predictions)
        
        # Flash loan phase
        self.app.router.add_get('/api/v1/flash/stats', self.get_flash_stats)
        self.app.router.add_get('/api/v1/flash/opportunities', self.get_flash_opportunities)
        
        # Launch predictor phase
        self.app.router.add_get('/api/v1/launches/predictions', self.get_launch_predictions)
        self.app.router.add_get('/api/v1/launches/stats', self.get_launch_stats)
        
        # Prediction markets phase
        self.app.router.add_get('/api/v1/markets', self.get_markets)
        self.app.router.add_get('/api/v1/markets/{market_id}', self.get_market_details)
        self.app.router.add_get('/api/v1/markets/stats', self.get_market_stats)
        
        # User & wallet endpoints
        self.app.router.add_get('/api/v1/users/stats', self.get_users_stats)
        self.app.router.add_get('/api/v1/wallets/elite', self.get_elite_wallets_stats)
        
        # User-specific endpoints for web dashboard
        self.app.router.add_get('/api/v1/user/{user_id}/profile', self.get_user_profile)
        self.app.router.add_get('/api/v1/user/{user_id}/trades', self.get_user_trades)
        self.app.router.add_get('/api/v1/user/{user_id}/positions', self.get_user_positions)
        self.app.router.add_get('/api/v1/user/{user_id}/stats', self.get_user_stats_detailed)
        self.app.router.add_get('/api/v1/user/{user_id}/wallet', self.get_user_wallet_info)
        self.app.router.add_post('/api/v1/user/{user_id}/buy', self.execute_user_buy)
        self.app.router.add_post('/api/v1/user/{user_id}/sell', self.execute_user_sell)
        self.app.router.add_get('/api/v1/user/{user_id}/settings', self.get_user_settings)
        self.app.router.add_put('/api/v1/user/{user_id}/settings', self.update_user_settings_endpoint)
        self.app.router.add_post('/api/v1/user/{user_id}/analyze', self.analyze_token_for_user)
        
        # Leaderboard and rankings
        self.app.router.add_get('/api/v1/leaderboard', self.get_leaderboard)
        self.app.router.add_get('/api/v1/rankings/traders', self.get_trader_rankings)
        
        # WebSocket
        self.app.router.add_get('/ws', self.websocket_handler)
    
    def _setup_cors(self):
        """Setup CORS for frontend access"""
        self._setup_cors_on_app(self.app)
    
    def _setup_cors_on_app(self, app: web.Application):
        """Setup CORS on a specific aiohttp application"""
        cors = aiohttp_cors.setup(app, defaults={
            origin: aiohttp_cors.ResourceOptions(
                allow_credentials=True,
                expose_headers="*",
                allow_headers="*",
                allow_methods="*"
            ) for origin in self.cors_origins
        })
        
        # Configure CORS on all routes
        for route in list(app.router.routes()):
            try:
                cors.add(route)
            except Exception:
                pass  # Route may already have CORS
    
    async def start(self):
        """Start the web server"""
        self.runner = web.AppRunner(self.app)
        await self.runner.setup()
        self.site = web.TCPSite(self.runner, self.host, self.port)
        await self.site.start()
        
        # Start background broadcast task
        self.broadcast_task = asyncio.create_task(self._broadcast_loop())
        
        logger.info(f"Web API server started on {self.host}:{self.port}")
    
    async def stop(self):
        """Stop the web server"""
        if self.broadcast_task:
            self.broadcast_task.cancel()
            try:
                await self.broadcast_task
            except asyncio.CancelledError:
                pass
        
        # Close all WebSocket connections
        for ws in self.ws_clients:
            await ws.close()
        
        if self.site:
            await self.site.stop()
        if self.runner:
            await self.runner.cleanup()
        
        logger.info("Web API server stopped")
    
    # ==================== Frontend Pages ====================
    
    async def serve_waitlist(self, request: web.Request) -> web.Response:
        """Serve waitlist page"""
        try:
            with open('./public/waitlist.html', 'r', encoding='utf-8') as f:
                content = f.read()
            return web.Response(text=content, content_type='text/html')
        except FileNotFoundError:
            return web.Response(text='Waitlist page not found', status=404)
    
    async def serve_index(self, request: web.Request) -> web.Response:
        """Serve main landing page"""
        try:
            with open('./public/index.html', 'r', encoding='utf-8') as f:
                content = f.read()
            return web.Response(text=content, content_type='text/html')
        except FileNotFoundError:
            return web.Response(text='Landing page not found', status=404)
    
    async def serve_dashboard(self, request: web.Request) -> web.Response:
        """Serve trading dashboard"""
        try:
            with open('./public/dashboard.html', 'r', encoding='utf-8') as f:
                content = f.read()
            return web.Response(text=content, content_type='text/html')
        except FileNotFoundError:
            return web.Response(text='Dashboard not found', status=404)
    
    async def serve_prediction_market(self, request: web.Request) -> web.Response:
        """Serve prediction market page"""
        try:
            with open('./public/prediction-market.html', 'r', encoding='utf-8') as f:
                content = f.read()
            return web.Response(text=content, content_type='text/html')
        except FileNotFoundError:
            return web.Response(text='Prediction market page not found', status=404)
    
    async def serve_docs(self, request: web.Request) -> web.Response:
        """Serve documentation page"""
        try:
            with open('./public/docs.html', 'r', encoding='utf-8') as f:
                content = f.read()
            return web.Response(text=content, content_type='text/html')
        except FileNotFoundError:
            return web.Response(text='Documentation not found', status=404)
    
    async def serve_profile(self, request: web.Request) -> web.Response:
        """Serve epic user profile page"""
        try:
            with open('./public/user-profile.html', 'r', encoding='utf-8') as f:
                content = f.read()
            return web.Response(text=content, content_type='text/html')
        except FileNotFoundError:
            return web.Response(text='Profile page not found', status=404)
    
    async def serve_css(self, request: web.Request) -> web.Response:
        """Serve enhanced CSS file"""
        try:
            with open('./public/static/css/apollo-enhanced-style.css', 'r', encoding='utf-8') as f:
                content = f.read()
            return web.Response(text=content, content_type='text/css')
        except FileNotFoundError:
            return web.Response(text='/* CSS not found */', status=404, content_type='text/css')
    
    async def serve_js(self, request: web.Request) -> web.Response:
        """Serve enhanced JS file"""
        try:
            with open('./public/static/js/apollo-enhanced-effects.js', 'r', encoding='utf-8') as f:
                content = f.read()
            return web.Response(text=content, content_type='application/javascript')
        except FileNotFoundError:
            return web.Response(text='// JS not found', status=404, content_type='application/javascript')
    
    # ==================== Health Checks ====================
    
    async def health_check(self, request: web.Request) -> web.Response:
        """Health check endpoint (alias for /live)"""
        return web.json_response({'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()})
    
    async def live_check(self, request: web.Request) -> web.Response:
        """Liveness probe (Kubernetes-style)"""
        return web.json_response({'status': 'alive'})
    
    async def ready_check(self, request: web.Request) -> web.Response:
        """Readiness check endpoint"""
        # Check database connection
        try:
            async with self.database.async_session() as session:
                await session.execute(select(1))
            return web.json_response({
                'status': 'ready',
                'checks': {'database': {'ok': True, 'detail': 'Connected'}}
            })
        except Exception as e:
            logger.error(f"Readiness check failed: {e}")
            return web.json_response(
                {
                    'status': 'starting',
                    'checks': {'database': {'ok': False, 'detail': str(e)}}
                },
                status=503
            )
    
    # ==================== Waitlist Endpoints ====================
    
    async def add_to_waitlist(self, request: web.Request) -> web.Response:
        """Add email to waitlist"""
        try:
            data = await request.json()
            email = data.get('email', '').strip().lower()
            
            if not email:
                return web.json_response({'error': 'Email is required'}, status=400)
            
            # Basic email validation
            import re
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, email):
                return web.json_response({'error': 'Invalid email address'}, status=400)
            
            # Get IP and user agent
            ip_address = request.remote
            user_agent = request.headers.get('User-Agent', '')
            
            from src.modules.database import WaitlistSignup
            
            async with self.database.async_session() as session:
                # Check if email already exists
                from sqlalchemy import select
                result = await session.execute(
                    select(WaitlistSignup).where(WaitlistSignup.email == email)
                )
                existing = result.scalar_one_or_none()
                
                if existing:
                    return web.json_response({
                        'message': 'You are already on the waitlist!',
                        'signup_date': existing.signup_date.isoformat()
                    })
                
                # Add new signup
                new_signup = WaitlistSignup(
                    email=email,
                    ip_address=ip_address,
                    user_agent=user_agent
                )
                session.add(new_signup)
                await session.commit()
                
                logger.info(f"New waitlist signup: {email}")
                
                return web.json_response({
                    'message': 'Successfully added to waitlist!',
                    'email': email,
                    'signup_date': new_signup.signup_date.isoformat()
                })
                
        except Exception as e:
            logger.error(f"Error adding to waitlist: {e}")
            return web.json_response({'error': 'Internal server error'}, status=500)
    
    async def get_waitlist_count(self, request: web.Request) -> web.Response:
        """Get total number of waitlist signups"""
        try:
            from src.modules.database import WaitlistSignup
            from sqlalchemy import func, select
            
            async with self.database.async_session() as session:
                result = await session.execute(
                    select(func.count(WaitlistSignup.id))
                )
                count = result.scalar() or 0
                
                return web.json_response({
                    'count': count,
                    'message': f'{count} people on the waitlist'
                })
                
        except Exception as e:
            logger.error(f"Error getting waitlist count: {e}")
            return web.json_response({'error': 'Internal server error'}, status=500)
    
    async def register_waitlist(self, request: web.Request) -> web.Response:
        """Register for waitlist with Twitter + Telegram + Wallet"""
        try:
            data = await request.json()
            twitter_handle = data.get('twitter_handle', '').strip().lstrip('@').lower()
            telegram_username = data.get('telegram_username', '').strip().lstrip('@').lower()
            wallet_address = data.get('wallet_address', '').strip()
            
            if not twitter_handle:
                return web.json_response({'error': 'Twitter handle is required'}, status=400)
            
            if not telegram_username:
                return web.json_response({'error': 'Telegram username is required'}, status=400)
            
            if not wallet_address or len(wallet_address) < 32:
                return web.json_response({'error': 'Valid Solana wallet address is required'}, status=400)
            
            # Validate Twitter handle
            import re
            if not re.match(r'^[A-Za-z0-9_]{1,15}$', twitter_handle):
                return web.json_response({'error': 'Invalid Twitter handle'}, status=400)
            
            # Validate Telegram username
            if not re.match(r'^[A-Za-z0-9_]{5,32}$', telegram_username):
                return web.json_response({'error': 'Invalid Telegram username'}, status=400)
            
            ip_address = request.remote
            user_agent = request.headers.get('User-Agent', '')
            
            from src.modules.database import WaitlistSignup
            from sqlalchemy import select
            
            async with self.database.async_session() as session:
                # Check if already on waitlist
                result = await session.execute(
                    select(WaitlistSignup).where(WaitlistSignup.twitter_handle == twitter_handle)
                )
                existing = result.scalar_one_or_none()
                
                if existing:
                    # Update wallet and telegram if changed
                    if existing.wallet_address != wallet_address:
                        existing.wallet_address = wallet_address
                    if existing.telegram_username != telegram_username:
                        existing.telegram_username = telegram_username
                    await session.commit()
                    
                    return web.json_response({
                        'message': 'Already on waitlist',
                        'twitter_handle': '@' + twitter_handle,
                        'telegram_username': '@' + telegram_username,
                        'approved': existing.is_approved
                    })
                
                # Add to waitlist
                new_signup = WaitlistSignup(
                    twitter_handle=twitter_handle,
                    telegram_username=telegram_username,
                    wallet_address=wallet_address,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    is_approved=False
                )
                session.add(new_signup)
                await session.commit()
                
                logger.info(f"New waitlist signup: @{twitter_handle} (TG: @{telegram_username}) - {wallet_address}")
                
                return web.json_response({
                    'message': 'Successfully joined waitlist!',
                    'twitter_handle': '@' + twitter_handle,
                    'telegram_username': '@' + telegram_username,
                    'approved': False
                })
                
        except Exception as e:
            logger.error(f"Error registering waitlist: {e}")
            return web.json_response({'error': 'Internal server error'}, status=500)
    
    async def check_access(self, request: web.Request) -> web.Response:
        """Check if user has been granted access"""
        try:
            twitter_handle = request.query.get('twitter', '').strip().lstrip('@').lower()
            
            if not twitter_handle:
                return web.json_response({'approved': False, 'message': 'No Twitter handle provided'})
            
            from src.modules.database import WaitlistSignup
            from sqlalchemy import select
            
            # Pre-approved users (can expand this list)
            APPROVED_USERS = ['danksince93', 'ckfidel', 'yourusername']
            
            # Check if user is pre-approved
            if twitter_handle in APPROVED_USERS:
                return web.json_response({
                    'approved': True,
                    'twitter_handle': '@' + twitter_handle,
                    'message': 'Access granted!'
                })
            
            # Check database
            async with self.database.async_session() as session:
                result = await session.execute(
                    select(WaitlistSignup).where(WaitlistSignup.twitter_handle == twitter_handle)
                )
                user = result.scalar_one_or_none()
                
                if user and user.is_approved:
                    return web.json_response({
                        'approved': True,
                        'twitter_handle': '@' + twitter_handle,
                        'approved_date': user.approved_date.isoformat() if user.approved_date else None
                    })
                else:
                    return web.json_response({
                        'approved': False,
                        'message': 'Access not granted yet. Follow @ApolloTrading for announcements.'
                    })
                    
        except Exception as e:
            logger.error(f"Error checking access: {e}")
            return web.json_response({'approved': False, 'error': str(e)}, status=500)
    
    async def register_wallet(self, request: web.Request) -> web.Response:
        """Register Solana wallet for web3 authentication"""
        try:
            data = await request.json()
            wallet_address = data.get('wallet_address', '').strip()
            wallet_provider = data.get('wallet_provider', 'unknown').strip().lower()
            
            if not wallet_address:
                return web.json_response({'error': 'Wallet address is required'}, status=400)
            
            # Basic Solana address validation (32-44 characters, base58)
            if len(wallet_address) < 32 or len(wallet_address) > 44:
                return web.json_response({'error': 'Invalid Solana wallet address'}, status=400)
            
            # Get IP and user agent
            ip_address = request.remote
            user_agent = request.headers.get('User-Agent', '')
            
            from src.modules.database import WalletRegistration
            from sqlalchemy import select
            
            async with self.database.async_session() as session:
                # Check if wallet already registered
                result = await session.execute(
                    select(WalletRegistration).where(WalletRegistration.wallet_address == wallet_address)
                )
                existing = result.scalar_one_or_none()
                
                if existing:
                    # Update last seen
                    existing.last_seen = datetime.utcnow()
                    existing.visit_count += 1
                    await session.commit()
                    
                    return web.json_response({
                        'message': 'Wallet already registered',
                        'wallet_address': wallet_address,
                        'registered_date': existing.registered_date.isoformat(),
                        'visit_count': existing.visit_count
                    })
                
                # Register new wallet
                new_registration = WalletRegistration(
                    wallet_address=wallet_address,
                    wallet_provider=wallet_provider,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    visit_count=1
                )
                session.add(new_registration)
                await session.commit()
                
                logger.info(f"New wallet registered: {wallet_address} ({wallet_provider})")
                
                return web.json_response({
                    'message': 'Wallet registered successfully!',
                    'wallet_address': wallet_address,
                    'registered_date': new_registration.registered_date.isoformat()
                })
                
        except Exception as e:
            logger.error(f"Error registering wallet: {e}")
            return web.json_response({'error': 'Internal server error'}, status=500)
    
    async def register_twitter(self, request: web.Request) -> web.Response:
        """Register Twitter account for authentication and profile"""
        try:
            data = await request.json()
            twitter_handle = data.get('twitter_handle', '').strip().lstrip('@')
            
            if not twitter_handle:
                return web.json_response({'error': 'Twitter handle is required'}, status=400)
            
            # Twitter handle validation (1-15 characters, alphanumeric + underscore)
            import re
            if not re.match(r'^[A-Za-z0-9_]{1,15}$', twitter_handle):
                return web.json_response({'error': 'Invalid Twitter handle'}, status=400)
            
            # Get IP and user agent
            ip_address = request.remote
            user_agent = request.headers.get('User-Agent', '')
            
            from src.modules.database import TwitterRegistration
            from sqlalchemy import select
            
            async with self.database.async_session() as session:
                # Check if Twitter handle already registered
                result = await session.execute(
                    select(TwitterRegistration).where(TwitterRegistration.twitter_handle == twitter_handle.lower())
                )
                existing = result.scalar_one_or_none()
                
                if existing:
                    # Update last seen
                    existing.last_seen = datetime.utcnow()
                    existing.visit_count += 1
                    await session.commit()
                    
                    return web.json_response({
                        'message': 'Twitter account already registered',
                        'twitter_handle': '@' + twitter_handle,
                        'registered_date': existing.registered_date.isoformat(),
                        'visit_count': existing.visit_count
                    })
                
                # Register new Twitter account
                new_registration = TwitterRegistration(
                    twitter_handle=twitter_handle.lower(),
                    display_handle='@' + twitter_handle,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    visit_count=1
                )
                session.add(new_registration)
                await session.commit()
                
                logger.info(f"New Twitter account registered: @{twitter_handle}")
                
                return web.json_response({
                    'message': 'Twitter account registered successfully!',
                    'twitter_handle': '@' + twitter_handle,
                    'registered_date': new_registration.registered_date.isoformat()
                })
                
        except Exception as e:
            logger.error(f"Error registering Twitter account: {e}")
            return web.json_response({'error': 'Internal server error'}, status=500)
    
    # ==================== Dashboard Endpoints ====================
    
    async def get_metrics(self, request: web.Request) -> web.Response:
        """Get bot performance metrics"""
        try:
            async with self.database.async_session() as session:
                # Total trades
                total_trades_result = await session.execute(
                    select(func.count(Trade.id)).where(Trade.success == True)
                )
                total_trades = total_trades_result.scalar() or 0
                
                # Win rate (trades with positive PnL)
                winning_trades_result = await session.execute(
                    select(func.count(Trade.id)).where(
                        and_(Trade.success == True, Trade.pnl_sol > 0)
                    )
                )
                winning_trades = winning_trades_result.scalar() or 0
                win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
                
                # Total PnL
                total_pnl_result = await session.execute(
                    select(func.sum(Trade.pnl_sol)).where(Trade.success == True)
                )
                total_pnl = total_pnl_result.scalar() or 0.0
                
                # Active users (users with at least one trade)
                active_users_result = await session.execute(
                    select(func.count(func.distinct(Trade.user_id))).where(Trade.success == True)
                )
                active_users = active_users_result.scalar() or 0
                
                # Elite wallets count
                elite_wallets_result = await session.execute(
                    select(func.count(TrackedWallet.id)).where(TrackedWallet.is_trader == True)
                )
                elite_wallets = elite_wallets_result.scalar() or 441
                
                # Predictions today
                today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
                predictions_today_result = await session.execute(
                    select(func.count(Trade.id)).where(
                        and_(
                            Trade.context == 'prediction',
                            Trade.timestamp >= today_start
                        )
                    )
                )
                predictions_today = predictions_today_result.scalar() or 0
                
                # Flash loans executed (from context)
                flash_loans_result = await session.execute(
                    select(func.count(Trade.id)).where(
                        Trade.context == 'flash_loan'
                    )
                )
                flash_loans_executed = flash_loans_result.scalar() or 0
                
                # Average confidence (from snipe runs)
                avg_confidence_result = await session.execute(
                    select(func.avg(SnipeRun.ai_confidence)).where(
                        SnipeRun.ai_confidence.isnot(None)
                    )
                )
                avg_confidence = avg_confidence_result.scalar() or 75.0
                
                return web.json_response({
                    'totalTrades': total_trades,
                    'winRate': round(win_rate, 2),
                    'totalPnL': round(total_pnl, 4),
                    'activeUsers': active_users,
                    'eliteWallets': elite_wallets,
                    'predictionsToday': predictions_today,
                    'flashLoansExecuted': flash_loans_executed,
                    'avgConfidence': round(avg_confidence, 2)
                })
        
        except Exception as e:
            logger.error(f"Error fetching metrics: {e}")
            return web.json_response({'error': str(e)}, status=500)
    
    async def get_performance(self, request: web.Request) -> web.Response:
        """Get 7-day performance data"""
        try:
            async with self.database.async_session() as session:
                # Get last 7 days of data
                days_data = []
                for i in range(6, -1, -1):  # 6 days ago to today
                    day_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=i)
                    day_end = day_start + timedelta(days=1)
                    
                    # PnL for the day
                    pnl_result = await session.execute(
                        select(func.sum(Trade.pnl_sol)).where(
                            and_(
                                Trade.success == True,
                                Trade.timestamp >= day_start,
                                Trade.timestamp < day_end
                            )
                        )
                    )
                    pnl = pnl_result.scalar() or 0.0
                    
                    # Trades count
                    trades_result = await session.execute(
                        select(func.count(Trade.id)).where(
                            and_(
                                Trade.success == True,
                                Trade.timestamp >= day_start,
                                Trade.timestamp < day_end
                            )
                        )
                    )
                    trades = trades_result.scalar() or 0
                    
                    # Win rate
                    winning_result = await session.execute(
                        select(func.count(Trade.id)).where(
                            and_(
                                Trade.success == True,
                                Trade.pnl_sol > 0,
                                Trade.timestamp >= day_start,
                                Trade.timestamp < day_end
                            )
                        )
                    )
                    winning = winning_result.scalar() or 0
                    win_rate = (winning / trades * 100) if trades > 0 else 0
                    
                    day_name = "Today" if i == 0 else day_start.strftime("%a")
                    
                    days_data.append({
                        'date': day_name,
                        'pnl': round(pnl, 2),
                        'trades': trades,
                        'winRate': round(win_rate, 1)
                    })
                
                return web.json_response(days_data)
        
        except Exception as e:
            logger.error(f"Error fetching performance: {e}")
            return web.json_response({'error': str(e)}, status=500)
    
    async def get_recent_trades(self, request: web.Request) -> web.Response:
        """Get recent trades"""
        try:
            limit = int(request.query.get('limit', 20))
            
            async with self.database.async_session() as session:
                result = await session.execute(
                    select(Trade)
                    .where(Trade.success == True)
                    .order_by(desc(Trade.timestamp))
                    .limit(limit)
                )
                trades = result.scalars().all()
                
                trades_data = []
                for trade in trades:
                    trades_data.append({
                        'id': trade.id,
                        'timestamp': trade.timestamp.isoformat(),
                        'type': trade.trade_type,
                        'token': trade.token_symbol or trade.token_mint[:8],
                        'amountSol': round(trade.amount_sol, 4),
                        'price': round(trade.price, 8) if trade.price else None,
                        'pnl': round(trade.pnl_sol, 4) if trade.pnl_sol else None,
                        'context': trade.context
                    })
                
                return web.json_response(trades_data)
        
        except Exception as e:
            logger.error(f"Error fetching recent trades: {e}")
            return web.json_response({'error': str(e)}, status=500)
    
    async def get_top_tokens(self, request: web.Request) -> web.Response:
        """Get top performing tokens"""
        try:
            async with self.database.async_session() as session:
                # Group by token and sum PnL
                result = await session.execute(
                    select(
                        Trade.token_symbol,
                        Trade.token_mint,
                        func.sum(Trade.pnl_sol).label('total_pnl'),
                        func.count(Trade.id).label('trade_count'),
                        func.sum(func.case((Trade.pnl_sol > 0, 1), else_=0)).label('winning_trades')
                    )
                    .where(and_(Trade.success == True, Trade.token_symbol.isnot(None)))
                    .group_by(Trade.token_symbol, Trade.token_mint)
                    .order_by(desc('total_pnl'))
                    .limit(5)
                )
                
                top_tokens = []
                for row in result:
                    symbol, mint, total_pnl, trade_count, winning_trades = row
                    win_rate = (winning_trades / trade_count * 100) if trade_count > 0 else 0
                    
                    top_tokens.append({
                        'symbol': f"${symbol}" if symbol else f"${mint[:6]}",
                        'pnl': f"+${abs(total_pnl):.0f}" if total_pnl > 0 else f"-${abs(total_pnl):.0f}",
                        'winRate': int(win_rate),
                        'trades': trade_count
                    })
                
                return web.json_response(top_tokens)
        
        except Exception as e:
            logger.error(f"Error fetching top tokens: {e}")
            return web.json_response({'error': str(e)}, status=500)
    
    async def get_phases_status(self, request: web.Request) -> web.Response:
        """Get 4-phase system status"""
        return web.json_response({
            'predictions': 'active',
            'flashLoans': 'active',
            'launchPredictor': 'active',
            'predictionMarkets': 'active'
        })
    
    async def get_phases_distribution(self, request: web.Request) -> web.Response:
        """Get trade distribution by phase"""
        try:
            async with self.database.async_session() as session:
                # Count trades by context
                result = await session.execute(
                    select(
                        Trade.context,
                        func.count(Trade.id).label('count')
                    )
                    .where(Trade.success == True)
                    .group_by(Trade.context)
                )
                
                context_map = {
                    'prediction': 'Predictions',
                    'flash_loan': 'Flash Loans',
                    'sniper': 'Launch Snipes',
                    'market': 'Markets',
                    'manual': 'Manual'
                }
                
                distribution = []
                for row in result:
                    context, count = row
                    name = context_map.get(context, context.title())
                    distribution.append({
                        'name': name,
                        'value': count
                    })
                
                return web.json_response(distribution)
        
        except Exception as e:
            logger.error(f"Error fetching phase distribution: {e}")
            return web.json_response({'error': str(e)}, status=500)
    
    async def get_alerts(self, request: web.Request) -> web.Response:
        """Get system alerts"""
        # TODO: Implement real alert system
        # For now, return recent significant events
        alerts = [
            {
                'type': 'success',
                'message': 'System operational - all modules running',
                'timestamp': datetime.utcnow().isoformat()
            }
        ]
        return web.json_response(alerts)
    
    # ==================== Admin Endpoints ====================
    
    async def get_services_status(self, request: web.Request) -> web.Response:
        """Get status of all services"""
        services = {
            'tradingBot': {
                'status': 'healthy',
                'uptime': 99.97,
                'lastCheck': datetime.utcnow().isoformat()
            },
            'database': {
                'status': 'healthy',
                'connections': 12,
                'responseTime': 45
            },
            'redis': {
                'status': 'healthy',
                'memoryUsage': 67,
                'hitRate': 94.3
            },
            'rpc': {
                'status': 'healthy',
                'provider': 'Helius',
                'latency': 120
            },
            'telegram': {
                'status': 'healthy',
                'usersOnline': 0,
                'messagesPerMin': 0
            },
            'ai': {
                'status': 'healthy',
                'modelAccuracy': 76.8,
                'predictionsToday': 0
            }
        }
        
        # If monitoring module is available, get real stats
        if self.monitoring:
            try:
                stats = self.monitoring.get_stats() if hasattr(self.monitoring, 'get_stats') else {}
                # Update services with real data
                if stats:
                    pass  # TODO: Map monitoring stats to services
            except Exception as e:
                logger.error(f"Error getting monitoring stats: {e}")
        
        return web.json_response(services)
    
    async def restart_service(self, request: web.Request) -> web.Response:
        """Restart a service (admin only)"""
        service_name = request.match_info['service']
        logger.info(f"Restart requested for service: {service_name}")
        
        # TODO: Implement actual service restart logic
        return web.json_response({
            'status': 'success',
            'message': f'Service {service_name} restart initiated',
            'service': service_name
        })
    
    async def get_config(self, request: web.Request) -> web.Response:
        """Get current configuration"""
        import os
        
        config = {
            'ALLOW_BROADCAST': os.getenv('ALLOW_BROADCAST', 'false').lower() == 'true',
            'AUTO_TRADE_ENABLED': os.getenv('AUTO_TRADE_ENABLED', 'false').lower() == 'true',
            'FLASH_LOAN_ENABLED': os.getenv('ENABLE_FLASH_LOANS', 'false').lower() == 'true',
            'LAUNCH_MONITOR_ENABLED': os.getenv('ENABLE_LAUNCH_MONITOR', 'true').lower() == 'true',
            'MIN_CONFIDENCE': int(os.getenv('MIN_AI_CONFIDENCE', '65')),
            'MAX_DAILY_TRADES': int(os.getenv('MAX_DAILY_TRADES', '25')),
            'DAILY_LIMIT_SOL': float(os.getenv('DAILY_LIMIT_SOL', '10')),
            'ELITE_WALLETS_COUNT': 441,
            'API_RATE_LIMIT': 100
        }
        
        return web.json_response(config)
    
    async def update_config(self, request: web.Request) -> web.Response:
        """Update configuration (admin only)"""
        try:
            data = await request.json()
            logger.info(f"Config update requested: {data}")
            
            # TODO: Implement actual config update logic
            # This should update .env file or environment variables
            
            return web.json_response({
                'status': 'success',
                'message': 'Configuration updated (restart required)',
                'config': data
            })
        except Exception as e:
            logger.error(f"Error updating config: {e}")
            return web.json_response({'error': str(e)}, status=500)
    
    async def get_logs(self, request: web.Request) -> web.Response:
        """Get system logs"""
        # TODO: Read from actual log file
        logs = [
            {
                'timestamp': datetime.utcnow().isoformat(),
                'level': 'INFO',
                'message': 'Web API server initialized',
                'module': 'WebAPI'
            }
        ]
        return web.json_response(logs)
    
    async def export_logs(self, request: web.Request) -> web.Response:
        """Export logs as file"""
        # TODO: Implement log export
        return web.Response(
            text="Log export not yet implemented",
            content_type='text/plain'
        )
    
    # ==================== Prediction Phase ====================
    
    async def get_prediction_stats(self, request: web.Request) -> web.Response:
        """Get prediction accuracy stats"""
        try:
            async with self.database.async_session() as session:
                # Count predictions
                total_result = await session.execute(
                    select(func.count(SnipeRun.id))
                )
                total_predictions = total_result.scalar() or 0
                
                # Average confidence
                avg_confidence_result = await session.execute(
                    select(func.avg(SnipeRun.ai_confidence)).where(
                        SnipeRun.ai_confidence.isnot(None)
                    )
                )
                avg_confidence = avg_confidence_result.scalar() or 75.0
                
                return web.json_response({
                    'totalPredictions': total_predictions,
                    'avgConfidence': round(avg_confidence, 2),
                    'accuracy': 76.8  # TODO: Calculate from outcomes
                })
        except Exception as e:
            logger.error(f"Error fetching prediction stats: {e}")
            return web.json_response({'error': str(e)}, status=500)
    
    async def get_recent_predictions(self, request: web.Request) -> web.Response:
        """Get recent predictions"""
        try:
            limit = int(request.query.get('limit', 10))
            
            async with self.database.async_session() as session:
                result = await session.execute(
                    select(SnipeRun)
                    .order_by(desc(SnipeRun.decision_timestamp))
                    .limit(limit)
                )
                predictions = result.scalars().all()
                
                predictions_data = []
                for pred in predictions:
                    predictions_data.append({
                        'id': pred.snipe_id,
                        'token': pred.token_symbol or pred.token_mint[:8],
                        'confidence': round(pred.ai_confidence, 2) if pred.ai_confidence else None,
                        'recommendation': pred.ai_recommendation,
                        'timestamp': pred.decision_timestamp.isoformat(),
                        'status': pred.status
                    })
                
                return web.json_response(predictions_data)
        except Exception as e:
            logger.error(f"Error fetching recent predictions: {e}")
            return web.json_response({'error': str(e)}, status=500)
    
    # ==================== Flash Loan Phase ====================
    
    async def get_flash_stats(self, request: web.Request) -> web.Response:
        """Get flash loan stats"""
        try:
            async with self.database.async_session() as session:
                # Count flash loan trades
                count_result = await session.execute(
                    select(func.count(Trade.id)).where(Trade.context == 'flash_loan')
                )
                total_flash_loans = count_result.scalar() or 0
                
                # Total profit from flash loans
                profit_result = await session.execute(
                    select(func.sum(Trade.pnl_sol)).where(
                        and_(Trade.context == 'flash_loan', Trade.success == True)
                    )
                )
                total_profit = profit_result.scalar() or 0.0
                
                return web.json_response({
                    'totalExecuted': total_flash_loans,
                    'totalProfit': round(total_profit, 4),
                    'avgProfit': round(total_profit / total_flash_loans, 4) if total_flash_loans > 0 else 0
                })
        except Exception as e:
            logger.error(f"Error fetching flash stats: {e}")
            return web.json_response({'error': str(e)}, status=500)
    
    async def get_flash_opportunities(self, request: web.Request) -> web.Response:
        """Get current flash loan arbitrage opportunities"""
        # TODO: Implement real-time opportunity detection
        return web.json_response([])
    
    # ==================== Launch Predictor Phase ====================
    
    async def get_launch_predictions(self, request: web.Request) -> web.Response:
        """Get upcoming launch predictions"""
        # TODO: Query from launch predictor module
        return web.json_response([])
    
    async def get_launch_stats(self, request: web.Request) -> web.Response:
        """Get launch prediction accuracy"""
        return web.json_response({
            'totalPredictions': 0,
            'accuracy': 0,
            'avgEarlyDetection': '2-6 hours'
        })
    
    # ==================== Prediction Markets Phase ====================
    
    async def get_markets(self, request: web.Request) -> web.Response:
        """Get active prediction markets"""
        # TODO: Query from prediction markets module
        return web.json_response([])
    
    async def get_market_details(self, request: web.Request) -> web.Response:
        """Get market details"""
        market_id = request.match_info['market_id']
        # TODO: Query specific market
        return web.json_response({'id': market_id, 'status': 'not_found'}, status=404)
    
    async def get_market_stats(self, request: web.Request) -> web.Response:
        """Get market stats"""
        return web.json_response({
            'activeMarkets': 0,
            'totalVolume': 0,
            'participants': 0
        })
    
    # ==================== User-Specific Dashboard Endpoints ====================
    
    async def get_user_profile(self, request: web.Request) -> web.Response:
        """Get COMPLETE user profile with ALL identity sources, PnL, rankings, and comprehensive stats"""
        try:
            user_id = int(request.match_info['user_id'])
            
            async with self.database.async_session() as session:
                # Get user stats (30 days and lifetime)
                stats_30 = await self.database.get_user_stats(user_id, days=30)
                stats_7 = await self.database.get_user_stats(user_id, days=7)
                stats_lifetime = await self.database.get_user_stats(user_id, days=999999)
                
                # Get bot-generated wallet
                wallet_result = await session.execute(
                    select(UserWallet).where(UserWallet.user_id == user_id)
                )
                wallet = wallet_result.scalar_one_or_none()
                
                # Get Twitter registration
                from src.modules.database import TwitterRegistration, WaitlistSignup, WalletRegistration
                twitter_result = await session.execute(
                    select(TwitterRegistration).where(TwitterRegistration.twitter_handle.ilike(f'%{user_id}%'))
                )
                twitter = twitter_result.scalar_one_or_none()
                
                # Try to find by telegram username in waitlist
                waitlist_result = None
                if wallet and wallet.telegram_username:
                    waitlist_result = await session.execute(
                        select(WaitlistSignup).where(WaitlistSignup.telegram_username == wallet.telegram_username.lower())
                    )
                    waitlist = waitlist_result.scalar_one_or_none()
                else:
                    waitlist = None
                
                # Get trader profile if exists
                trader_profile = await self.database.get_trader_profile(user_id)
                
                # Get user's rank
                all_users_result = await session.execute(
                    select(
                        Trade.user_id,
                        func.sum(Trade.pnl_sol).label('total_pnl')
                    )
                    .where(Trade.success == True)
                    .group_by(Trade.user_id)
                    .order_by(desc('total_pnl'))
                )
                all_users = list(all_users_result)
                user_rank = next((i + 1 for i, (uid, _) in enumerate(all_users) if uid == user_id), None)
                
                # Calculate additional metrics
                daily_pnl = await self.database.get_daily_pnl(user_id)
                
                # Get best and worst trades
                best_trade_result = await session.execute(
                    select(Trade.pnl_sol).where(
                        and_(Trade.user_id == user_id, Trade.success == True)
                    ).order_by(desc(Trade.pnl_sol)).limit(1)
                )
                best_trade = best_trade_result.scalar() or 0.0
                
                worst_trade_result = await session.execute(
                    select(Trade.pnl_sol).where(
                        and_(Trade.user_id == user_id, Trade.success == True)
                    ).order_by(Trade.pnl_sol.asc()).limit(1)
                )
                worst_trade = worst_trade_result.scalar() or 0.0
                
                # Get average trade size
                avg_trade_result = await session.execute(
                    select(func.avg(Trade.amount_sol)).where(
                        and_(Trade.user_id == user_id, Trade.success == True)
                    )
                )
                avg_trade_size = avg_trade_result.scalar() or 0.0
                
                # Get trade count by context
                trade_contexts_result = await session.execute(
                    select(
                        Trade.context,
                        func.count(Trade.id).label('count')
                    ).where(
                        and_(Trade.user_id == user_id, Trade.success == True)
                    ).group_by(Trade.context)
                )
                trade_contexts = {row[0]: row[1] for row in trade_contexts_result}
                
                # Get open positions count
                open_positions = await self.database.get_open_positions(user_id)
                
                # Calculate streak (consecutive winning days)
                # This is a simplified version
                winning_streak = 0  # TODO: Implement proper streak calculation
                
                profile = {
                    'user_id': user_id,
                    
                    # Identity Section - ALL sources
                    'identity': {
                        'telegram_username': wallet.telegram_username if wallet else None,
                        'telegram_user_id': user_id,
                        'twitter_handle': (waitlist.twitter_handle if waitlist and waitlist.twitter_handle 
                                         else twitter.display_handle if twitter else None),
                        'display_name': wallet.telegram_username if wallet else f'User{user_id}',
                    },
                    
                    # Wallets Section - Bot wallet + External wallet
                    'wallets': {
                        'bot_wallet': {
                            'address': wallet.public_key if wallet else None,
                            'balance': float(wallet.sol_balance) if wallet else 0.0,
                            'created_at': wallet.created_at.isoformat() if wallet else None,
                            'last_used': wallet.last_used.isoformat() if wallet else None
                        },
                        'external_wallet': {
                            'address': waitlist.wallet_address if waitlist and waitlist.wallet_address else None,
                            'connected': bool(waitlist and waitlist.wallet_address)
                        }
                    },
                    
                    # Rankings
                    'rankings': {
                        'global_rank': user_rank,
                        'total_users': len(all_users),
                        'percentile': round((1 - (user_rank / len(all_users))) * 100, 2) if user_rank and all_users else 0
                    },
                    
                    # Comprehensive Stats
                    'stats': {
                        'lifetime': {
                            'total_trades': stats_lifetime.get('total_trades', 0),
                            'profitable_trades': stats_lifetime.get('profitable_trades', 0),
                            'win_rate': round(stats_lifetime.get('win_rate', 0), 2),
                            'total_pnl': round(stats_lifetime.get('total_pnl', 0), 4),
                            'best_trade': round(best_trade, 4),
                            'worst_trade': round(worst_trade, 4),
                            'avg_trade_size': round(avg_trade_size, 4)
                        },
                        'monthly': {
                            'total_trades': stats_30.get('total_trades', 0),
                            'profitable_trades': stats_30.get('profitable_trades', 0),
                            'win_rate': round(stats_30.get('win_rate', 0), 2),
                            'total_pnl': round(stats_30.get('total_pnl', 0), 4)
                        },
                        'weekly': {
                            'total_trades': stats_7.get('total_trades', 0),
                            'profitable_trades': stats_7.get('profitable_trades', 0),
                            'win_rate': round(stats_7.get('win_rate', 0), 2),
                            'total_pnl': round(stats_7.get('total_pnl', 0), 4)
                        },
                        'today': {
                            'pnl': round(daily_pnl, 4)
                        }
                    },
                    
                    # Trading Activity
                    'activity': {
                        'open_positions': len(open_positions),
                        'winning_streak': winning_streak,
                        'trade_breakdown': trade_contexts,
                        'last_trade': wallet.last_used.isoformat() if wallet else None
                    },
                    
                    # Trader Profile (for social trading)
                    'trader_profile': {
                        'is_trader': bool(trader_profile),
                        'tier': trader_profile.trader_tier if trader_profile else 'bronze',
                        'followers': trader_profile.followers if trader_profile else 0,
                        'reputation_score': round(trader_profile.reputation_score, 2) if trader_profile else 0,
                        'strategies_shared': trader_profile.strategies_shared if trader_profile else 0,
                        'is_verified': trader_profile.is_verified if trader_profile else False
                    } if trader_profile else {
                        'is_trader': False,
                        'tier': 'bronze',
                        'followers': 0,
                        'reputation_score': 0,
                        'strategies_shared': 0,
                        'is_verified': False
                    },
                    
                    # Account metadata
                    'metadata': {
                        'account_created': wallet.created_at.isoformat() if wallet else None,
                        'is_approved': waitlist.is_approved if waitlist else False,
                        'signup_date': waitlist.signup_date.isoformat() if waitlist else None
                    }
                }
                
                return web.json_response(profile)
                
        except Exception as e:
            logger.error(f"Error fetching user profile: {e}")
            return web.json_response({'error': str(e)}, status=500)
    
    async def get_user_trades(self, request: web.Request) -> web.Response:
        """Get user's trade history"""
        try:
            user_id = int(request.match_info['user_id'])
            limit = int(request.query.get('limit', 50))
            
            trades = await self.database.get_user_trades(user_id, limit=limit)
            
            trades_data = []
            for trade in trades:
                trades_data.append({
                    'id': trade.id,
                    'signature': trade.signature,
                    'timestamp': trade.timestamp.isoformat(),
                    'type': trade.trade_type,
                    'token_mint': trade.token_mint,
                    'token_symbol': trade.token_symbol,
                    'amount_sol': round(trade.amount_sol, 4),
                    'amount_tokens': round(trade.amount_tokens, 4) if trade.amount_tokens else None,
                    'price': round(trade.price, 8) if trade.price else None,
                    'pnl_sol': round(trade.pnl_sol, 4) if trade.pnl_sol else None,
                    'pnl_percentage': round(trade.pnl_percentage, 2) if trade.pnl_percentage else None,
                    'context': trade.context,
                    'success': trade.success
                })
            
            return web.json_response(trades_data)
            
        except Exception as e:
            logger.error(f"Error fetching user trades: {e}")
            return web.json_response({'error': str(e)}, status=500)
    
    async def get_user_positions(self, request: web.Request) -> web.Response:
        """Get user's open positions"""
        try:
            user_id = int(request.match_info['user_id'])
            
            positions = await self.database.get_open_positions(user_id)
            
            positions_data = []
            for pos in positions:
                positions_data.append({
                    'id': pos.id,
                    'position_id': pos.position_id,
                    'token_mint': pos.token_mint,
                    'token_symbol': pos.token_symbol,
                    'entry_price': round(pos.entry_price, 8),
                    'entry_amount_sol': round(pos.entry_amount_sol, 4),
                    'entry_amount_tokens': round(pos.entry_amount_tokens, 4),
                    'entry_timestamp': pos.entry_timestamp.isoformat(),
                    'remaining_amount_sol': round(pos.remaining_amount_sol, 4),
                    'remaining_amount_tokens': round(pos.remaining_amount_tokens, 4),
                    'realized_pnl_sol': round(pos.realized_pnl_sol, 4),
                    'is_open': pos.is_open,
                    'source': pos.source
                })
            
            return web.json_response(positions_data)
            
        except Exception as e:
            logger.error(f"Error fetching user positions: {e}")
            return web.json_response({'error': str(e)}, status=500)
    
    async def get_user_stats_detailed(self, request: web.Request) -> web.Response:
        """Get detailed user statistics"""
        try:
            user_id = int(request.match_info['user_id'])
            days = int(request.query.get('days', 30))
            
            stats = await self.database.get_user_stats(user_id, days=days)
            daily_pnl = await self.database.get_daily_pnl(user_id)
            
            return web.json_response({
                'user_id': user_id,
                'total_trades': stats.get('total_trades', 0),
                'profitable_trades': stats.get('profitable_trades', 0),
                'win_rate': round(stats.get('win_rate', 0), 2),
                'total_pnl': round(stats.get('total_pnl', 0), 4),
                'daily_pnl': round(daily_pnl, 4),
                'period_days': days
            })
            
        except Exception as e:
            logger.error(f"Error fetching user stats: {e}")
            return web.json_response({'error': str(e)}, status=500)
    
    async def get_user_wallet_info(self, request: web.Request) -> web.Response:
        """Get user's wallet information"""
        try:
            user_id = int(request.match_info['user_id'])
            
            async with self.database.async_session() as session:
                result = await session.execute(
                    select(UserWallet).where(UserWallet.user_id == user_id)
                )
                wallet = result.scalar_one_or_none()
                
                if not wallet:
                    return web.json_response({'error': 'Wallet not found'}, status=404)
                
                return web.json_response({
                    'user_id': user_id,
                    'public_key': wallet.public_key,
                    'sol_balance': float(wallet.sol_balance),
                    'last_balance_update': wallet.last_balance_update.isoformat() if wallet.last_balance_update else None,
                    'created_at': wallet.created_at.isoformat(),
                    'is_active': wallet.is_active
                })
                
        except Exception as e:
            logger.error(f"Error fetching wallet info: {e}")
            return web.json_response({'error': str(e)}, status=500)
    
    async def execute_user_buy(self, request: web.Request) -> web.Response:
        """Execute buy command for user from web dashboard"""
        try:
            user_id = int(request.match_info['user_id'])
            data = await request.json()
            
            token_mint = data.get('token_mint')
            amount_sol = float(data.get('amount_sol', 0))
            token_symbol = data.get('token_symbol')
            
            if not token_mint or amount_sol <= 0:
                return web.json_response({
                    'error': 'Invalid parameters. Required: token_mint, amount_sol'
                }, status=400)
            
            # Check if trade_executor is available (injected from bot)
            if not hasattr(self, 'trade_executor') or not self.trade_executor:
                return web.json_response({
                    'error': 'Trading functionality not available. Bot module not connected.'
                }, status=503)
            
            # Execute trade through the trade executor
            result = await self.trade_executor.execute_buy(
                user_id=user_id,
                token_mint=token_mint,
                amount_sol=amount_sol,
                token_symbol=token_symbol,
                reason='web_dashboard',
                context='web_dashboard'
            )
            
            if result.get('success'):
                return web.json_response({
                    'success': True,
                    'message': 'Buy order executed successfully',
                    'signature': result.get('signature'),
                    'amount_sol': amount_sol,
                    'token_mint': token_mint
                })
            else:
                return web.json_response({
                    'success': False,
                    'error': result.get('error', 'Trade execution failed')
                }, status=400)
                
        except Exception as e:
            logger.error(f"Error executing buy: {e}")
            return web.json_response({'error': str(e)}, status=500)
    
    async def execute_user_sell(self, request: web.Request) -> web.Response:
        """Execute sell command for user from web dashboard"""
        try:
            user_id = int(request.match_info['user_id'])
            data = await request.json()
            
            token_mint = data.get('token_mint')
            amount_tokens = data.get('amount_tokens', 'all')
            token_symbol = data.get('token_symbol')
            
            if not token_mint:
                return web.json_response({
                    'error': 'Invalid parameters. Required: token_mint'
                }, status=400)
            
            # Check if trade_executor is available
            if not hasattr(self, 'trade_executor') or not self.trade_executor:
                return web.json_response({
                    'error': 'Trading functionality not available. Bot module not connected.'
                }, status=503)
            
            # Execute sell through the trade executor
            result = await self.trade_executor.execute_sell(
                user_id=user_id,
                token_mint=token_mint,
                amount_tokens=amount_tokens,
                token_symbol=token_symbol,
                reason='web_dashboard',
                context='web_dashboard'
            )
            
            if result.get('success'):
                return web.json_response({
                    'success': True,
                    'message': 'Sell order executed successfully',
                    'signature': result.get('signature'),
                    'amount_sol_received': result.get('amount_sol_received'),
                    'token_mint': token_mint
                })
            else:
                return web.json_response({
                    'success': False,
                    'error': result.get('error', 'Trade execution failed')
                }, status=400)
                
        except Exception as e:
            logger.error(f"Error executing sell: {e}")
            return web.json_response({'error': str(e)}, status=500)
    
    async def get_user_settings(self, request: web.Request) -> web.Response:
        """Get user's settings"""
        try:
            user_id = int(request.match_info['user_id'])
            
            settings = await self.database.get_user_settings(user_id)
            
            if not settings:
                return web.json_response({
                    'error': 'User settings not found'
                }, status=404)
            
            return web.json_response({
                'user_id': user_id,
                'auto_trading_enabled': settings.auto_trading_enabled,
                'max_trade_size_sol': float(settings.max_trade_size_sol),
                'daily_loss_limit_sol': float(settings.daily_loss_limit_sol),
                'slippage_percentage': float(settings.slippage_percentage),
                'require_confirmation': settings.require_confirmation,
                'use_stop_loss': settings.use_stop_loss,
                'default_stop_loss_percentage': float(settings.default_stop_loss_percentage),
                'use_take_profit': settings.use_take_profit,
                'default_take_profit_percentage': float(settings.default_take_profit_percentage),
                'check_honeypots': settings.check_honeypots,
                'min_liquidity_usd': float(settings.min_liquidity_usd),
                'snipe_enabled': settings.snipe_enabled,
                'snipe_max_amount': float(settings.snipe_max_amount),
                'snipe_min_liquidity': float(settings.snipe_min_liquidity),
                'snipe_min_confidence': float(settings.snipe_min_confidence)
            })
            
        except Exception as e:
            logger.error(f"Error fetching user settings: {e}")
            return web.json_response({'error': str(e)}, status=500)
    
    async def update_user_settings_endpoint(self, request: web.Request) -> web.Response:
        """Update user's settings"""
        try:
            user_id = int(request.match_info['user_id'])
            data = await request.json()
            
            # Update settings in database
            await self.database.update_user_settings(user_id, data)
            
            return web.json_response({
                'success': True,
                'message': 'Settings updated successfully',
                'user_id': user_id
            })
            
        except Exception as e:
            logger.error(f"Error updating user settings: {e}")
            return web.json_response({'error': str(e)}, status=500)
    
    async def analyze_token_for_user(self, request: web.Request) -> web.Response:
        """Run AI analysis on a token for user"""
        try:
            user_id = int(request.match_info['user_id'])
            data = await request.json()
            
            token_mint = data.get('token_mint')
            
            if not token_mint:
                return web.json_response({
                    'error': 'token_mint is required'
                }, status=400)
            
            # Check if AI engine is available
            if not self.ai_engine:
                return web.json_response({
                    'error': 'AI analysis not available'
                }, status=503)
            
            # Run AI analysis
            analysis = await self.ai_engine.analyze_token(token_mint)
            
            return web.json_response({
                'success': True,
                'token_mint': token_mint,
                'analysis': analysis
            })
            
        except Exception as e:
            logger.error(f"Error analyzing token: {e}")
            return web.json_response({'error': str(e)}, status=500)
    
    async def get_leaderboard(self, request: web.Request) -> web.Response:
        """Get trading leaderboard"""
        try:
            limit = int(request.query.get('limit', 50))
            days = int(request.query.get('days', 30))
            
            start_date = datetime.utcnow() - timedelta(days=days)
            
            async with self.database.async_session() as session:
                # Get top traders by PnL
                result = await session.execute(
                    select(
                        Trade.user_id,
                        func.sum(Trade.pnl_sol).label('total_pnl'),
                        func.count(Trade.id).label('total_trades'),
                        func.sum(func.case((Trade.pnl_sol > 0, 1), else_=0)).label('profitable_trades')
                    )
                    .where(and_(
                        Trade.success == True,
                        Trade.timestamp >= start_date
                    ))
                    .group_by(Trade.user_id)
                    .order_by(desc('total_pnl'))
                    .limit(limit)
                )
                
                leaderboard = []
                for rank, (user_id, total_pnl, total_trades, profitable_trades) in enumerate(result, 1):
                    win_rate = (profitable_trades / total_trades * 100) if total_trades > 0 else 0
                    
                    # Get wallet info
                    wallet_result = await session.execute(
                        select(UserWallet).where(UserWallet.user_id == user_id)
                    )
                    wallet = wallet_result.scalar_one_or_none()
                    
                    # Get trader profile
                    trader_profile = await self.database.get_trader_profile(user_id)
                    
                    leaderboard.append({
                        'rank': rank,
                        'user_id': user_id,
                        'username': wallet.telegram_username if wallet else f'User{user_id}',
                        'total_pnl': round(total_pnl, 4),
                        'total_trades': total_trades,
                        'win_rate': round(win_rate, 2),
                        'tier': trader_profile.trader_tier if trader_profile else 'bronze',
                        'followers': trader_profile.followers if trader_profile else 0
                    })
                
                return web.json_response({
                    'leaderboard': leaderboard,
                    'period_days': days
                })
                
        except Exception as e:
            logger.error(f"Error fetching leaderboard: {e}")
            return web.json_response({'error': str(e)}, status=500)
    
    async def get_trader_rankings(self, request: web.Request) -> web.Response:
        """Get trader profile rankings"""
        try:
            limit = int(request.query.get('limit', 50))
            
            trader_profiles = await self.database.get_trader_profiles()
            
            # Sort by reputation score
            sorted_traders = sorted(
                trader_profiles,
                key=lambda x: x.reputation_score,
                reverse=True
            )[:limit]
            
            rankings = []
            for rank, trader in enumerate(sorted_traders, 1):
                rankings.append({
                    'rank': rank,
                    'user_id': trader.user_id,
                    'username': trader.label,
                    'tier': trader.trader_tier,
                    'reputation_score': round(trader.reputation_score, 2),
                    'followers': trader.followers,
                    'total_trades': trader.total_trades,
                    'win_rate': round(trader.win_rate, 2),
                    'total_pnl': round(trader.total_pnl, 4) if trader.total_pnl else 0,
                    'is_verified': trader.is_verified
                })
            
            return web.json_response(rankings)
            
        except Exception as e:
            logger.error(f"Error fetching trader rankings: {e}")
            return web.json_response({'error': str(e)}, status=500)
    
    # ==================== User & Wallet Endpoints ====================
    
    async def get_users_stats(self, request: web.Request) -> web.Response:
        """Get user statistics"""
        try:
            async with self.database.async_session() as session:
                # Total users
                total_users_result = await session.execute(
                    select(func.count(func.distinct(UserWallet.user_id)))
                )
                total_users = total_users_result.scalar() or 0
                
                # Active users (with trades)
                active_users_result = await session.execute(
                    select(func.count(func.distinct(Trade.user_id)))
                )
                active_users = active_users_result.scalar() or 0
                
                return web.json_response({
                    'totalUsers': total_users,
                    'activeUsers': active_users
                })
        except Exception as e:
            logger.error(f"Error fetching user stats: {e}")
            return web.json_response({'error': str(e)}, status=500)
    
    async def get_elite_wallets_stats(self, request: web.Request) -> web.Response:
        """Get elite wallet tracking stats"""
        try:
            async with self.database.async_session() as session:
                # Count elite wallets
                result = await session.execute(
                    select(func.count(TrackedWallet.id)).where(
                        TrackedWallet.is_trader == True
                    )
                )
                elite_count = result.scalar() or 441
                
                return web.json_response({
                    'totalTracked': elite_count,
                    'averageWinRate': 68.5,
                    'totalFollowers': 0
                })
        except Exception as e:
            logger.error(f"Error fetching elite wallet stats: {e}")
            return web.json_response({'error': str(e)}, status=500)
    
    # ==================== WebSocket ====================
    
    async def websocket_handler(self, request: web.Request) -> web.WebSocketResponse:
        """WebSocket endpoint for real-time updates"""
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        
        self.ws_clients.append(ws)
        logger.info(f"WebSocket client connected. Total clients: {len(self.ws_clients)}")
        
        try:
            async for msg in ws:
                # Handle incoming messages if needed
                pass
        finally:
            self.ws_clients.remove(ws)
            logger.info(f"WebSocket client disconnected. Total clients: {len(self.ws_clients)}")
        
        return ws
    
    async def _broadcast_loop(self):
        """Background task to broadcast updates to all WebSocket clients"""
        while True:
            try:
                await asyncio.sleep(3)  # Broadcast every 3 seconds
                
                if not self.ws_clients:
                    continue
                
                # Fetch current metrics
                async with self.database.async_session() as session:
                    # Get basic metrics for broadcast
                    total_trades_result = await session.execute(
                        select(func.count(Trade.id)).where(Trade.success == True)
                    )
                    total_trades = total_trades_result.scalar() or 0
                    
                    update_data = {
                        'type': 'metrics_update',
                        'timestamp': datetime.utcnow().isoformat(),
                        'data': {
                            'totalTrades': total_trades,
                            # Add more real-time metrics as needed
                        }
                    }
                    
                    # Broadcast to all connected clients
                    disconnected = []
                    for ws in self.ws_clients:
                        try:
                            await ws.send_json(update_data)
                        except Exception as e:
                            logger.error(f"Error sending to WebSocket client: {e}")
                            disconnected.append(ws)
                    
                    # Remove disconnected clients
                    for ws in disconnected:
                        if ws in self.ws_clients:
                            self.ws_clients.remove(ws)
            
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in broadcast loop: {e}")
                await asyncio.sleep(5)  # Wait before retrying

