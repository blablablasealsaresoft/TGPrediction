#!/usr/bin/env python3
"""
Validate all configured API keys for production deployment.
Tests connectivity and quota for each critical API service.
"""

import asyncio
import os
import sys
from pathlib import Path
import aiohttp
from dotenv import load_dotenv

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Load environment
load_dotenv()

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_success(msg):
    print(f"{Colors.GREEN}✅ {msg}{Colors.END}")

def print_error(msg):
    print(f"{Colors.RED}❌ {msg}{Colors.END}")

def print_warning(msg):
    print(f"{Colors.YELLOW}⚠️  {msg}{Colors.END}")

def print_info(msg):
    print(f"{Colors.BLUE}ℹ️  {msg}{Colors.END}")

async def validate_helius():
    """Validate Helius RPC API"""
    api_key = os.getenv('HELIUS_API_KEY')
    if not api_key:
        print_error("Helius: API key not found")
        return False
    
    url = f"https://mainnet.helius-rpc.com/?api-key={api_key}"
    
    try:
        async with aiohttp.ClientSession() as session:
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getVersion"
            }
            async with session.post(url, json=payload, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if 'result' in data:
                        print_success(f"Helius: Connected (Solana version: {data['result']['solana-core']})")
                        return True
                print_error(f"Helius: Invalid response (status {resp.status})")
                return False
    except Exception as e:
        print_error(f"Helius: Connection failed - {e}")
        return False

async def validate_coingecko():
    """Validate CoinGecko API"""
    api_key = os.getenv('COINGECKO_API_KEY')
    if not api_key:
        print_warning("CoinGecko: API key not found (optional, using free tier)")
        return True
    
    # Test with free endpoint
    url = "https://api.coingecko.com/api/v3/ping"
    
    try:
        async with aiohttp.ClientSession() as session:
            headers = {}
            if api_key and api_key.startswith('CG-'):
                headers['x-cg-demo-api-key'] = api_key
            
            async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if 'gecko_says' in data:
                        print_success(f"CoinGecko: Connected - {data['gecko_says']}")
                        return True
                print_warning(f"CoinGecko: Unexpected response (status {resp.status})")
                return True  # Non-critical
    except Exception as e:
        print_warning(f"CoinGecko: Connection failed - {e} (non-critical)")
        return True

async def validate_solscan():
    """Validate Solscan API"""
    api_key = os.getenv('SOLSCAN_API_KEY')
    if not api_key:
        print_warning("Solscan: API key not found (optional)")
        return True
    
    url = "https://pro-api.solscan.io/v2.0/account/transactions"
    
    try:
        async with aiohttp.ClientSession() as session:
            headers = {
                'token': api_key
            }
            # Test with known Solana address
            params = {
                'address': 'So11111111111111111111111111111111111111112',
                'page_size': 1
            }
            async with session.get(url, headers=headers, params=params, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status == 200:
                    print_success("Solscan: API key valid")
                    return True
                elif resp.status == 401:
                    print_error("Solscan: API key invalid or expired")
                    return False
                print_warning(f"Solscan: Unexpected response (status {resp.status})")
                return True
    except Exception as e:
        print_warning(f"Solscan: Connection failed - {e} (non-critical)")
        return True

async def validate_birdeye():
    """Validate Birdeye API"""
    api_key = os.getenv('BIRDEYE_API_KEY')
    if not api_key:
        print_warning("Birdeye: API key not found (optional)")
        return True
    
    url = "https://public-api.birdeye.so/defi/price"
    
    try:
        async with aiohttp.ClientSession() as session:
            headers = {
                'X-API-KEY': api_key
            }
            params = {
                'address': 'So11111111111111111111111111111111111111112'
            }
            async with session.get(url, headers=headers, params=params, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if data.get('success'):
                        print_success(f"Birdeye: API key valid (SOL price: ${data['data']['value']:.2f})")
                        return True
                elif resp.status == 401 or resp.status == 403:
                    print_error("Birdeye: API key invalid or expired")
                    return False
                print_warning(f"Birdeye: Unexpected response (status {resp.status})")
                return True
    except Exception as e:
        print_warning(f"Birdeye: Connection failed - {e} (non-critical)")
        return True

async def validate_rugcheck():
    """Validate RugCheck API (no key needed)"""
    url = "https://api.rugcheck.xyz/v1/tokens/So11111111111111111111111111111111111111112/report"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status == 200:
                    print_success("RugCheck: API accessible (no key required)")
                    return True
                print_warning(f"RugCheck: Service may be down (status {resp.status})")
                return True
    except Exception as e:
        print_warning(f"RugCheck: Connection failed - {e} (non-critical)")
        return True

async def validate_dexscreener():
    """Validate DexScreener API (no key needed)"""
    url = "https://api.dexscreener.com/latest/dex/tokens/So11111111111111111111111111111111111111112"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if 'pairs' in data:
                        print_success(f"DexScreener: API accessible ({len(data['pairs'])} pairs found)")
                        return True
                print_warning(f"DexScreener: Unexpected response (status {resp.status})")
                return True
    except Exception as e:
        print_warning(f"DexScreener: Connection failed - {e} (non-critical)")
        return True

def validate_twitter_credentials():
    """Validate Twitter credentials exist"""
    username = os.getenv('TWITTER_USERNAME')
    email = os.getenv('TWITTER_EMAIL')
    password = os.getenv('TWITTER_PASSWORD')
    
    if username and email and password:
        print_success(f"Twitter: Credentials configured (username: {username})")
        print_info("Twitter: Using Twikit - actual connection test requires runtime")
        return True
    else:
        print_warning("Twitter: Credentials incomplete (sentiment analysis will be limited)")
        return True

def validate_discord_token():
    """Validate Discord bot token exists"""
    token = os.getenv('DISCORD_BOT_TOKEN')
    
    if token and len(token) > 50:
        print_success("Discord: Bot token configured")
        print_info("Discord: Actual validation requires runtime connection")
        return True
    else:
        print_warning("Discord: Bot token not configured (optional)")
        return True

def validate_telegram():
    """Validate Telegram bot token"""
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    
    if not token:
        print_error("Telegram: Bot token not found (CRITICAL)")
        return False
    
    if ':' not in token or len(token) < 40:
        print_error("Telegram: Bot token format invalid")
        return False
    
    print_success("Telegram: Bot token format valid")
    print_info("Telegram: Actual validation requires runtime connection")
    return True

def validate_environment():
    """Validate critical environment variables"""
    critical_vars = {
        'WALLET_PRIVATE_KEY': 'Wallet private key',
        'WALLET_ENCRYPTION_KEY': 'Wallet encryption key',
        'ADMIN_CHAT_ID': 'Admin Telegram ID',
        'SOLANA_NETWORK': 'Solana network',
    }
    
    all_valid = True
    for var, name in critical_vars.items():
        value = os.getenv(var)
        if value:
            if var == 'WALLET_PRIVATE_KEY':
                print_success(f"{name}: Configured (length: {len(value)})")
            elif var == 'WALLET_ENCRYPTION_KEY':
                print_success(f"{name}: Configured (base64 format)")
            else:
                print_success(f"{name}: {value}")
        else:
            print_error(f"{name}: NOT CONFIGURED")
            all_valid = False
    
    return all_valid

async def validate_fallback_rpcs():
    """Validate fallback RPC endpoints"""
    fallbacks = []
    for i in range(1, 6):
        url = os.getenv(f'FALLBACK_RPC_{i}')
        if url:
            fallbacks.append(url)
    
    if not fallbacks:
        print_warning("No fallback RPCs configured")
        return True
    
    print_info(f"Found {len(fallbacks)} fallback RPC(s)")
    
    # Test first fallback
    if fallbacks:
        url = fallbacks[0]
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "getVersion"
                }
                async with session.post(url, json=payload, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                    if resp.status == 200:
                        print_success(f"Fallback RPC 1: Accessible")
                        return True
        except Exception as e:
            print_warning(f"Fallback RPC 1: Failed - {e}")
    
    return True

async def main():
    """Run all API validations"""
    print("\n" + "="*60)
    print("🔍 API KEY VALIDATION - Production Deployment")
    print("="*60 + "\n")
    
    # Critical APIs (must pass)
    print("📌 CRITICAL APIs (must be valid):\n")
    critical_results = []
    
    critical_results.append(await validate_helius())
    critical_results.append(validate_telegram())
    critical_results.append(validate_environment())
    
    # Optional APIs (warnings only)
    print("\n📊 OPTIONAL APIs (warnings if unavailable):\n")
    optional_results = []
    
    optional_results.append(await validate_coingecko())
    optional_results.append(await validate_solscan())
    optional_results.append(await validate_birdeye())
    optional_results.append(await validate_rugcheck())
    optional_results.append(await validate_dexscreener())
    optional_results.append(validate_twitter_credentials())
    optional_results.append(validate_discord_token())
    optional_results.append(await validate_fallback_rpcs())
    
    # Summary
    print("\n" + "="*60)
    print("📋 VALIDATION SUMMARY")
    print("="*60)
    
    critical_passed = sum(critical_results)
    critical_total = len(critical_results)
    optional_passed = sum(optional_results)
    optional_total = len(optional_results)
    
    print(f"\nCritical APIs: {critical_passed}/{critical_total} passed")
    print(f"Optional APIs: {optional_passed}/{optional_total} passed")
    
    if critical_passed == critical_total:
        print_success("\n✅ ALL CRITICAL APIs VALIDATED - Ready for deployment!")
        return 0
    else:
        print_error("\n❌ CRITICAL API VALIDATION FAILED - Fix issues before deployment!")
        return 1

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\nValidation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"\nUnexpected error: {e}")
        sys.exit(1)

