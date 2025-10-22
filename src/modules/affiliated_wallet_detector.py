"""
🔗 AFFILIATED WALLET DETECTOR
Detects side wallets and related addresses using FREE public Solana RPC

Uses standard Solana RPC methods (completely free):
- getSignaturesForAddress
- getTransaction
- Pattern analysis
"""

import asyncio
import logging
from typing import Dict, List, Set, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
from solana.rpc.async_api import AsyncClient
from solders.pubkey import Pubkey

logger = logging.getLogger(__name__)


class AffiliatedWalletDetector:
    """
    Detects affiliated/side wallets using FREE public RPC
    
    Detection Methods:
    1. Fund Transfer Analysis - Wallets that frequently receive SOL from tracked wallet
    2. Simultaneous Trading - Wallets that trade same tokens within short time windows
    3. Common Token Holdings - Wallets holding similar token portfolios
    """
    
    def __init__(self, rpc_client: AsyncClient):
        self.client = rpc_client
        self.affiliation_cache: Dict[str, List[Tuple[str, float]]] = {}  # wallet -> [(affiliated, confidence)]
    
    async def find_affiliated_wallets(
        self,
        main_wallet: str,
        lookback_hours: int = 24,
        min_confidence: float = 0.6
    ) -> List[Tuple[str, float, str]]:
        """
        Find wallets affiliated with the main wallet
        
        Args:
            main_wallet: The wallet address to analyze
            lookback_hours: How far back to analyze (default 24h)
            min_confidence: Minimum confidence score (0-1)
        
        Returns:
            List of (wallet_address, confidence_score, reason) tuples
        """
        
        logger.info(f"🔍 Analyzing {main_wallet[:8]}... for affiliated wallets...")
        
        affiliated_wallets = {}  # address -> (confidence, reasons)
        
        try:
            # Method 1: Find wallets that receive frequent transfers
            transfer_targets = await self._find_transfer_targets(main_wallet, lookback_hours)
            for address, confidence in transfer_targets.items():
                if address not in affiliated_wallets:
                    affiliated_wallets[address] = [confidence, []]
                else:
                    affiliated_wallets[address][0] += confidence
                affiliated_wallets[address][1].append("Frequent recipient of funds")
            
            # Method 2: Find wallets that trade simultaneously
            concurrent_traders = await self._find_concurrent_traders(main_wallet, lookback_hours)
            for address, confidence in concurrent_traders.items():
                if address not in affiliated_wallets:
                    affiliated_wallets[address] = [confidence, []]
                else:
                    affiliated_wallets[address][0] += confidence
                affiliated_wallets[address][1].append("Trades same tokens simultaneously")
            
            # Filter by minimum confidence
            results = [
                (addr, conf, ", ".join(reasons))
                for addr, (conf, reasons) in affiliated_wallets.items()
                if conf >= min_confidence
            ]
            
            # Sort by confidence
            results.sort(key=lambda x: x[1], reverse=True)
            
            logger.info(f"✅ Found {len(results)} affiliated wallets (confidence ≥ {min_confidence:.0%})")
            
            return results[:10]  # Return top 10
            
        except Exception as e:
            logger.error(f"Error finding affiliated wallets: {e}")
            return []
    
    async def _find_transfer_targets(
        self,
        main_wallet: str,
        lookback_hours: int
    ) -> Dict[str, float]:
        """
        Find wallets that frequently receive SOL transfers from main wallet
        Uses: getSignaturesForAddress (FREE!)
        """
        
        transfer_targets = defaultdict(int)  # address -> transfer_count
        
        try:
            pubkey = Pubkey.from_string(main_wallet)
            
            # Get recent transaction signatures (FREE method!)
            # Use smaller limit to avoid rate limiting
            sigs_response = await self.client.get_signatures_for_address(
                pubkey,
                limit=20  # Reduced to avoid rate limits
            )
            
            signatures = sigs_response.value
            logger.info(f"  Found {len(signatures)} recent transactions")
            
            # Analyze each transaction with rate limiting
            checked = 0
            for sig_info in signatures[:15]:  # Check only 15 to avoid rate limits
                try:
                    # Add delay before EACH request to avoid rate limit
                    await asyncio.sleep(0.3)  # 300ms delay = ~3 requests/sec (safe!)
                    
                    # Get full transaction
                    tx_response = await self.client.get_transaction(
                        sig_info.signature,
                        max_supported_transaction_version=0
                    )
                    
                    if not tx_response.value:
                        continue
                    
                    tx = tx_response.value
                    
                    # Parse transaction for SOL transfers
                    # Look at post balances vs pre balances
                    if hasattr(tx.transaction, 'message') and hasattr(tx.transaction.message, 'account_keys'):
                        accounts = tx.transaction.message.account_keys
                        pre_balances = tx.meta.pre_balances if hasattr(tx.meta, 'pre_balances') else []
                        post_balances = tx.meta.post_balances if hasattr(tx.meta, 'post_balances') else []
                        
                        # Find accounts that received SOL
                        for i, account in enumerate(accounts):
                            if i < len(pre_balances) and i < len(post_balances):
                                balance_change = post_balances[i] - pre_balances[i]
                                
                                # If received SOL and not the main wallet
                                if balance_change > 0 and str(account) != main_wallet:
                                    transfer_targets[str(account)] += 1
                                    logger.debug(f"    Found transfer to: {str(account)[:8]}...")
                    
                    checked += 1
                
                except Exception as e:
                    logger.debug(f"Error parsing transaction: {e}")
                    await asyncio.sleep(1)  # Longer delay on error
                    continue
            
            # Calculate confidence based on transfer frequency
            results = {}
            for address, count in transfer_targets.items():
                # Confidence = (transfer_count / total_checked) * weight
                confidence = min((count / max(checked, 1)) * 0.7, 0.7)  # Max 0.7
                if confidence > 0.2:  # At least 20% confidence
                    results[address] = confidence
            
            logger.info(f"  Found {len(results)} potential side wallets from transfers")
            return results
            
        except Exception as e:
            import traceback
            logger.error(f"Error analyzing transfers: {e}")
            logger.error(traceback.format_exc())
            return {}
    
    async def _find_concurrent_traders(
        self,
        main_wallet: str,
        lookback_hours: int
    ) -> Dict[str, float]:
        """
        Find wallets that trade the same tokens around the same time
        This indicates coordinated trading or same owner
        """
        
        # This is more complex and requires parsing swap transactions
        # For now, return empty - can be enhanced later
        
        logger.debug(f"  Concurrent trader detection (advanced feature)")
        return {}
    
    async def auto_discover_and_track(
        self,
        main_wallets: List[str],
        db_manager,
        user_id: int,
        max_to_add: int = 5
    ):
        """
        Automatically discover and add affiliated wallets to database
        
        Args:
            main_wallets: List of primary wallets to analyze
            db_manager: Database manager for adding wallets
            user_id: User ID for tracking
            max_to_add: Maximum affiliated wallets to add per main wallet
        """
        
        logger.info(f"🔎 Auto-discovering affiliated wallets for {len(main_wallets)} main wallets...")
        
        all_affiliated = []
        
        for main_wallet in main_wallets:
            affiliated = await self.find_affiliated_wallets(
                main_wallet,
                lookback_hours=48,  # Last 2 days
                min_confidence=0.4  # Lower threshold for auto-add
            )
            
            for address, confidence, reason in affiliated[:max_to_add]:
                all_affiliated.append((address, confidence, reason, main_wallet))
        
        # Add to database
        added_count = 0
        for address, confidence, reason, source_wallet in all_affiliated:
            try:
                wallet_data = {
                    'user_id': user_id,
                    'wallet_address': address,
                    'label': f"Side wallet of {source_wallet[:8]}...",
                    'score': confidence * 100,  # Convert to 0-100
                    'total_trades': 0,
                    'profitable_trades': 0,
                    'win_rate': 0.0,
                    'total_pnl': 0.0,
                    'copy_enabled': True,
                    'copy_amount_sol': 0.1,
                    'added_at': datetime.utcnow(),
                    'last_checked': datetime.utcnow()
                }
                
                await db_manager.add_tracked_wallet(wallet_data)
                
                logger.info(f"✅ Auto-added affiliated wallet: {address[:8]}... (confidence: {confidence:.0%})")
                logger.info(f"   Reason: {reason}")
                logger.info(f"   Source: {source_wallet[:8]}...")
                
                added_count += 1
                
            except Exception as e:
                # Might already exist
                logger.debug(f"Skipped {address[:8]}...: {e}")
        
        logger.info(f"🎯 Auto-discovery complete! Added {added_count} affiliated wallets")
        return added_count

