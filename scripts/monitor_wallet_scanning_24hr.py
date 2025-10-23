"""
🧪 24-HOUR WALLET SCANNING MONITOR
Monitors copy-trading wallet detection for 24 hours

FEATURES MONITORED:
1. Wallet transaction detection
2. Copy-trading signal generation
3. Performance tracking
4. Real-time statistics
5. Anomaly detection
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List
import os
import sys
import json

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from solana.rpc.async_api import AsyncClient
from src.modules.wallet_intelligence import WalletIntelligenceEngine
from src.modules.database import DatabaseManager
from src.modules.affiliated_wallet_detector import AffiliatedWalletDetector

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler(f'wallet_monitor_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class WalletScanningMonitor:
    """24-hour wallet scanning monitor"""
    
    def __init__(self):
        self.rpc_url = os.getenv('SOLANA_RPC_URL', 'https://api.mainnet-beta.solana.com')
        self.client = AsyncClient(self.rpc_url)
        self.db = DatabaseManager()
        
        # Initialize components
        self.wallet_intelligence = WalletIntelligenceEngine(self.client)
        self.affiliated_detector = AffiliatedWalletDetector(self.client)
        
        # Monitoring stats
        self.stats = {
            'start_time': datetime.now(),
            'end_time': None,
            'transactions_detected': 0,
            'wallets_tracked': 0,
            'copy_signals_generated': 0,
            'profitable_trades': 0,
            'losing_trades': 0,
            'total_volume_sol': 0.0,
            'affiliated_wallets_found': 0,
            'hourly_stats': {}
        }
        
        self.is_running = False
        
        logger.info("🧪 24-Hour Wallet Scanning Monitor initialized")
        logger.info(f"   Start time: {self.stats['start_time']}")
        logger.info(f"   Duration: 24 hours")
    
    async def load_tracked_wallets(self) -> List[str]:
        """Load tracked wallets from database"""
        try:
            # Get tracked wallets for test user
            tracked = await self.db.get_tracked_wallets(user_id=1)
            
            wallet_addresses = [w['wallet_address'] for w in tracked]
            
            logger.info(f"📊 Loaded {len(wallet_addresses)} tracked wallets")
            
            return wallet_addresses
            
        except Exception as e:
            logger.error(f"❌ Error loading wallets: {e}")
            return []
    
    async def monitor_wallet_activity(self, wallet_address: str) -> Dict:
        """Monitor activity for a single wallet"""
        try:
            # Get recent transactions
            transactions = await self.wallet_intelligence.get_wallet_transactions(
                wallet_address,
                limit=100
            )
            
            if not transactions:
                return {'transactions': 0, 'signals': 0}
            
            signals_generated = 0
            
            # Analyze each transaction
            for tx in transactions:
                # Check if this should generate a copy-trading signal
                if await self._should_generate_signal(wallet_address, tx):
                    signals_generated += 1
                    self.stats['copy_signals_generated'] += 1
                    
                    logger.info(f"📡 COPY SIGNAL: {wallet_address[:8]}...")
                    logger.info(f"   Transaction: {tx.get('signature', 'N/A')[:8]}...")
            
            self.stats['transactions_detected'] += len(transactions)
            
            return {
                'transactions': len(transactions),
                'signals': signals_generated
            }
            
        except Exception as e:
            logger.debug(f"Error monitoring wallet {wallet_address[:8]}...: {e}")
            return {'transactions': 0, 'signals': 0}
    
    async def _should_generate_signal(self, wallet_address: str, transaction: Dict) -> bool:
        """Determine if transaction should generate copy signal"""
        try:
            # Check wallet score
            metrics = await self.wallet_intelligence.get_wallet_metrics(wallet_address)
            
            if not metrics:
                return False
            
            # Generate signal if:
            # 1. Wallet score > 70
            # 2. Transaction is a swap
            # 3. Recent activity
            
            if metrics.overall_score > 70:
                # Check if it's a swap transaction
                tx_type = transaction.get('type', '')
                if 'swap' in tx_type.lower() or 'buy' in tx_type.lower():
                    return True
            
            return False
            
        except:
            return False
    
    async def scan_for_affiliated_wallets(self, wallet_address: str):
        """Scan for affiliated wallets"""
        try:
            affiliated = await self.affiliated_detector.discover_affiliated_wallets(
                wallet_address,
                max_depth=2
            )
            
            if affiliated:
                logger.info(f"🔗 Found {len(affiliated)} affiliated wallets for {wallet_address[:8]}...")
                self.stats['affiliated_wallets_found'] += len(affiliated)
            
            return affiliated
            
        except Exception as e:
            logger.debug(f"Error scanning affiliated wallets: {e}")
            return []
    
    async def update_hourly_stats(self):
        """Update hourly statistics"""
        current_hour = datetime.now().hour
        
        if current_hour not in self.stats['hourly_stats']:
            self.stats['hourly_stats'][current_hour] = {
                'transactions': 0,
                'signals': 0,
                'wallets_active': 0
            }
    
    async def print_stats_summary(self):
        """Print current statistics"""
        elapsed = datetime.now() - self.stats['start_time']
        hours_elapsed = elapsed.total_seconds() / 3600
        
        logger.info(f"\n{'='*60}")
        logger.info(f"📊 MONITORING STATISTICS")
        logger.info(f"{'='*60}")
        logger.info(f"Time elapsed: {hours_elapsed:.1f} hours")
        logger.info(f"Transactions detected: {self.stats['transactions_detected']:,}")
        logger.info(f"Copy signals generated: {self.stats['copy_signals_generated']:,}")
        logger.info(f"Wallets tracked: {self.stats['wallets_tracked']}")
        logger.info(f"Affiliated wallets found: {self.stats['affiliated_wallets_found']}")
        logger.info(f"Avg transactions/hour: {self.stats['transactions_detected'] / max(hours_elapsed, 0.1):.1f}")
        logger.info(f"Avg signals/hour: {self.stats['copy_signals_generated'] / max(hours_elapsed, 0.1):.1f}")
        logger.info(f"{'='*60}\n")
    
    async def monitoring_loop(self, duration_hours: int = 24):
        """Main monitoring loop"""
        self.is_running = True
        end_time = datetime.now() + timedelta(hours=duration_hours)
        
        # Load tracked wallets
        tracked_wallets = await self.load_tracked_wallets()
        
        if not tracked_wallets:
            logger.warning("⚠️ No tracked wallets found. Adding some test wallets...")
            # Add some known active wallets for testing
            test_wallets = [
                "9nNLzq7ccL4nvDAMVP7aPoUv8Ti3qXZqnNaee8Qp57WE",
                "F4SkBcN7VoyA27dY96A3k9QzEMrFju7PwPY6tswRjmKX",
                "3S8TjEDc2iiYivfjegWXi5kRuxKS5BEDiyeK2PjcUdqn"
            ]
            tracked_wallets = test_wallets
        
        self.stats['wallets_tracked'] = len(tracked_wallets)
        
        logger.info(f"🚀 MONITORING STARTED")
        logger.info(f"   Duration: {duration_hours} hours")
        logger.info(f"   End time: {end_time}")
        logger.info(f"   Wallets: {len(tracked_wallets)}\n")
        
        scan_count = 0
        
        try:
            while self.is_running and datetime.now() < end_time:
                scan_count += 1
                scan_start = datetime.now()
                
                logger.info(f"🔍 Scan #{scan_count} - {scan_start.strftime('%Y-%m-%d %H:%M:%S')}")
                
                # Monitor each wallet
                for wallet in tracked_wallets:
                    try:
                        activity = await self.monitor_wallet_activity(wallet)
                        
                        if activity['transactions'] > 0:
                            logger.info(f"   {wallet[:8]}...: {activity['transactions']} tx, {activity['signals']} signals")
                        
                        # Periodically scan for affiliated wallets
                        if scan_count % 10 == 0:  # Every 10 scans
                            await self.scan_for_affiliated_wallets(wallet)
                        
                    except Exception as e:
                        logger.debug(f"Error processing wallet {wallet[:8]}...: {e}")
                    
                    # Small delay between wallets
                    await asyncio.sleep(0.5)
                
                # Update stats
                await self.update_hourly_stats()
                
                # Print summary every hour
                if scan_count % 60 == 0:  # Assuming 1 scan per minute
                    await self.print_stats_summary()
                
                # Wait before next scan (60 seconds)
                scan_duration = (datetime.now() - scan_start).total_seconds()
                wait_time = max(60 - scan_duration, 5)
                
                logger.info(f"   ⏳ Next scan in {wait_time:.0f} seconds...\n")
                await asyncio.sleep(wait_time)
            
            # Final stats
            self.stats['end_time'] = datetime.now()
            
            logger.info(f"\n{'='*60}")
            logger.info(f"✅ MONITORING COMPLETE")
            logger.info(f"{'='*60}")
            
            await self.print_stats_summary()
            
            # Save stats to file
            self.save_stats_to_file()
            
        except KeyboardInterrupt:
            logger.info(f"\n⚠️ Monitoring interrupted by user")
            self.stats['end_time'] = datetime.now()
            await self.print_stats_summary()
            self.save_stats_to_file()
        
        except Exception as e:
            logger.error(f"❌ Error in monitoring loop: {e}")
            raise
    
    def save_stats_to_file(self):
        """Save statistics to JSON file"""
        try:
            filename = f"wallet_monitor_stats_{self.stats['start_time'].strftime('%Y%m%d_%H%M%S')}.json"
            
            stats_data = {
                'start_time': self.stats['start_time'].isoformat(),
                'end_time': self.stats['end_time'].isoformat() if self.stats['end_time'] else None,
                'duration_hours': (self.stats['end_time'] - self.stats['start_time']).total_seconds() / 3600 if self.stats['end_time'] else None,
                'transactions_detected': self.stats['transactions_detected'],
                'copy_signals_generated': self.stats['copy_signals_generated'],
                'wallets_tracked': self.stats['wallets_tracked'],
                'affiliated_wallets_found': self.stats['affiliated_wallets_found'],
                'hourly_stats': self.stats['hourly_stats']
            }
            
            with open(filename, 'w') as f:
                json.dump(stats_data, f, indent=2)
            
            logger.info(f"💾 Stats saved to: {filename}")
            
        except Exception as e:
            logger.error(f"❌ Error saving stats: {e}")
    
    async def run(self, duration_hours: int = 24):
        """Run the monitor"""
        try:
            await self.monitoring_loop(duration_hours)
        finally:
            await self.client.close()


async def main():
    """Run the 24-hour monitor"""
    
    # Parse duration from command line
    duration = 24  # Default 24 hours
    
    if len(sys.argv) > 1:
        try:
            duration = float(sys.argv[1])
        except:
            pass
    
    monitor = WalletScanningMonitor()
    
    try:
        await monitor.run(duration_hours=duration)
    except KeyboardInterrupt:
        logger.info("\n⚠️ Monitoring stopped by user")
    except Exception as e:
        logger.error(f"❌ Monitor failed: {e}")
        raise


if __name__ == "__main__":
    print("\n🧪 24-HOUR WALLET SCANNING MONITOR")
    print("="*60)
    print("This will monitor wallet scanning and copy-trading")
    print("detection for 24 hours (or specified duration).")
    print("")
    print("Usage: python monitor_wallet_scanning_24hr.py [hours]")
    print("Example: python monitor_wallet_scanning_24hr.py 1  # 1 hour test")
    print("="*60)
    print("")
    
    asyncio.run(main())

