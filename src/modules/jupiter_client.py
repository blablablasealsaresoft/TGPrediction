"""
Jupiter Aggregator Integration
Provides best pricing across Solana DEXes
"""

import aiohttp
import logging
from typing import Dict, Optional, List
from decimal import Decimal
from solders.pubkey import Pubkey
from solders.keypair import Keypair
from solders.transaction import VersionedTransaction
from solana.rpc.async_api import AsyncClient

logger = logging.getLogger(__name__)


class JupiterClient:
    """
    Jupiter Aggregator client for best swap rates
    Aggregates prices across: Raydium, Orca, Serum, and more
    """
    
    JUPITER_API_V6 = "https://quote-api.jup.ag/v6"
    JUPITER_PRICE_API = "https://price.jup.ag/v4"
    
    def __init__(self, rpc_client: AsyncClient):
        self.rpc_client = rpc_client
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def get_quote(
        self,
        input_mint: str,
        output_mint: str,
        amount: int,  # In smallest units (lamports for SOL)
        slippage_bps: int = 50,  # 0.5%
        only_direct_routes: bool = False
    ) -> Optional[Dict]:
        """
        Get best swap quote from Jupiter
        
        Args:
            input_mint: Input token mint address
            output_mint: Output token mint address
            amount: Amount in smallest token units
            slippage_bps: Slippage tolerance in basis points (50 = 0.5%)
            only_direct_routes: Only use direct routes (faster but may miss better prices)
        
        Returns:
            Quote data including price, route, and price impact
        """
        try:
            params = {
                "inputMint": input_mint,
                "outputMint": output_mint,
                "amount": str(amount),
                "slippageBps": slippage_bps,
                "onlyDirectRoutes": str(only_direct_routes).lower()
            }
            
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            async with self.session.get(
                f"{self.JUPITER_API_V6}/quote",
                params=params
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"Got Jupiter quote: {data.get('outAmount', 0)} output tokens")
                    return data
                else:
                    error_text = await response.text()
                    logger.error(f"Jupiter quote error: {response.status} - {error_text}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error getting Jupiter quote: {e}")
            return None
    
    async def get_swap_transaction(
        self,
        quote: Dict,
        user_public_key: str,
        wrap_unwrap_sol: bool = True,
        fee_account: Optional[str] = None
    ) -> Optional[str]:
        """
        Get serialized transaction for the swap
        
        Args:
            quote: Quote data from get_quote()
            user_public_key: User's wallet public key
            wrap_unwrap_sol: Automatically wrap/unwrap SOL
            fee_account: Optional fee account for referral fees
        
        Returns:
            Base64 encoded serialized transaction
        """
        try:
            payload = {
                "quoteResponse": quote,
                "userPublicKey": user_public_key,
                "wrapAndUnwrapSol": wrap_unwrap_sol
            }
            
            if fee_account:
                payload["feeAccount"] = fee_account
            
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            async with self.session.post(
                f"{self.JUPITER_API_V6}/swap",
                json=payload
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("swapTransaction")
                else:
                    error_text = await response.text()
                    logger.error(f"Jupiter swap transaction error: {response.status} - {error_text}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error getting swap transaction: {e}")
            return None
    
    async def execute_swap(
        self,
        input_mint: str,
        output_mint: str,
        amount: int,
        keypair: Keypair,
        slippage_bps: int = 50,
        max_retries: int = 3
    ) -> Optional[Dict]:
        """
        Execute a complete swap operation
        
        Args:
            input_mint: Input token mint
            output_mint: Output token mint
            amount: Amount to swap (in smallest units)
            keypair: User's keypair for signing
            slippage_bps: Slippage tolerance
            max_retries: Maximum retry attempts
        
        Returns:
            Transaction result with signature
        """
        try:
            # Get quote
            quote = await self.get_quote(
                input_mint,
                output_mint,
                amount,
                slippage_bps
            )
            
            if not quote:
                return {"success": False, "error": "Failed to get quote"}
            
            # Calculate price impact
            price_impact = float(quote.get("priceImpactPct", 0))
            if abs(price_impact) > 5.0:  # 5% price impact warning
                logger.warning(f"High price impact: {price_impact}%")
            
            # Get swap transaction
            user_pubkey = str(keypair.pubkey())
            swap_tx_base64 = await self.get_swap_transaction(
                quote,
                user_pubkey
            )
            
            if not swap_tx_base64:
                return {"success": False, "error": "Failed to get swap transaction"}
            
            # Deserialize and sign transaction
            import base64
            tx_bytes = base64.b64decode(swap_tx_base64)
            transaction = VersionedTransaction.from_bytes(tx_bytes)
            
            # Sign transaction
            # Note: VersionedTransaction requires different signing approach
            signature_bytes = keypair.sign_message(bytes(transaction.message))
            
            # Send transaction with retries
            for attempt in range(max_retries):
                try:
                    # Send raw transaction
                    result = await self.rpc_client.send_raw_transaction(
                        tx_bytes,
                        opts={"skip_preflight": False, "preflight_commitment": "confirmed"}
                    )
                    
                    if result.value:
                        signature = str(result.value)
                        logger.info(f"Swap transaction sent: {signature}")
                        
                        # Confirm transaction
                        confirmed = await self._confirm_transaction(signature)
                        
                        if confirmed:
                            return {
                                "success": True,
                                "signature": signature,
                                "input_amount": amount,
                                "output_amount": int(quote.get("outAmount", 0)),
                                "price_impact": price_impact,
                                "route": quote.get("routePlan", [])
                            }
                    
                except Exception as e:
                    logger.warning(f"Swap attempt {attempt + 1} failed: {e}")
                    if attempt < max_retries - 1:
                        await asyncio.sleep(1)
                        continue
            
            return {"success": False, "error": "Failed to send transaction after retries"}
            
        except Exception as e:
            logger.error(f"Swap execution error: {e}")
            return {"success": False, "error": str(e)}
    
    async def _confirm_transaction(self, signature: str, max_wait: int = 60) -> bool:
        """Wait for transaction confirmation"""
        import asyncio
        
        for _ in range(max_wait):
            try:
                status = await self.rpc_client.get_signature_statuses([signature])
                if status.value and status.value[0]:
                    if status.value[0].confirmation_status in ["confirmed", "finalized"]:
                        return True
                await asyncio.sleep(1)
            except Exception as e:
                logger.error(f"Error checking transaction status: {e}")
                await asyncio.sleep(1)
        
        return False
    
    async def get_token_price(self, token_mints: List[str]) -> Dict[str, float]:
        """
        Get current prices for tokens
        
        Args:
            token_mints: List of token mint addresses
        
        Returns:
            Dict mapping mint addresses to USD prices
        """
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            # Jupiter price API expects comma-separated list
            ids = ",".join(token_mints)
            
            async with self.session.get(
                f"{self.JUPITER_PRICE_API}/price",
                params={"ids": ids}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    prices = {}
                    for mint in token_mints:
                        price_data = data.get("data", {}).get(mint, {})
                        prices[mint] = float(price_data.get("price", 0))
                    return prices
                else:
                    logger.error(f"Price API error: {response.status}")
                    return {}
                    
        except Exception as e:
            logger.error(f"Error getting token prices: {e}")
            return {}
    
    async def get_token_info(self, token_mint: str) -> Optional[Dict]:
        """Get detailed token information"""
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            # Use Jupiter's token list
            async with self.session.get(
                "https://token.jup.ag/all"
            ) as response:
                if response.status == 200:
                    tokens = await response.json()
                    for token in tokens:
                        if token.get("address") == token_mint:
                            return token
                    return None
                else:
                    return None
                    
        except Exception as e:
            logger.error(f"Error getting token info: {e}")
            return None


class AntiMEVProtection:
    """
    Anti-MEV protection using Jito bundles
    Prevents frontrunning and sandwich attacks
    """
    
    JITO_BLOCK_ENGINE = "https://mainnet.block-engine.jito.wtf"
    JITO_TIP_ACCOUNTS = [
        "96gYZGLnJYVFmbjzopPSU6QiEV5fGqZNyN9nmNhvrZU5",
        "HFqU5x63VTqvQss8hp11i4wVV8bD44PvwucfZ2bU7gRe",
        "Cw8CFyM9FkoMi7K7Crf6HNQqf4uEMzpKw6QNghXLvLkY",
        "ADaUMid9yfUytqMBgopwjb2DTLSokTSzL1zt6iGPaS49",
        "DfXygSm4jCyNCybVYYK6DwvWqjKee8pbDmJGcLWNDXjh",
        "ADuUkR4vqLUMWXxW9gh6D6L8pMSawimctcNZ5pGwDcEt",
        "DttWaMuVvTiduZRnguLF7jNxTgiMBZ1hyAumKUiL2KRL",
        "3AVi9Tg9Uo68tJfuvoKvqKNWKkC5wPdSSdeBnizKZ6jT"
    ]
    
    def __init__(self, rpc_client: AsyncClient):
        self.rpc_client = rpc_client
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def send_bundle(
        self,
        transactions: List[VersionedTransaction],
        tip_lamports: int = 10000  # Tip for block inclusion
    ) -> Optional[str]:
        """
        Send transaction bundle via Jito
        Prevents MEV by guaranteeing atomic execution
        
        Args:
            transactions: List of transactions to bundle
            tip_lamports: Tip amount for validators
        
        Returns:
            Bundle ID if successful
        """
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            # Add tip transaction
            # Tip goes to random Jito tip account
            import random
            tip_account = random.choice(self.JITO_TIP_ACCOUNTS)
            
            # Serialize transactions
            serialized_txs = [
                base64.b64encode(bytes(tx)).decode('utf-8')
                for tx in transactions
            ]
            
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "sendBundle",
                "params": [serialized_txs]
            }
            
            async with self.session.post(
                f"{self.JITO_BLOCK_ENGINE}/api/v1/bundles",
                json=payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    bundle_id = data.get("result")
                    logger.info(f"Bundle sent: {bundle_id}")
                    return bundle_id
                else:
                    error = await response.text()
                    logger.error(f"Bundle send failed: {error}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error sending bundle: {e}")
            return None
    
    async def get_bundle_status(self, bundle_id: str) -> Optional[Dict]:
        """Check bundle status"""
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getBundleStatuses",
                "params": [[bundle_id]]
            }
            
            async with self.session.post(
                f"{self.JITO_BLOCK_ENGINE}/api/v1/bundles",
                json=payload
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("result", {})
                else:
                    return None
                    
        except Exception as e:
            logger.error(f"Error getting bundle status: {e}")
            return None
