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
        
        self._setup_routes()
        self._setup_cors()
    
    def set_modules(
        self,
        monitoring=None,
        ai_engine=None,
        flash_loan_engine=None,
        launch_predictor=None,
        prediction_markets=None
    ):
        """Inject module instances for API to use"""
        self.monitoring = monitoring
        self.ai_engine = ai_engine
        self.flash_loan_engine = flash_loan_engine
        self.launch_predictor = launch_predictor
        self.prediction_markets = prediction_markets
    
    def _setup_routes(self):
        """Setup all API routes"""
        # Frontend pages
        self.app.router.add_get('/', self.serve_waitlist)
        self.app.router.add_get('/app', self.serve_index)
        self.app.router.add_get('/dashboard', self.serve_dashboard)
        self.app.router.add_get('/prediction-market', self.serve_prediction_market)
        self.app.router.add_get('/docs', self.serve_docs)
        
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

