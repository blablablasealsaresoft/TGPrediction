#!/usr/bin/env python3
"""
Continuous bot health monitoring script
Checks key metrics and alerts if thresholds exceeded
"""

import asyncio
import os
import sys
import json
from pathlib import Path
from datetime import datetime, timedelta
import aiohttp

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from dotenv import load_dotenv
load_dotenv()

class HealthMonitor:
    def __init__(self):
        self.alerts = []
        
    async def check_http_health(self):
        """Check HTTP health endpoint"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get('http://localhost:8080/health', timeout=5) as resp:
                    if resp.status == 200:
                        return {'status': 'ok', 'code': resp.status}
                    return {'status': 'degraded', 'code': resp.status}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    async def check_database(self):
        """Check database connectivity"""
        try:
            import asyncpg
            db_url = os.getenv('DATABASE_URL', 'postgresql://trader:T_TleomdfYmv-13lnjehNu7xp-q99RRXyW13XreWof8@localhost:5432/trading_bot')
            if db_url.startswith('postgresql+asyncpg://'):
                db_url = db_url.replace('postgresql+asyncpg://', 'postgresql://')
            
            conn = await asyncpg.connect(db_url, timeout=5)
            
            # Check table counts
            trades = await conn.fetchval("SELECT COUNT(*) FROM trades")
            wallets = await conn.fetchval("SELECT COUNT(*) FROM tracked_wallets")
            users = await conn.fetchval("SELECT COUNT(*) FROM user_wallets")
            
            await conn.close()
            
            return {
                'status': 'ok',
                'trades': trades,
                'wallets': wallets,
                'users': users
            }
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def check_log_errors(self):
        """Check for recent errors in logs"""
        log_file = Path('logs/trading_bot.jsonl')
        
        if not log_file.exists():
            return {'status': 'no_logs', 'count': 0}
        
        errors = []
        warnings = []
        
        try:
            # Read last 1000 lines
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                recent_lines = lines[-1000:] if len(lines) > 1000 else lines
            
            for line in recent_lines:
                try:
                    log_entry = json.loads(line)
                    level = log_entry.get('level', '')
                    
                    if level == 'ERROR':
                        errors.append(log_entry)
                    elif level == 'WARNING':
                        warnings.append(log_entry)
                except:
                    continue
            
            return {
                'status': 'ok',
                'error_count': len(errors),
                'warning_count': len(warnings),
                'recent_errors': errors[-5:] if errors else []
            }
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def generate_alert(self, category, message, severity='warning'):
        """Generate an alert"""
        alert = {
            'timestamp': datetime.now().isoformat(),
            'category': category,
            'message': message,
            'severity': severity
        }
        self.alerts.append(alert)
        return alert
    
    async def run_health_check(self):
        """Run complete health check"""
        print("="*60)
        print(f"🏥 BOT HEALTH MONITOR - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60)
        print()
        
        # Check HTTP endpoint
        print("🌐 HTTP Health Endpoint:")
        http_health = await self.check_http_health()
        if http_health['status'] == 'ok':
            print(f"   ✅ Responding (status {http_health['code']})")
        else:
            print(f"   ⚠️  {http_health.get('message', 'Not responding')}")
            self.generate_alert('http', 'Health endpoint not responding', 'warning')
        
        print()
        
        # Check database
        print("🗄️  Database:")
        db_health = await self.check_database()
        if db_health['status'] == 'ok':
            print(f"   ✅ Connected")
            print(f"   📊 Trades: {db_health['trades']}")
            print(f"   👥 Users: {db_health['users']}")
            print(f"   💼 Tracked Wallets: {db_health['wallets']}")
            
            if db_health['wallets'] < 400:
                self.generate_alert('database', f"Low wallet count: {db_health['wallets']}", 'warning')
        else:
            print(f"   ❌ Connection failed: {db_health.get('message', 'Unknown error')}")
            self.generate_alert('database', 'Database connection failed', 'critical')
        
        print()
        
        # Check logs
        print("📝 Log Analysis:")
        log_check = self.check_log_errors()
        if log_check['status'] == 'ok':
            error_count = log_check['error_count']
            warning_count = log_check['warning_count']
            
            print(f"   Errors (last 1000 lines): {error_count}")
            print(f"   Warnings (last 1000 lines): {warning_count}")
            
            if error_count > 10:
                print(f"   ⚠️  High error rate detected!")
                self.generate_alert('logs', f'High error count: {error_count}', 'warning')
            
            if log_check['recent_errors']:
                print(f"   Recent errors:")
                for err in log_check['recent_errors']:
                    print(f"     - {err.get('event', 'Unknown error')}")
        else:
            print(f"   ⚠️  Unable to read logs: {log_check.get('message', 'No logs')}")
        
        print()
        print("="*60)
        
        # Summary
        if self.alerts:
            print(f"⚠️  {len(self.alerts)} ALERT(S) GENERATED:")
            for alert in self.alerts:
                severity_icon = "🔴" if alert['severity'] == 'critical' else "🟡"
                print(f"   {severity_icon} [{alert['category']}] {alert['message']}")
            print()
            return False
        else:
            print("✅ ALL CHECKS PASSED - System healthy!")
            print()
            return True

async def main():
    monitor = HealthMonitor()
    healthy = await monitor.run_health_check()
    
    print("📋 Recommendations:")
    print("  - Run this script daily")
    print("  - Check Telegram /metrics command")
    print("  - Review logs/trading_bot.jsonl for patterns")
    print("  - Backup database weekly: python scripts/create_db_backup.ps1")
    print()
    
    return 0 if healthy else 1

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\nMonitoring cancelled")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Monitor failed: {e}")
        sys.exit(1)

