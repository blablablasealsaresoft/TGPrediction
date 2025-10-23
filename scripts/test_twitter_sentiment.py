"""
Test Twitter OAuth 2.0 integration and sentiment analysis
"""
import os
import sys
import asyncio
from pathlib import Path
from dotenv import load_dotenv

# Load environment
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.modules.sentiment_analysis import SocialMediaAggregator

async def test_twitter():
    """Test Twitter OAuth 2.0 credentials"""
    
    print("=" * 70)
    print("🐦 TESTING TWITTER OAUTH 2.0 INTEGRATION")
    print("=" * 70)
    
    # Get credentials from .env
    twitter_api_key = os.getenv('TWITTER_API_KEY')
    twitter_bearer_token = os.getenv('TWITTER_BEARER_TOKEN')
    twitter_client_id = os.getenv('TWITTER_CLIENT_ID')
    twitter_client_secret = os.getenv('TWITTER_CLIENT_SECRET')
    
    print("\n[CREDENTIALS CHECK]")
    print(f"  API Key: {'✅ Present' if twitter_api_key else '❌ Missing'}")
    print(f"  Bearer Token: {'✅ Present' if twitter_bearer_token else '❌ Missing'}")
    print(f"  Client ID: {'✅ Present' if twitter_client_id else '❌ Missing'}")
    print(f"  Client Secret: {'✅ Present' if twitter_client_secret else '❌ Missing'}")
    
    if not twitter_bearer_token:
        print("\n❌ Twitter Bearer Token required for OAuth 2.0")
        print("   Add TWITTER_BEARER_TOKEN to your .env file")
        return
    
    # Initialize sentiment analyzer
    print("\n[INITIALIZING SENTIMENT ANALYZER]")
    try:
        aggregator = SocialMediaAggregator(
            twitter_api_key=twitter_api_key,
            twitter_bearer_token=twitter_bearer_token,
            twitter_client_id=twitter_client_id,
            twitter_client_secret=twitter_client_secret,
            reddit_credentials={
                'client_id': os.getenv('REDDIT_CLIENT_ID'),
                'client_secret': os.getenv('REDDIT_CLIENT_SECRET')
            }
        )
        print("  ✅ Sentiment analyzer initialized")
    except Exception as e:
        print(f"  ❌ Error initializing: {e}")
        return
    
    # Test 1: Analyze popular token (SOL)
    print("\n[TEST 1: SOL Sentiment Analysis]")
    try:
        print("  🔄 Fetching Twitter sentiment for SOL...")
        sentiment = await aggregator.analyze_token_sentiment(
            "So11111111111111111111111111111111111111112",
            "SOL"
        )
        
        print(f"  ✅ Sentiment Score: {sentiment.get('sentiment_score', 0):.1f}/100")
        print(f"  📊 Twitter Mentions: {sentiment.get('twitter', {}).get('mentions', 0)}")
        print(f"  📈 Viral Potential: {sentiment.get('viral_potential', 0):.1%}")
        print(f"  🔥 Trending: {'YES' if sentiment.get('twitter', {}).get('trending', False) else 'No'}")
        
        # Check if we got real data
        twitter_mentions = sentiment.get('twitter', {}).get('mentions', 0)
        if twitter_mentions > 0:
            print("\n  ✅ TWITTER API IS WORKING!")
            print(f"  Found {twitter_mentions} mentions - Real data!")
        else:
            print("\n  ⚠️ No Twitter mentions found")
            print("  This could mean:")
            print("    - API credentials work but SOL has no recent mentions")
            print("    - Or rate limits hit")
            print("    - Or API credentials invalid")
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 2: Detect viral tokens
    print("\n[TEST 2: Viral Token Detection]")
    try:
        print("  🔄 Searching for viral tokens...")
        viral_tokens = await aggregator.detect_viral_tokens(min_score=60)
        
        if viral_tokens:
            print(f"  ✅ Found {len(viral_tokens)} viral tokens:")
            for token in viral_tokens[:5]:
                print(f"     • {token.get('symbol', 'UNKNOWN')}: {token.get('score', 0):.1f} score")
        else:
            print("  📊 No viral tokens detected")
            print("  (This is normal if markets are quiet)")
    
    except Exception as e:
        print(f"  ❌ Error: {e}")
    
    print("\n" + "=" * 70)
    print("✅ TWITTER SENTIMENT TEST COMPLETE")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(test_twitter())

