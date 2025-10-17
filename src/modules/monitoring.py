"""
Monitoring and Alerting Module
Tracks bot health, performance, and sends alerts
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from telegram import Bot
from telegram.error import TelegramError

logger = logging.getLogger(__name__)


class BotMonitor:
    """Monitor bot health and performance"""
    
    def __init__(self, bot: Bot, admin_chat_id: Optional[int] = None):
        self.bot = bot
        self.admin_chat_id = admin_chat_id
        
        # Metrics
        self.start_time = datetime.utcnow()
        self.total_requests = 0
        self.successful_trades = 0
        self.failed_trades = 0
        self.errors: List[Dict] = []
        self.last_heartbeat = datetime.utcnow()
        
        # Alerts
        self.alert_cooldown: Dict[str, datetime] = {}
        self.alert_cooldown_seconds = 300  # 5 minutes
    
    def record_request(self):
        """Record an API request"""
        self.total_requests += 1
    
    def record_trade_success(self):
        """Record successful trade"""
        self.successful_trades += 1
    
    def record_trade_failure(self, error: str):
        """Record failed trade"""
        self.failed_trades += 1
        self.errors.append({
            'timestamp': datetime.utcnow(),
            'type': 'trade_failure',
            'message': error
        })
    
    def record_error(self, error_type: str, message: str):
        """Record an error"""
        self.errors.append({
            'timestamp': datetime.utcnow(),
            'type': error_type,
            'message': message
        })
        
        # Keep only last 100 errors
        if len(self.errors) > 100:
            self.errors = self.errors[-100:]
    
    def update_heartbeat(self):
        """Update heartbeat timestamp"""
        self.last_heartbeat = datetime.utcnow()
    
    async def send_alert(self, alert_type: str, message: str):
        """Send alert to admin"""
        if not self.admin_chat_id:
            return
        
        # Check cooldown
        cooldown_key = f"{alert_type}:{message[:50]}"
        if cooldown_key in self.alert_cooldown:
            time_since_last = (datetime.utcnow() - self.alert_cooldown[cooldown_key]).seconds
            if time_since_last < self.alert_cooldown_seconds:
                return  # Skip duplicate alert
        
        try:
            alert_message = f"🚨 *ALERT*\n\n"
            alert_message += f"Type: `{alert_type}`\n"
            alert_message += f"Time: `{datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}`\n\n"
            alert_message += f"{message}"
            
            await self.bot.send_message(
                chat_id=self.admin_chat_id,
                text=alert_message,
                parse_mode='Markdown'
            )
            
            # Update cooldown
            self.alert_cooldown[cooldown_key] = datetime.utcnow()
            
        except TelegramError as e:
            logger.error(f"Failed to send alert: {e}")
    
    def get_stats(self) -> Dict:
        """Get current statistics"""
        uptime = datetime.utcnow() - self.start_time
        success_rate = (
            self.successful_trades / (self.successful_trades + self.failed_trades) * 100
            if (self.successful_trades + self.failed_trades) > 0
            else 0
        )
        
        return {
            'uptime_seconds': uptime.total_seconds(),
            'uptime_hours': uptime.total_seconds() / 3600,
            'total_requests': self.total_requests,
            'successful_trades': self.successful_trades,
            'failed_trades': self.failed_trades,
            'success_rate': success_rate,
            'recent_errors': len(self.errors),
            'last_heartbeat': self.last_heartbeat
        }
    
    def get_health_status(self) -> Dict:
        """Get health status"""
        stats = self.get_stats()
        
        # Determine health
        is_healthy = True
        issues = []
        
        # Check heartbeat
        heartbeat_age = (datetime.utcnow() - self.last_heartbeat).seconds
        if heartbeat_age > 300:  # 5 minutes
            is_healthy = False
            issues.append("No heartbeat in 5 minutes")
        
        # Check success rate
        if stats['success_rate'] < 50 and (self.successful_trades + self.failed_trades) > 10:
            is_healthy = False
            issues.append(f"Low success rate: {stats['success_rate']:.1f}%")
        
        # Check recent errors
        recent_errors = [e for e in self.errors if (datetime.utcnow() - e['timestamp']).seconds < 3600]
        if len(recent_errors) > 10:
            is_healthy = False
            issues.append(f"Many recent errors: {len(recent_errors)}")
        
        return {
            'healthy': is_healthy,
            'issues': issues,
            'stats': stats
        }
    
    async def check_and_alert(self):
        """Check health and send alerts if needed"""
        health = self.get_health_status()
        
        if not health['healthy']:
            issues_text = "\n".join(f"• {issue}" for issue in health['issues'])
            await self.send_alert(
                "HEALTH_CHECK",
                f"Bot health issues detected:\n\n{issues_text}"
            )


class PerformanceTracker:
    """Track trading performance metrics"""
    
    def __init__(self):
        self.trades: List[Dict] = []
        self.daily_pnl: Dict[str, float] = {}
    
    def record_trade(self, trade_data: Dict):
        """Record a trade"""
        self.trades.append({
            **trade_data,
            'timestamp': datetime.utcnow()
        })
        
        # Update daily PnL
        date = datetime.utcnow().strftime('%Y-%m-%d')
        if date not in self.daily_pnl:
            self.daily_pnl[date] = 0.0
        
        pnl = trade_data.get('pnl', 0.0)
        self.daily_pnl[date] += pnl
    
    def get_performance_summary(self, days: int = 7) -> Dict:
        """Get performance summary"""
        cutoff = datetime.utcnow() - timedelta(days=days)
        recent_trades = [t for t in self.trades if t['timestamp'] > cutoff]
        
        if not recent_trades:
            return {
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'win_rate': 0,
                'total_pnl': 0,
                'avg_win': 0,
                'avg_loss': 0,
                'largest_win': 0,
                'largest_loss': 0
            }
        
        winning_trades = [t for t in recent_trades if t.get('pnl', 0) > 0]
        losing_trades = [t for t in recent_trades if t.get('pnl', 0) < 0]
        
        total_pnl = sum(t.get('pnl', 0) for t in recent_trades)
        
        return {
            'total_trades': len(recent_trades),
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'win_rate': len(winning_trades) / len(recent_trades) * 100,
            'total_pnl': total_pnl,
            'avg_win': sum(t['pnl'] for t in winning_trades) / len(winning_trades) if winning_trades else 0,
            'avg_loss': sum(t['pnl'] for t in losing_trades) / len(losing_trades) if losing_trades else 0,
            'largest_win': max((t['pnl'] for t in winning_trades), default=0),
            'largest_loss': min((t['pnl'] for t in losing_trades), default=0),
            'period_days': days
        }
    
    def get_daily_pnl_chart(self, days: int = 30) -> List[Dict]:
        """Get daily PnL data for charting"""
        chart_data = []
        for i in range(days):
            date = (datetime.utcnow() - timedelta(days=i)).strftime('%Y-%m-%d')
            pnl = self.daily_pnl.get(date, 0.0)
            chart_data.append({
                'date': date,
                'pnl': pnl
            })
        return chart_data[::-1]  # Reverse to oldest first


class RateLimiter:
    """Rate limiting for API calls"""
    
    def __init__(self, max_calls: int = 100, period_seconds: int = 60):
        self.max_calls = max_calls
        self.period_seconds = period_seconds
        self.calls: List[datetime] = []
    
    async def acquire(self):
        """Wait if necessary to respect rate limit"""
        now = datetime.utcnow()
        
        # Remove old calls outside the window
        cutoff = now - timedelta(seconds=self.period_seconds)
        self.calls = [c for c in self.calls if c > cutoff]
        
        # Check if we need to wait
        if len(self.calls) >= self.max_calls:
            oldest_call = self.calls[0]
            wait_time = self.period_seconds - (now - oldest_call).seconds
            if wait_time > 0:
                logger.info(f"Rate limit reached, waiting {wait_time}s")
                await asyncio.sleep(wait_time)
                return await self.acquire()
        
        # Record this call
        self.calls.append(now)
    
    def get_remaining_calls(self) -> int:
        """Get number of remaining calls in current window"""
        now = datetime.utcnow()
        cutoff = now - timedelta(seconds=self.period_seconds)
        recent_calls = [c for c in self.calls if c > cutoff]
        return max(0, self.max_calls - len(recent_calls))


class HealthCheckServer:
    """Simple health check endpoint"""
    
    def __init__(self, monitor: BotMonitor, port: int = 8080):
        self.monitor = monitor
        self.port = port
    
    async def start(self):
        """Start health check server"""
        from aiohttp import web
        
        async def health_check(request):
            """Health check endpoint"""
            health = self.monitor.get_health_status()
            
            if health['healthy']:
                return web.json_response({
                    'status': 'healthy',
                    'stats': health['stats']
                }, status=200)
            else:
                return web.json_response({
                    'status': 'unhealthy',
                    'issues': health['issues'],
                    'stats': health['stats']
                }, status=503)
        
        async def metrics(request):
            """Metrics endpoint"""
            stats = self.monitor.get_stats()
            return web.json_response(stats)
        
        app = web.Application()
        app.router.add_get('/health', health_check)
        app.router.add_get('/metrics', metrics)
        
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, 'localhost', self.port)
        await site.start()
        
        logger.info(f"Health check server started on port {self.port}")


# Example usage in main bot
async def monitor_bot_health(monitor: BotMonitor):
    """Background task to monitor bot health"""
    while True:
        try:
            await asyncio.sleep(300)  # Check every 5 minutes
            monitor.update_heartbeat()
            await monitor.check_and_alert()
        except Exception as e:
            logger.error(f"Health monitoring error: {e}")
