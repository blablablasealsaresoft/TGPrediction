"""
🧪 MASTER TEST RUNNER
Runs all comprehensive tests and generates detailed report

TESTS INCLUDED:
1. Auto-sell system (stop-loss, take-profit, trailing stop)
2. Jito bundle execution (MEV protection)
3. Twitter OAuth 2.0 & sentiment analysis
4. Copy trading & social marketplace
5. Honeypot protection (6 layers)
"""

import asyncio
import logging
from datetime import datetime
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler(f'test_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

# Fix Windows console encoding
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')
logger = logging.getLogger(__name__)


async def run_auto_sell_test():
    """Run auto-sell system test"""
    logger.info("\n" + "="*60)
    logger.info("🧪 TEST 1: AUTO-SELL SYSTEM")
    logger.info("="*60)
    
    try:
        from test_auto_sell_system import AutoSellTester
        
        tester = AutoSellTester()
        results = await tester.run_comprehensive_test()
        await tester.client.close()
        
        passed = sum(results.values())
        total = len(results)
        
        return {
            'name': 'Auto-Sell System',
            'passed': passed,
            'total': total,
            'success_rate': (passed / total * 100) if total > 0 else 0,
            'details': results
        }
    except Exception as e:
        logger.error(f"❌ Auto-sell test failed: {e}")
        return {
            'name': 'Auto-Sell System',
            'passed': 0,
            'total': 5,
            'success_rate': 0,
            'error': str(e)
        }


async def run_jito_test():
    """Run Jito bundle execution test"""
    logger.info("\n" + "="*60)
    logger.info("🧪 TEST 2: JITO BUNDLE EXECUTION")
    logger.info("="*60)
    
    try:
        from test_jito_bundles import JitoBundleTester
        
        tester = JitoBundleTester()
        results = await tester.run_comprehensive_test()
        await tester.client.close()
        
        passed = sum(results.values())
        total = len(results)
        
        return {
            'name': 'Jito Bundle Execution',
            'passed': passed,
            'total': total,
            'success_rate': (passed / total * 100) if total > 0 else 0,
            'details': results
        }
    except Exception as e:
        logger.error(f"❌ Jito test failed: {e}")
        return {
            'name': 'Jito Bundle Execution',
            'passed': 0,
            'total': 5,
            'success_rate': 0,
            'error': str(e)
        }


async def run_twitter_test():
    """Run Twitter OAuth 2.0 test"""
    logger.info("\n" + "="*60)
    logger.info("🧪 TEST 3: TWITTER OAUTH 2.0 & SENTIMENT")
    logger.info("="*60)
    
    try:
        from test_twitter_oauth import TwitterOAuthTester
        
        tester = TwitterOAuthTester()
        results = await tester.run_comprehensive_test()
        
        passed = sum(results.values())
        total = len(results)
        
        return {
            'name': 'Twitter OAuth 2.0',
            'passed': passed,
            'total': total,
            'success_rate': (passed / total * 100) if total > 0 else 0,
            'details': results
        }
    except Exception as e:
        logger.error(f"❌ Twitter test failed: {e}")
        return {
            'name': 'Twitter OAuth 2.0',
            'passed': 0,
            'total': 6,
            'success_rate': 0,
            'error': str(e)
        }


async def run_copy_trading_test():
    """Run copy trading test"""
    logger.info("\n" + "="*60)
    logger.info("🧪 TEST 4: COPY TRADING & SOCIAL MARKETPLACE")
    logger.info("="*60)
    
    try:
        from test_copy_trading import CopyTradingTester
        
        tester = CopyTradingTester()
        results = await tester.run_comprehensive_test()
        
        passed = sum(results.values())
        total = len(results)
        
        return {
            'name': 'Copy Trading',
            'passed': passed,
            'total': total,
            'success_rate': (passed / total * 100) if total > 0 else 0,
            'details': results
        }
    except Exception as e:
        logger.error(f"❌ Copy trading test failed: {e}")
        return {
            'name': 'Copy Trading',
            'passed': 0,
            'total': 6,
            'success_rate': 0,
            'error': str(e)
        }


async def run_honeypot_test():
    """Run honeypot protection test"""
    logger.info("\n" + "="*60)
    logger.info("🧪 TEST 5: HONEYPOT PROTECTION (6 LAYERS)")
    logger.info("="*60)
    
    try:
        from test_honeypot_protection import HoneypotProtectionTester
        
        tester = HoneypotProtectionTester()
        results = await tester.run_comprehensive_test()
        await tester.client.close()
        
        passed = sum(results.values())
        total = len(results)
        
        return {
            'name': 'Honeypot Protection',
            'passed': passed,
            'total': total,
            'success_rate': (passed / total * 100) if total > 0 else 0,
            'details': results
        }
    except Exception as e:
        logger.error(f"❌ Honeypot test failed: {e}")
        return {
            'name': 'Honeypot Protection',
            'passed': 0,
            'total': 7,
            'success_rate': 0,
            'error': str(e)
        }


async def generate_report(test_results):
    """Generate comprehensive test report"""
    logger.info("\n" + "="*80)
    logger.info("📊 COMPREHENSIVE TEST REPORT")
    logger.info("="*80)
    logger.info(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    total_tests = 0
    total_passed = 0
    
    # Individual test results
    logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    logger.info("INDIVIDUAL TEST RESULTS:")
    logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
    
    for i, result in enumerate(test_results, 1):
        total_tests += result['total']
        total_passed += result['passed']
        
        status = "✅ PASSED" if result['success_rate'] >= 80 else "⚠️ PARTIAL" if result['success_rate'] >= 50 else "❌ FAILED"
        
        logger.info(f"{i}. {result['name']:30s} {status}")
        logger.info(f"   Tests Passed: {result['passed']}/{result['total']}")
        logger.info(f"   Success Rate: {result['success_rate']:.1f}%")
        
        if 'error' in result:
            logger.info(f"   Error: {result['error']}")
        
        logger.info("")
    
    # Overall summary
    overall_success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
    
    logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    logger.info("OVERALL SUMMARY:")
    logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
    
    logger.info(f"Total Tests Run: {total_tests}")
    logger.info(f"Tests Passed: {total_passed}")
    logger.info(f"Tests Failed: {total_tests - total_passed}")
    logger.info(f"Overall Success Rate: {overall_success_rate:.1f}%\n")
    
    if overall_success_rate >= 90:
        logger.info("🎉 EXCELLENT! All systems operational!")
    elif overall_success_rate >= 70:
        logger.info("✅ GOOD! Most systems working correctly")
    elif overall_success_rate >= 50:
        logger.info("⚠️ FAIR! Some systems need attention")
    else:
        logger.info("❌ POOR! Multiple systems need fixing")
    
    logger.info("\n" + "="*80)
    
    # Feature status
    logger.info("\n📋 FEATURE STATUS:\n")
    
    features = {
        'Twitter Sentiment': test_results[0]['success_rate'] >= 80 if len(test_results) > 0 else False,
        'Copy Trading': test_results[1]['success_rate'] >= 80 if len(test_results) > 1 else False,
        'Honeypot Protection': test_results[2]['success_rate'] >= 80 if len(test_results) > 2 else False,
    }
    
    for feature, working in features.items():
        status = "✅ OPERATIONAL" if working else "⚠️ NEEDS ATTENTION"
        logger.info(f"   {feature:25s}: {status}")
    
    logger.info("\n" + "="*80)
    
    return {
        'total_tests': total_tests,
        'total_passed': total_passed,
        'success_rate': overall_success_rate,
        'test_results': test_results
    }


async def main():
    """Run all tests and generate report"""
    logger.info("\n" + "="*80)
    logger.info("🚀 SOLANA TRADING BOT - COMPREHENSIVE TEST SUITE")
    logger.info("="*80)
    logger.info("Testing all revolutionary features...\n")
    
    # Run all tests
    test_results = []
    
    # Test 1: Auto-sell system
    # Note: This uses real SOL - uncomment to run
    # result = await run_auto_sell_test()
    # test_results.append(result)
    
    # Test 2: Jito bundles
    # Note: This uses real SOL - uncomment to run
    # result = await run_jito_test()
    # test_results.append(result)
    
    # Test 3: Twitter OAuth (safe to run)
    result = await run_twitter_test()
    test_results.append(result)
    
    # Test 4: Copy trading (safe to run)
    result = await run_copy_trading_test()
    test_results.append(result)
    
    # Test 5: Honeypot protection (safe to run)
    result = await run_honeypot_test()
    test_results.append(result)
    
    # Generate comprehensive report
    final_report = await generate_report(test_results)
    
    logger.info("\n✅ All tests complete!")
    logger.info(f"📄 Detailed log saved to test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    
    return final_report


if __name__ == "__main__":
    print("\n🧪 SOLANA TRADING BOT - MASTER TEST SUITE")
    print("="*80)
    print("")
    print("⚠️  IMPORTANT:")
    print("   - Some tests use REAL SOL (auto-sell, Jito)")
    print("   - These are COMMENTED OUT by default")
    print("   - Edit run_all_tests.py to enable them")
    print("")
    print("Safe tests that will run:")
    print("   ✅ Twitter OAuth 2.0 & Sentiment")
    print("   ✅ Copy Trading & Social Marketplace")
    print("   ✅ Honeypot Protection (6 layers)")
    print("")
    print("="*80)
    print("")
    
    response = input("Run tests? (yes/no): ")
    
    if response.lower() == 'yes':
        asyncio.run(main())
    else:
        print("\n❌ Tests cancelled")

