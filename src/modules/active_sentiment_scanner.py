"""
ACTIVE SENTIMENT SCANNER
Actively scans Twitter/Reddit/Discord for trending Solana tokens

This PROACTIVELY finds viral tokens BEFORE they pump
Uses your Twitter/Reddit/Discord APIs to scan in real-time
"""

import asyncio
import logging
import aiohttp
import re
from typing import Dict, List, Optional, Set
from datetime import datetime, timedelta
from collections import Counter, defaultdict

logger = logging.getLogger(__name__)


class ActiveSentimentScanner:
    """
    Actively scans social media for trending Solana tokens
    Unlike passive analyzers, this FINDS tokens going viral
    """
    
    def __init__(
        self,
        twitter_bearer_token: Optional[str] = None,
        reddit_client_id: Optional[str] = None,
        reddit_client_secret: Optional[str] = None,
    ):
        self.twitter_bearer = twitter_bearer_token
        self.reddit_id = reddit_client_id
        self.reddit_secret = reddit_client_secret
        
        # Cache of trending tokens
        self.trending_cache: Dict[str, Dict] = {}
        self.last_scan = None
        
        # Solana-specific search terms
        self.search_terms = [
            "#Solana",
            "#SOL",
            "$SOL",
            "pump.fun",
            "raydium",
            "jupiter swap",
            "solana dex",
        ]
        
        # Regex to extract Solana addresses from text
        self.solana_address_pattern = re.compile(r'\b([1-9A-HJ-NP-Za-km-z]{32,44})\b')
        
        logger.info(f"🔍 Active Sentiment Scanner initialized")
        logger.info(f"   Twitter: {'✅ ENABLED' if twitter_bearer_token else '❌ disabled'}")
        logger.info(f"   Reddit: {'✅ ENABLED' if reddit_client_id else '❌ disabled'}")
    
    def has_apis_configured(self) -> bool:
        """Check if ANY APIs are configured"""
        return bool(self.twitter_bearer or (self.reddit_id and self.reddit_secret))
    
    async def scan_for_trending_tokens(self) -> List[Dict]:
        """
        ACTIVELY scan Twitter/Reddit for trending Solana tokens
        
        Returns list of tokens sorted by viral score
        """
        if not self.has_apis_configured():
            logger.warning("No social media APIs configured - cannot scan for trending tokens")
            return []
        
        # Check cache (don't scan more than every 5 minutes)
        if self.last_scan and (datetime.utcnow() - self.last_scan).seconds < 300:
            return self._get_cached_trending()
        
        logger.info("🔍 Actively scanning social media for viral Solana tokens...")
        
        # Scan all sources in parallel
        tasks = []
        if self.twitter_bearer:
            tasks.append(self._scan_twitter())
        if self.reddit_id and self.reddit_secret:
            tasks.append(self._scan_reddit())
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Aggregate findings
        token_mentions = defaultdict(lambda: {
            'address': '',
            'mentions': 0,
            'sentiment_score': 0,
            'sources': [],
            'viral_velocity': 0,
            'first_seen': datetime.utcnow()
        })
        
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Scanner error: {result}")
                continue
            
            if not result:
                continue
            
            for token_addr, data in result.items():
                token_mentions[token_addr]['address'] = token_addr
                token_mentions[token_addr]['mentions'] += data.get('mentions', 0)
                token_mentions[token_addr]['sentiment_score'] += data.get('sentiment', 50)
                token_mentions[token_addr]['sources'].append(data.get('source', 'unknown'))
        
        # Calculate viral scores
        trending_tokens = []
        for addr, data in token_mentions.items():
            if data['mentions'] < 3:  # Filter noise
                continue
            
            # Average sentiment across sources
            num_sources = len(data['sources'])
            avg_sentiment = data['sentiment_score'] / num_sources if num_sources > 0 else 50
            
            # Viral score = mentions * sentiment * source diversity
            viral_score = data['mentions'] * (avg_sentiment / 50) * num_sources
            
            trending_tokens.append({
                'token_address': addr,
                'mentions': data['mentions'],
                'sentiment_score': avg_sentiment,
                'sources': data['sources'],
                'viral_score': viral_score,
                'viral_potential': min(viral_score / 100, 1.0),
                'discovered_at': datetime.utcnow().isoformat()
            })
        
        # Sort by viral score
        trending_tokens.sort(key=lambda x: x['viral_score'], reverse=True)
        
        # Update cache
        self.trending_cache = {t['token_address']: t for t in trending_tokens}
        self.last_scan = datetime.utcnow()
        
        logger.info(f"🔍 Found {len(trending_tokens)} trending Solana tokens")
        
        return trending_tokens
    
    async def _scan_twitter(self) -> Dict[str, Dict]:
        """
        Scan Twitter for Solana token mentions
        Uses Twitter API v2 with bearer token
        """
        if not self.twitter_bearer:
            return {}
        
        logger.info("🐦 Scanning Twitter for Solana tokens...")
        
        found_tokens = {}
        
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    'Authorization': f'Bearer {self.twitter_bearer}',
                    'User-Agent': 'Elite-Trading-Bot/1.0'
                }
                
                # Search recent tweets about Solana
                for term in self.search_terms[:3]:  # Limit to avoid rate limits
                    url = 'https://api.twitter.com/2/tweets/search/recent'
                    params = {
                        'query': f'{term} -is:retweet',
                        'max_results': 10,
                        'tweet.fields': 'created_at,public_metrics',
                    }
                    
                    async with session.get(url, headers=headers, params=params) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            tweets = data.get('data', [])
                            
                            # Extract Solana addresses from tweets
                            for tweet in tweets:
                                text = tweet.get('text', '')
                                addresses = self.solana_address_pattern.findall(text)
                                
                                for addr in addresses:
                                    if addr not in found_tokens:
                                        found_tokens[addr] = {
                                            'mentions': 0,
                                            'sentiment': 50,
                                            'source': 'twitter'
                                        }
                                    
                                    found_tokens[addr]['mentions'] += 1
                                    
                                    # Basic sentiment from engagement
                                    metrics = tweet.get('public_metrics', {})
                                    likes = metrics.get('like_count', 0)
                                    retweets = metrics.get('retweet_count', 0)
                                    engagement = likes + retweets * 2
                                    
                                    # Higher engagement = higher sentiment
                                    if engagement > 50:
                                        found_tokens[addr]['sentiment'] = 75
                                    elif engagement > 10:
                                        found_tokens[addr]['sentiment'] = 65
                        else:
                            logger.warning(f"Twitter API returned {resp.status}")
                
        except Exception as e:
            logger.error(f"Twitter scan error: {e}")
        
        logger.info(f"🐦 Found {len(found_tokens)} tokens on Twitter")
        return found_tokens
    
    async def _scan_reddit(self) -> Dict[str, Dict]:
        """
        Scan Reddit for Solana token mentions
        """
        if not self.reddit_id or not self.reddit_secret:
            return {}
        
        logger.info("🔴 Scanning Reddit for Solana tokens...")
        
        found_tokens = {}
        
        try:
            # Get Reddit access token
            async with aiohttp.ClientSession() as session:
                auth = aiohttp.BasicAuth(self.reddit_id, self.reddit_secret)
                data = {
                    'grant_type': 'client_credentials'
                }
                
                async with session.post(
                    'https://www.reddit.com/api/v1/access_token',
                    auth=auth,
                    data=data,
                    headers={'User-Agent': 'EliteTradingBot/1.0'}
                ) as resp:
                    if resp.status == 200:
                        token_data = await resp.json()
                        access_token = token_data.get('access_token')
                        
                        if access_token:
                            # Search Solana-related subreddits
                            headers = {
                                'Authorization': f'Bearer {access_token}',
                                'User-Agent': 'EliteTradingBot/1.0'
                            }
                            
                            subreddits = ['Solana', 'SolanaAlt', 'CryptoMoonShots']
                            
                            for sub in subreddits:
                                url = f'https://oauth.reddit.com/r/{sub}/hot'
                                params = {'limit': 10}
                                
                                async with session.get(url, headers=headers, params=params) as r:
                                    if r.status == 200:
                                        data = await r.json()
                                        posts = data.get('data', {}).get('children', [])
                                        
                                        for post in posts:
                                            post_data = post.get('data', {})
                                            title = post_data.get('title', '')
                                            selftext = post_data.get('selftext', '')
                                            text = f"{title} {selftext}"
                                            
                                            # Extract addresses
                                            addresses = self.solana_address_pattern.findall(text)
                                            
                                            for addr in addresses:
                                                if addr not in found_tokens:
                                                    found_tokens[addr] = {
                                                        'mentions': 0,
                                                        'sentiment': 50,
                                                        'source': 'reddit'
                                                    }
                                                
                                                found_tokens[addr]['mentions'] += 1
                                                
                                                # Sentiment from upvotes
                                                upvotes = post_data.get('ups', 0)
                                                if upvotes > 50:
                                                    found_tokens[addr]['sentiment'] = 70
                                                elif upvotes > 10:
                                                    found_tokens[addr]['sentiment'] = 60
        
        except Exception as e:
            logger.error(f"Reddit scan error: {e}")
        
        logger.info(f"🔴 Found {len(found_tokens)} tokens on Reddit")
        return found_tokens
    
    def _get_cached_trending(self) -> List[Dict]:
        """Return cached trending tokens"""
        return sorted(
            self.trending_cache.values(),
            key=lambda x: x['viral_score'],
            reverse=True
        )

