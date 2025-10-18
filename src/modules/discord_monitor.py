"""
Discord Bot Monitor for Token Mentions
Real-time monitoring of Discord servers for crypto discussions
"""

import asyncio
import logging
from typing import Dict, List, Optional, Set
from datetime import datetime, timedelta
from collections import defaultdict
import discord
from discord.ext import commands

logger = logging.getLogger(__name__)


class TokenDiscordBot(commands.Bot):
    """
    Discord bot that monitors specified channels for token mentions
    """
    
    def __init__(self, token: str, command_prefix: str = "!"):
        intents = discord.Intents.default()
        intents.message_content = True  # Need this to read messages
        intents.guilds = True
        intents.messages = True
        
        super().__init__(command_prefix=command_prefix, intents=intents)
        
        self.bot_token = token
        self.message_buffer: Dict[str, List[Dict]] = defaultdict(list)
        self.tracked_keywords: Set[str] = set()
        self.max_buffer_size = 1000  # Limit buffer size
        self.message_expiry = timedelta(hours=24)  # Keep messages for 24h
        
        # Statistics
        self.total_messages_processed = 0
        self.servers_monitored = 0
        
    async def on_ready(self):
        """Called when bot is ready"""
        logger.info(f"Discord bot logged in as {self.user}")
        logger.info(f"Monitoring {len(self.guilds)} servers")
        self.servers_monitored = len(self.guilds)
        
    async def on_message(self, message: discord.Message):
        """Called when a message is received"""
        # Ignore bot's own messages
        if message.author == self.user:
            return
        
        # Process commands first
        await self.process_commands(message)
        
        # Check message content for tracked keywords
        message_lower = message.content.lower()
        
        for keyword in self.tracked_keywords:
            if keyword.lower() in message_lower:
                # Store message for analysis
                self._buffer_message(keyword, message)
                self.total_messages_processed += 1
                
    def _buffer_message(self, keyword: str, message: discord.Message):
        """Buffer a message for later analysis"""
        message_data = {
            'content': message.content,
            'author': str(message.author),
            'channel_id': message.channel.id,
            'guild_id': message.guild.id if message.guild else None,
            'timestamp': message.created_at,
            'reactions': len(message.reactions),
        }
        
        # Add to buffer
        self.message_buffer[keyword].append(message_data)
        
        # Cleanup old messages and limit size
        self._cleanup_buffer(keyword)
        
    def _cleanup_buffer(self, keyword: str):
        """Remove old messages and limit buffer size"""
        now = datetime.utcnow()
        buffer = self.message_buffer[keyword]
        
        # Remove messages older than expiry time
        buffer = [
            msg for msg in buffer
            if (now - msg['timestamp'].replace(tzinfo=None)) < self.message_expiry
        ]
        
        # Limit buffer size (keep most recent)
        if len(buffer) > self.max_buffer_size:
            buffer = buffer[-self.max_buffer_size:]
        
        self.message_buffer[keyword] = buffer
        
    def track_keyword(self, keyword: str):
        """Add a keyword to track"""
        self.tracked_keywords.add(keyword)
        logger.info(f"Now tracking keyword: {keyword}")
        
    def untrack_keyword(self, keyword: str):
        """Remove a keyword from tracking"""
        self.tracked_keywords.discard(keyword)
        if keyword in self.message_buffer:
            del self.message_buffer[keyword]
        logger.info(f"Stopped tracking keyword: {keyword}")
        
    def get_mentions(self, keyword: str, hours: int = 24) -> List[Dict]:
        """Get recent mentions of a keyword"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        messages = self.message_buffer.get(keyword, [])
        
        # Filter by time
        recent = [
            msg for msg in messages
            if (datetime.utcnow() - msg['timestamp'].replace(tzinfo=None)) < timedelta(hours=hours)
        ]
        
        return recent
    
    async def start_monitoring(self):
        """Start the Discord bot"""
        try:
            await self.start(self.bot_token)
        except Exception as e:
            logger.error(f"Error starting Discord bot: {e}")
            
    async def stop_monitoring(self):
        """Stop the Discord bot"""
        await self.close()
        logger.info("Discord bot stopped")


class DiscordMonitorManager:
    """
    Manager for Discord bot monitoring
    Provides high-level interface for token monitoring
    """
    
    def __init__(self, bot_token: Optional[str] = None):
        self.bot_token = bot_token
        self.bot: Optional[TokenDiscordBot] = None
        self.running = False
        self.bot_task: Optional[asyncio.Task] = None
        
    async def start(self):
        """Start Discord monitoring"""
        if not self.bot_token:
            logger.warning("Discord bot token not configured")
            return False
        
        if self.running:
            logger.warning("Discord bot already running")
            return True
        
        try:
            self.bot = TokenDiscordBot(self.bot_token)
            
            # Start bot in background task
            self.bot_task = asyncio.create_task(self.bot.start_monitoring())
            self.running = True
            
            logger.info("Discord monitoring started")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start Discord monitoring: {e}")
            return False
    
    async def stop(self):
        """Stop Discord monitoring"""
        if not self.running:
            return
        
        try:
            if self.bot:
                await self.bot.stop_monitoring()
            
            if self.bot_task:
                self.bot_task.cancel()
                
            self.running = False
            logger.info("Discord monitoring stopped")
            
        except Exception as e:
            logger.error(f"Error stopping Discord monitoring: {e}")
    
    def track_token(self, token_address: str, keywords: List[str]):
        """Track a token by keywords"""
        if not self.bot or not self.running:
            logger.warning("Discord bot not running")
            return
        
        for keyword in keywords:
            self.bot.track_keyword(keyword)
    
    def get_token_mentions(self, keywords: List[str], hours: int = 24) -> Dict:
        """Get mentions for a token"""
        if not self.bot or not self.running:
            return {
                'mentions': 0,
                'sentiment_score': 50,
                'active_discussions': 0,
                'messages': []
            }
        
        all_messages = []
        for keyword in keywords:
            messages = self.bot.get_mentions(keyword, hours)
            all_messages.extend(messages)
        
        # Remove duplicates
        unique_messages = {msg['content']: msg for msg in all_messages}.values()
        unique_messages = list(unique_messages)
        
        return {
            'mentions': len(unique_messages),
            'messages': unique_messages,
            'active_discussions': len(set(msg['channel_id'] for msg in unique_messages)),
            'servers': len(set(msg['guild_id'] for msg in unique_messages if msg['guild_id']))
        }
    
    def get_stats(self) -> Dict:
        """Get monitoring statistics"""
        if not self.bot or not self.running:
            return {'running': False}
        
        return {
            'running': True,
            'servers_monitored': self.bot.servers_monitored,
            'keywords_tracked': len(self.bot.tracked_keywords),
            'messages_processed': self.bot.total_messages_processed
        }


# Example usage
async def main():
    """Example of using Discord monitor"""
    import os
    
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        print("DISCORD_TOKEN not set")
        return
    
    # Create manager
    manager = DiscordMonitorManager(token)
    
    # Start monitoring
    await manager.start()
    
    # Track a token
    manager.track_token(
        "So11111111111111111111111111111111111111112",
        ["SOL", "Solana", "$SOL"]
    )
    
    # Let it run for a while
    await asyncio.sleep(60)
    
    # Get mentions
    mentions = manager.get_token_mentions(["SOL", "Solana", "$SOL"])
    print(f"Found {mentions['mentions']} mentions")
    
    # Get stats
    stats = manager.get_stats()
    print(f"Stats: {stats}")
    
    # Stop
    await manager.stop()


if __name__ == "__main__":
    asyncio.run(main())

