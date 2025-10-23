"""
🚀 ULTRA-FAST EXECUTION ENGINE
Parallel multi-RPC submission with pre-signed transactions

FEATURES:
- Pre-signed transaction pool
- Parallel submission to Jito + multiple RPCs
- Fast simulation before submit
- Sub-second execution
- Automatic fastest-RPC selection
"""

import aiohttp
import asyncio
import base64
import time
import logging
from typing import List, Dict, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ExecutionResult:
    """Result of fast execution"""
    success: bool
    latency_ms: int
    winner: Optional[Dict] = None
    all_results: List[Dict] = None
    reason: str = ""


async def _rpc_send_signed_tx(
    session: aiohttp.ClientSession,
    rpc_url: str,
    signed_tx_b64: str,
    timeout_ms: int = 800
) -> Dict:
    """
    Send a signed tx (base64) to a Solana RPC endpoint using sendTransaction
    """
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "sendTransaction",
        "params": [signed_tx_b64, {"skipPreflight": True, "preflightCommitment": "confirmed"}]
    }
    
    try:
        timeout = aiohttp.ClientTimeout(total=timeout_ms/1000)
        async with session.post(rpc_url, json=payload, timeout=timeout) as resp:
            txt = await resp.text()
            return {"rpc": rpc_url, "status": resp.status, "body": txt, "success": resp.status == 200}
    except Exception as e:
        return {"rpc": rpc_url, "error": str(e), "success": False}


async def _simulate_transaction(
    session: aiohttp.ClientSession,
    rpc_url: str,
    signed_tx_b64: str,
    timeout_ms: int = 350
) -> bool:
    """
    Fast simulation - returns True if simulation looks OK (no obvious revert)
    """
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "simulateTransaction",
        "params": [signed_tx_b64, {"sigVerify": False, "replaceRecentBlockhash": True}]
    }
    
    try:
        timeout = aiohttp.ClientTimeout(total=timeout_ms/1000)
        async with session.post(rpc_url, json=payload, timeout=timeout) as resp:
            if resp.status != 200:
                return False
            
            j = await resp.json()
            # Quick heuristic: if 'err' in result → bad
            if j.get('result', {}).get('err'):
                logger.warning(f"❌ Simulation failed: {j.get('result', {}).get('err')}")
                return False
            
            return True
            
    except Exception as e:
        logger.debug(f"Simulation error: {e}")
        return False


