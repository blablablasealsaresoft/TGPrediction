"""
Test Jupiter DEX Integration
Quick test to verify Jupiter API quotes work
"""

import asyncio
import aiohttp
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_jupiter_quote():
    """Test getting a quote from Jupiter"""
    
    # Jupiter API endpoint
    JUPITER_API = "https://quote-api.jup.ag/v6"
    
    # Test: Get quote for swapping 0.1 SOL to USDC
    SOL_MINT = "So11111111111111111111111111111111111111112"
    USDC_MINT = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
    
    amount_lamports = int(0.1 * 1e9)  # 0.1 SOL in lamports
    
    params = {
        "inputMint": SOL_MINT,
        "outputMint": USDC_MINT,
        "amount": str(amount_lamports),
        "slippageBps": 50  # 0.5%
    }
    
    logger.info("🔍 Testing Jupiter API...")
    logger.info(f"   Swapping: 0.1 SOL → USDC")
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{JUPITER_API}/quote",
                params=params
            ) as response:
                
                logger.info(f"   Status Code: {response.status}")
                
                if response.status == 200:
                    data = await response.json()
                    
                    # Extract key info
                    input_amount = int(data.get('inAmount', 0)) / 1e9
                    output_amount = int(data.get('outAmount', 0)) / 1e6  # USDC has 6 decimals
                    price_impact = float(data.get('priceImpactPct', 0))
                    
                    logger.info("✅ Jupiter API Working!")
                    logger.info(f"   Input: {input_amount} SOL")
                    logger.info(f"   Output: ~${output_amount:.2f} USDC")
                    logger.info(f"   Price Impact: {price_impact:.4f}%")
                    logger.info(f"   Routes Found: {len(data.get('routePlan', []))}")
                    
                    return True
                else:
                    error_text = await response.text()
                    logger.error(f"❌ Jupiter API Error: {response.status}")
                    logger.error(f"   Response: {error_text}")
                    return False
                    
    except Exception as e:
        logger.error(f"❌ Exception: {e}")
        return False


async def test_jupiter_price():
    """Test getting price from Jupiter"""
    
    JUPITER_PRICE_API = "https://price.jup.ag/v4"
    
    # Test: Get SOL price
    params = {
        "ids": "So11111111111111111111111111111111111111112"  # SOL
    }
    
    logger.info("\n🔍 Testing Jupiter Price API...")
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{JUPITER_PRICE_API}/price",
                params=params
            ) as response:
                
                if response.status == 200:
                    data = await response.json()
                    sol_data = data.get('data', {}).get('So11111111111111111111111111111111111111112', {})
                    price = sol_data.get('price', 0)
                    
                    logger.info("✅ Jupiter Price API Working!")
                    logger.info(f"   SOL Price: ${price:.2f}")
                    
                    return True
                else:
                    logger.error(f"❌ Price API Error: {response.status}")
                    return False
                    
    except Exception as e:
        logger.error(f"❌ Exception: {e}")
        return False


async def main():
    """Run all tests"""
    logger.info("="*60)
    logger.info("JUPITER DEX INTEGRATION TEST")
    logger.info("="*60)
    
    # Test quote endpoint
    quote_success = await test_jupiter_quote()
    
    # Test price endpoint
    price_success = await test_jupiter_price()
    
    logger.info("\n" + "="*60)
    logger.info("RESULTS:")
    logger.info(f"   Quote API: {'✅ WORKING' if quote_success else '❌ FAILED'}")
    logger.info(f"   Price API: {'✅ WORKING' if price_success else '❌ FAILED'}")
    logger.info("="*60)
    
    if quote_success and price_success:
        logger.info("\n🎉 Jupiter Integration is FULLY FUNCTIONAL!")
        logger.info("   Ready for real trading!")
    else:
        logger.info("\n⚠️  Some tests failed. Check logs above.")


if __name__ == "__main__":
    asyncio.run(main())