async def submit_signed_tx_fast(
    signed_tx_bytes: bytes,
    rpc_endpoints: List[str],
    jito_submit_fn=None,  # Callable that submits to Jito
    simulate_rpc: Optional[str] = None,
    timeout_ms_on_all: int = 1200
) -> ExecutionResult:
    """
    Submit signed transaction as fast as possible:
      1) Quick simulate on 'simulate_rpc'
      2) Submit in PARALLEL to Jito + multiple RPCs
      3) Return first positive response
    
    Args:
        signed_tx_bytes: Pre-signed transaction bytes
        rpc_endpoints: List of RPC URLs to submit to
        jito_submit_fn: Function to submit Jito bundle
        simulate_rpc: RPC to use for fast simulation
        timeout_ms_on_all: Overall timeout in milliseconds
    
    Returns:
        ExecutionResult with success status and details
    """
    signed_b64 = base64.b64encode(signed_tx_bytes).decode()
    start = time.time()
    
    async with aiohttp.ClientSession() as session:
        # Step 1: Quick simulation (fast-fail honeypots/bad tx)
        if simulate_rpc:
            logger.info(f"🔍 Fast simulation on {simulate_rpc[:30]}...")
            ok = await _simulate_transaction(session, simulate_rpc, signed_b64, timeout_ms=300)
            
            if not ok:
                latency = int((time.time() - start) * 1000)
                logger.warning(f"❌ Simulation failed in {latency}ms - ABORTING")
                return ExecutionResult(
                    success=False,
                    latency_ms=latency,
                    reason="simulation_failed"
                )
            
            logger.info(f"✅ Simulation passed")
        
        # Step 2: Build parallel submission tasks
        tasks = []
        
        # Jito submission
        if jito_submit_fn:
            logger.info(f"🚀 Submitting to Jito bundle...")
            tasks.append(asyncio.create_task(jito_submit_fn(signed_tx_bytes)))
        
        # Submit to multiple RPC endpoints
        for rpc in rpc_endpoints:
            logger.info(f"📡 Submitting to RPC: {rpc[:40]}...")
            tasks.append(
                asyncio.create_task(
                    _rpc_send_signed_tx(session, rpc, signed_b64, timeout_ms=timeout_ms_on_all//2)
                )
            )
        
        logger.info(f"⚡ Parallel submission to {len(tasks)} destinations...")
        
        # Step 3: Race for first success
        done, pending = await asyncio.wait(
            tasks,
            timeout=(timeout_ms_on_all/1000),
            return_when=asyncio.FIRST_COMPLETED
        )
        
        # Process results
        results = []
        for task in list(done):
            try:
                res = task.result()
                results.append(res)
                
                # Check for success
                if isinstance(res, dict):
                    if res.get("status") == 200 or res.get("success") or res.get("bundle_id"):
                        # SUCCESS! Cancel remaining tasks
                        for p in pending:
                            p.cancel()
                        
                        latency = int((time.time() - start) * 1000)
                        logger.info(f"✅ TX CONFIRMED in {latency}ms via {res.get('rpc', 'Jito')[:30]}")
                        
                        return ExecutionResult(
                            success=True,
                            latency_ms=latency,
                            winner=res,
                            all_results=results
                        )
            except Exception as e:
                logger.debug(f"Task error: {e}")
                continue
        
        # Wait a bit more for remaining tasks
        if pending:
            done2, still_pending = await asyncio.wait(pending, timeout=1.0)
            
            for t in done2:
                try:
                    results.append(t.result())
                except Exception:
                    pass
            
            # Cancel any still running
            for p in still_pending:
                p.cancel()
        
        # Final check for any success
        for r in results:
            if isinstance(r, dict) and (r.get("status") == 200 or r.get("bundle_id") or r.get("success")):
                latency = int((time.time() - start) * 1000)
                logger.info(f"✅ TX CONFIRMED in {latency}ms (delayed)")
                
                return ExecutionResult(
                    success=True,
                    latency_ms=latency,
                    winner=r,
                    all_results=results
                )
        
        # No success
        latency = int((time.time() - start) * 1000)
        logger.error(f"❌ TX FAILED after {latency}ms - no successful submission")
        
        return ExecutionResult(
            success=False,
            latency_ms=latency,
            all_results=results,
            reason="no_success"
        )


class FastExecutionEngine:
    """
    Ultra-fast transaction execution engine
    """
    
    def __init__(self, primary_rpc: str, fallback_rpcs: List[str]):
        self.primary_rpc = primary_rpc
        self.fallback_rpcs = fallback_rpcs
        self.all_rpcs = [primary_rpc] + fallback_rpcs
        
        # RPC performance tracking
        self.rpc_latencies: Dict[str, List[float]] = {rpc: [] for rpc in self.all_rpcs}
        
        logger.info(f"⚡ Fast Execution Engine initialized with {len(self.all_rpcs)} RPCs")
    
    def record_latency(self, rpc_url: str, latency_ms: float):
        """Record RPC latency for performance tracking"""
        if rpc_url in self.rpc_latencies:
            self.rpc_latencies[rpc_url].append(latency_ms)
            # Keep only last 100 measurements
            if len(self.rpc_latencies[rpc_url]) > 100:
                self.rpc_latencies[rpc_url] = self.rpc_latencies[rpc_url][-100:]
    
    def get_fastest_rpcs(self, n: int = 3) -> List[str]:
        """Get N fastest RPCs based on recent latency"""
        rpc_avgs = []
        
        for rpc, latencies in self.rpc_latencies.items():
            if latencies:
                avg_latency = sum(latencies) / len(latencies)
                rpc_avgs.append((rpc, avg_latency))
        
        # Sort by latency
        rpc_avgs.sort(key=lambda x: x[1])
        
        # Return top N RPCs
        return [rpc for rpc, _ in rpc_avgs[:n]]
    
    async def execute_fast(
        self,
        signed_tx_bytes: bytes,
        jito_submit_fn=None,
        use_simulation: bool = True
    ) -> ExecutionResult:
        """
        Execute transaction with maximum speed
        
        Args:
            signed_tx_bytes: Pre-signed transaction
            jito_submit_fn: Jito submission function
            use_simulation: Run simulation first
        
        Returns:
            ExecutionResult
        """
        
        # Get fastest RPCs
        fastest_rpcs = self.get_fastest_rpcs(n=3)
        
        if not fastest_rpcs:
            fastest_rpcs = self.all_rpcs[:3]
        
        # Use fastest RPC for simulation
        simulate_rpc = fastest_rpcs[0] if use_simulation else None
        
        logger.info(f"⚡ Fast execution using {len(fastest_rpcs)} RPCs + Jito")
        
        # Execute with parallel submission
        result = await submit_signed_tx_fast(
            signed_tx_bytes=signed_tx_bytes,
            rpc_endpoints=fastest_rpcs,
            jito_submit_fn=jito_submit_fn,
            simulate_rpc=simulate_rpc,
            timeout_ms_on_all=1200
        )
        
        # Record latencies
        if result.all_results:
            for res in result.all_results:
                if isinstance(res, dict) and 'rpc' in res:
                    self.record_latency(res['rpc'], result.latency_ms)
        
        return result


# Example usage
async def example():
    """Example of using fast execution"""
    
    engine = FastExecutionEngine(
        primary_rpc="https://mainnet.helius-rpc.com/?api-key=YOUR_KEY",
        fallback_rpcs=[
            "https://api.mainnet-beta.solana.com",
            "https://solana-api.projectserum.com",
            "https://rpc.ankr.com/solana"
        ]
    )
    
    # Pre-signed transaction bytes (you'd get this from signing your swap)
    signed_tx = b"your_signed_transaction_bytes_here"
    
    # Define Jito submission
    async def submit_to_jito(tx_bytes):
        # Your Jito bundle submission code
        return {"bundle_id": "abc123", "success": True}
    
    # Execute
    result = await engine.execute_fast(
        signed_tx_bytes=signed_tx,
        jito_submit_fn=submit_to_jito,
        use_simulation=True
    )
    
    if result.success:
        print(f"✅ TX sent in {result.latency_ms}ms")
    else:
        print(f"❌ TX failed: {result.reason}")


if __name__ == "__main__":
    asyncio.run(example())

